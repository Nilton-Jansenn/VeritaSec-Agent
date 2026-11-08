"""Autorização determinística de aquisições ZAP vinculadas ao SARIF."""

from __future__ import annotations

import ipaddress
import json
import os
import subprocess

from pathlib import Path
from urllib.parse import unquote, urlsplit


def campo(obj, nome, padrao=None):
    if isinstance(obj, dict):
        return obj.get(nome, padrao)
    return getattr(obj, nome, padrao)


def caminho_seguro(caminho):
    if not isinstance(caminho, str):
        return False

    if (
        not caminho.startswith("/")
        or caminho.startswith("//")
        or len(caminho) > 2048
        or any(
            c in caminho
            for c in ("?", "#", "\\", "\x00", "\r", "\n")
        )
    ):
        return False

    decodificado = caminho

    # Não aceita caminhos codificados ou sujeitos
    # a interpretação ambígua pelo servidor.
    if "%" in caminho:
        return False

    decodificado = unquote(decodificado)

    if decodificado.startswith("//"):
        return False

    return not any(
        parte in (".", "..")
        for parte in decodificado.split("/")
    )


def procedencia_sarif(achado):
    if achado is None:
        return False

    metadados = campo(achado, "metadados", {})

    if not isinstance(metadados, dict):
        return False

    if metadados.get("origem") != "sarif":
        return False

    if metadados.get("runtime_local_autorizado") is not True:
        return False

    sarif = metadados.get("sarif")
    projeto = metadados.get("projeto")

    if not isinstance(sarif, str):
        return False

    if not isinstance(projeto, str):
        return False

    identificador = campo(achado, "id")

    if (
        not isinstance(identificador, str)
        or not identificador.startswith("sarif:")
    ):
        return False

    try:
        from aplicacao.multiagente.sarif_agent import (
            carregar_achados_sarif,
        )

        arquivo = Path(sarif).expanduser().resolve(
            strict=True
        )

        raiz = Path(projeto).expanduser().resolve(
            strict=True
        )

        if not arquivo.is_file() or not raiz.is_dir():
            return False

        originais = carregar_achados_sarif(
            str(arquivo),
            str(raiz),
        )

        for original in originais:
            if original.get("id") != identificador:
                continue

            for nome in (
                "regra",
                "arquivo",
                "linha",
            ):
                if campo(achado, nome) != original.get(nome):
                    return False

            meta_original = original.get(
                "metadados", {}
            )

            for nome in (
                "sarif",
                "projeto",
                "fingerprint",
                "uri_sarif",
            ):
                if (
                    metadados.get(nome)
                    != meta_original.get(nome)
                ):
                    return False

            return True

    except (
        OSError,
        ValueError,
        TypeError,
        KeyError,
        ImportError,
        RuntimeError,
    ):
        return False

    return False


def autorizado(achado):
    if not procedencia_sarif(achado):
        return False

    # VERITASSEC_VINCULO_EXATO_GET_20261027
    # O executor atual do ZAP utiliza accessUrl (GET).
    # Metodo e caminho precisam estar comprovados
    # no codigo-fonte associado ao achado SARIF.

    from .resolvedor_endpoints import resolver_endpoints

    meta = campo(achado, "metadados", {})

    if not isinstance(meta, dict):
        return False

    registrado = meta.get("resolucao_endpoint")

    if (
        not isinstance(registrado, dict)
        or not registrado.get("resolvido")
    ):
        return False

    atual = resolver_endpoints(
        arquivo=campo(achado, "arquivo"),
        linha=campo(achado, "linha"),
        projeto=meta.get("projeto"),
    )

    if not atual.get("resolvido"):
        return False

    if any(
        str(valor or "").upper() != "GET"
        for valor in (
            campo(achado, "metodo_http"),
            registrado.get("metodo_http"),
            atual.get("metodo_http"),
        )
    ):
        return False

    caminho = campo(achado, "caminho_http")

    if (
        caminho != registrado.get("caminho_http")
        or caminho != atual.get("caminho_http")
    ):
        return False

    if campo(
        achado, "execucao_dinamica_permitida"
    ) is not True:
        return False

    if not caminho_seguro(
        campo(achado, "caminho_http")
    ):
        return False

    if os.getenv("VERITASSEC_RUNTIME_LOCAL") != "true":
        return False

    if os.getenv("VERITASSEC_ZAP_HABILITADO") != "true":
        return False

    if os.getenv(
        "VERITASSEC_ZAP_URL"
    ) != "http://127.0.0.1:8090":
        return False

    if os.getenv(
        "VERITASSEC_RUNTIME_LOCAL_BASE_URL"
    ) != "http://127.0.0.1:3001":
        return False

    if campo(
        achado, "base_url_http"
    ) != "http://127.0.0.1:3001":
        return False

    return True


def alvo_privado():
    texto = os.getenv(
        "VERITASSEC_DAST_ALVO_PRIVADO", ""
    )

    url = urlsplit(texto)

    try:
        ip = ipaddress.ip_address(
            url.hostname or ""
        )
    except ValueError as exc:
        raise PermissionError(
            "ALVO_DOCKER_INVALIDO"
        ) from exc

    if not (
        url.scheme == "http"
        and url.port == 3000
        and url.path == "/"
        and not url.query
        and not url.fragment
        and url.username is None
        and url.password is None
        and ip.version == 4
        and ip.is_private
        and not ip.is_loopback
        and not ip.is_link_local
        and not ip.is_multicast
        and not ip.is_reserved
    ):
        raise PermissionError("ALVO_FORA_ESCOPO")

    processo = subprocess.run(
        [
            "docker",
            "inspect",
            "veritassec-juice-shop-local",
        ],
        capture_output=True,
        text=True,
        timeout=5,
        check=True,
    )

    container = json.loads(
        processo.stdout
    )[0]

    if not container["State"]["Running"]:
        raise PermissionError("RUNTIME_PARADO")

    ips = {
        rede["IPAddress"]
        for rede in container[
            "NetworkSettings"
        ]["Networks"].values()
    }

    if url.hostname not in ips:
        raise PermissionError(
            "IDENTIDADE_RUNTIME_NAO_CONFIRMADA"
        )

    return texto
