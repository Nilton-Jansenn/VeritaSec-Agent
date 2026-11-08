"""Adaptador conservador SAST/DAST.

Preserva os dados originais e não altera vereditos LLM.
"""

from __future__ import annotations

from collections import Counter
from copy import deepcopy

from aplicacao.multiagente.correlacao_semantica_http import (
    correlacionar,
)


def normalizar_achado(resultado):
    if not isinstance(resultado, dict):
        raise TypeError("Achado SARIF inválido")

    props = resultado.get("properties") or {}

    if not isinstance(props, dict):
        props = {}

    return {
        "endpoint": (
            props.get("endpoint")
            or props.get("url")
            or props.get("requestUrl")
        ),
        "metodo": (
            props.get("httpMethod")
            or props.get("method")
        ),
        "parametro": (
            props.get("parameter")
            or props.get("param")
        ),
        "cwe": (
            props.get("cwe")
            or resultado.get("ruleId")
        ),
    }


def normalizar_alerta(alerta):
    if not isinstance(alerta, dict):
        raise TypeError("Alerta ZAP inválido")

    return {
        "endpoint": alerta.get("url"),
        "metodo": alerta.get("method"),
        "parametro": alerta.get("param"),
        "cwe": alerta.get("cweid"),
    }


def integrar(sarif, alertas):
    """Integra evidências sem modificar as entradas."""

    if not isinstance(sarif, dict):
        raise TypeError("Documento SARIF inválido")

    if sarif.get("version") != "2.1.0":
        raise ValueError("Versão SARIF não suportada")

    if not isinstance(alertas, list):
        raise TypeError("Alertas devem ser uma lista")

    achados = []

    for run in sarif.get("runs", []):
        if not isinstance(run, dict):
            continue

        for resultado in run.get("results", []):
            achados.append(
                normalizar_achado(resultado)
            )

    alertas_normalizados = [
        normalizar_alerta(alerta)
        for alerta in alertas
    ]

    correlacoes = correlacionar(
        achados,
        alertas_normalizados,
    )

    if len(correlacoes) != len(achados):
        raise RuntimeError(
            "Quantidade de correlações inconsistente"
        )

    contagem = Counter(
        item["classificacao"]
        for item in correlacoes
    )

    return {
        "total_sast": len(achados),
        "total_dast": len(alertas),
        "confirmadas": contagem["CONFIRMADA"],
        "possiveis": contagem["POSSIVEL"],
        "nao_determinadas": contagem["NAO_DETERMINADA"],
        "correlacoes": deepcopy(correlacoes),
        "vereditos_llm_modificados": False,
    }
