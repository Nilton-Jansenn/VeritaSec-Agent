"""Execução dinâmica controlada via OWASP ZAP.

Não inicia Spider ou Active Scan.
Não modifica configurações do ZAP.
Não executa requisições fora do alvo autorizado.
"""

from __future__ import annotations

import ipaddress
import json
import os
import urllib.parse
import urllib.request
from datetime import datetime, timezone


class ExecucaoDASTInvalida(RuntimeError):
    pass


def validar_alvo(url: str) -> str:
    parsed = urllib.parse.urlsplit(url)

    if (
        parsed.scheme != "http"
        or not parsed.hostname
        or parsed.username
        or parsed.password
        or parsed.query
        or parsed.fragment
        or parsed.path not in ("", "/")
    ):
        raise ExecucaoDASTInvalida("ALVO_INVALIDO")

    try:
        endereco = ipaddress.ip_address(parsed.hostname)
    except ValueError as exc:
        raise ExecucaoDASTInvalida(
            "ALVO_DEVE_UTILIZAR_IP_PRIVADO_EXPLICITO"
        ) from exc

    if not endereco.is_private or endereco.is_loopback:
        raise ExecucaoDASTInvalida(
            "ALVO_FORA_DA_REDE_PRIVADA"
        )

    if parsed.port != 3000:
        raise ExecucaoDASTInvalida(
            "PORTA_DO_RUNTIME_NAO_APROVADA"
        )

    return f"http://{endereco}:3000/"


def validar_zap(url: str) -> str:
    parsed = urllib.parse.urlsplit(url)

    if (
        parsed.scheme != "http"
        or parsed.hostname != "127.0.0.1"
        or parsed.port != 8090
        or parsed.username
        or parsed.password
        or parsed.query
        or parsed.fragment
        or parsed.path not in ("", "/")
    ):
        raise ExecucaoDASTInvalida(
            "ENDERECO_ZAP_NAO_APROVADO"
        )

    return "http://127.0.0.1:8090"


def chamar_api(
    base: str,
    caminho: str,
    parametros: dict,
    chave: str,
) -> dict:
    parametros = dict(parametros)

    parametros["apikey"] = chave

    consulta = urllib.parse.urlencode(parametros)

    url = (
        base.rstrip("/")
        + caminho
        + "?"
        + consulta
    )

    req = urllib.request.Request(
        url,
        headers={"Accept": "application/json"},
    )

    try:
        with urllib.request.urlopen(
            req,
            timeout=20,
        ) as resposta:
            dados = resposta.read(2_000_000)
    except Exception as exc:
        raise ExecucaoDASTInvalida(
            f"FALHA_API_ZAP:{type(exc).__name__}"
        ) from exc

    try:
        resultado = json.loads(dados)
    except (ValueError, UnicodeDecodeError) as exc:
        raise ExecucaoDASTInvalida(
            "RESPOSTA_ZAP_INVALIDA"
        ) from exc

    if not isinstance(resultado, dict):
        raise ExecucaoDASTInvalida(
            "RESPOSTA_ZAP_INESPERADA"
        )

    if "code" in resultado and "message" in resultado:
        raise ExecucaoDASTInvalida(
            "ERRO_API_ZAP:"
            + str(resultado["code"])
        )

    return resultado


def executar(
    *,
    zap_url: str,
    alvo_url: str,
    chave_api: str,
    autorizado: bool,
) -> dict:
    if autorizado is not True:
        raise ExecucaoDASTInvalida(
            "AUTORIZACAO_EXPLICITA_OBRIGATORIA"
        )

    if not chave_api:
        raise ExecucaoDASTInvalida(
            "CHAVE_API_ZAP_AUSENTE"
        )

    base = validar_zap(zap_url)
    alvo = validar_alvo(alvo_url)

    inicio = datetime.now(timezone.utc).isoformat()

    versao = chamar_api(
        base,
        "/JSON/core/view/version/",
        {},
        chave_api,
    )

    # Ação controlada: solicita ao ZAP acessar
    # exclusivamente a URL base autorizada.
    acesso = chamar_api(
        base,
        "/JSON/core/action/accessUrl/",
        {
            "url": alvo,
            "followRedirects": "false",
        },
        chave_api,
    )

    # A consulta não dispara varredura ativa.
    alertas = chamar_api(
        base,
        "/JSON/alert/view/alerts/",
        {
            "baseurl": alvo,
            "start": 0,
            "count": 100,
        },
        chave_api,
    )

    origem = urllib.parse.urlsplit(alvo)

    filtrados = []

    for alerta in alertas.get("alerts", []):
        if not isinstance(alerta, dict):
            continue

        endereco = alerta.get("url", "")
        atual = urllib.parse.urlsplit(endereco)

        if (
            atual.scheme == origem.scheme
            and atual.hostname == origem.hostname
            and atual.port == origem.port
        ):
            filtrados.append(alerta)

    return {
        "inicio_utc": inicio,
        "fim_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "zap_version": versao.get("version"),
        "alvo": alvo,
        "acesso": acesso,
        "acesso_confirmado": (
            (
        isinstance(acesso.get("accessUrl"), list)
        and len(acesso["accessUrl"]) > 0
    )
        ),
        "alertas_origem": len(filtrados),
        "alertas": filtrados,
        "spider_executado": False,
        "active_scan_executado": False,
    }
