"""Conversão SARIF -> domínio VeritasSec-Agent."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from aplicacao.dominio.modelos import ReferenciaAchado


class ErroSarif(ValueError):
    pass


def _texto_mensagem(resultado: dict[str, Any]) -> str:
    mensagem = resultado.get("message") or {}

    if isinstance(mensagem, dict):
        return str(
            mensagem.get("text")
            or mensagem.get("markdown")
            or ""
        )

    return str(mensagem)


def _localizacao(
    resultado: dict[str, Any],
) -> tuple[str, int | None]:

    localizacoes = resultado.get("locations") or []

    if not localizacoes:
        return "<desconhecido>", None

    fisica = (
        localizacoes[0]
        .get("physicalLocation", {})
    )

    artefato = fisica.get("artifactLocation", {})
    regiao = fisica.get("region", {})

    arquivo = str(
        artefato.get("uri")
        or "<desconhecido>"
    )

    linha = regiao.get("startLine")

    if linha is not None:
        try:
            linha = int(linha)
        except (TypeError, ValueError):
            linha = None

    return arquivo, linha


def _cwe(
    resultado: dict[str, Any],
) -> str | None:

    propriedades = resultado.get("properties") or {}

    candidatos = [
        propriedades.get("cwe"),
        propriedades.get("CWE"),
    ]

    tags = propriedades.get("tags") or []

    if isinstance(tags, list):
        candidatos.extend(tags)

    for candidato in candidatos:
        if candidato is None:
            continue

        texto = str(candidato)

        if "CWE-" in texto.upper():
            indice = texto.upper().find("CWE-")
            resto = texto[indice:]

            numero = ""

            for caractere in resto[4:]:
                if caractere.isdigit():
                    numero += caractere
                else:
                    break

            if numero:
                return f"CWE-{numero}"

    return None


def _fingerprint(
    projeto: str,
    regra: str,
    arquivo: str,
    linha: int | None,
    mensagem: str,
) -> str:

    canonico = "|".join([
        projeto.strip(),
        regra.strip(),
        arquivo.strip(),
        str(linha or ""),
        " ".join(mensagem.split()),
    ])

    return hashlib.sha256(
        canonico.encode("utf-8")
    ).hexdigest()


def converter_resultado(
    resultado: dict[str, Any],
    projeto: str,
) -> ReferenciaAchado:

    regra = str(
        resultado.get("ruleId")
        or resultado.get("rule", {}).get("id")
        or "regra-desconhecida"
    )

    arquivo, linha = _localizacao(resultado)
    mensagem = _texto_mensagem(resultado)

    fingerprints = resultado.get(
        "partialFingerprints"
    ) or {}

    fingerprint = None

    if isinstance(fingerprints, dict):
        for valor in fingerprints.values():
            if valor:
                fingerprint = str(valor)
                break

    if not fingerprint:
        fingerprint = _fingerprint(
            projeto,
            regra,
            arquivo,
            linha,
            mensagem,
        )

    return ReferenciaAchado(
        projeto=projeto,
        regra=regra,
        arquivo=arquivo,
        linha=linha,
        cwe=_cwe(resultado),
        mensagem=mensagem,
        fingerprint=fingerprint,
    )


def carregar_sarif(
    caminho: str | Path,
    projeto: str,
) -> list[ReferenciaAchado]:

    path = Path(caminho)

    if not path.is_file():
        raise ErroSarif(
            f"arquivo SARIF inexistente: {path}"
        )

    try:
        documento = json.loads(
            path.read_text(encoding="utf-8")
        )
    except (OSError, json.JSONDecodeError) as exc:
        raise ErroSarif(
            f"SARIF inválido: {exc}"
        ) from exc

    if not isinstance(documento, dict):
        raise ErroSarif(
            "raiz SARIF deve ser objeto JSON"
        )

    runs = documento.get("runs")

    if not isinstance(runs, list):
        raise ErroSarif(
            "campo runs ausente ou inválido"
        )

    achados: list[ReferenciaAchado] = []

    for run in runs:
        if not isinstance(run, dict):
            continue

        resultados = run.get("results") or []

        if not isinstance(resultados, list):
            continue

        for resultado in resultados:
            if not isinstance(resultado, dict):
                continue

            achados.append(
                converter_resultado(
                    resultado,
                    projeto,
                )
            )

    return achados
