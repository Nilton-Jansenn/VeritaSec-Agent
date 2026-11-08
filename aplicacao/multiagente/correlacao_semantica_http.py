"""Correlação semântica conservadora entre SAST e DAST.

Não confirma explorabilidade nem altera vereditos LLM.
"""

from __future__ import annotations

import re
from urllib.parse import urlsplit


METODOS = {
    "GET", "POST", "PUT", "PATCH",
    "DELETE", "HEAD", "OPTIONS",
}


def normalizar_metodo(valor):
    if not isinstance(valor, str):
        return None

    valor = valor.strip().upper()

    return valor if valor in METODOS else None


def normalizar_cwe(valor):
    if isinstance(valor, int) and valor > 0:
        return str(valor)

    if not isinstance(valor, str):
        return None

    valor = valor.strip()

    if valor.isdigit():
        return str(int(valor))

    match = re.search(
        r"\bCWE[-_ ]?(\d{1,5})\b",
        valor,
        re.IGNORECASE,
    )

    return str(int(match.group(1))) if match else None


def normalizar_endpoint(valor):
    if not isinstance(valor, str):
        return None

    valor = valor.strip()

    if not valor:
        return None

    try:
        parsed = urlsplit(valor)
    except ValueError:
        return None

    if parsed.scheme:
        if parsed.scheme.lower() not in {"http", "https"}:
            return None

        if not parsed.hostname:
            return None

        caminho = parsed.path or "/"

    elif valor.startswith("/"):
        caminho = parsed.path or "/"

    else:
        return None

    if "\x00" in caminho:
        return None

    return caminho.rstrip("/") or "/"


def normalizar_parametro(valor):
    if not isinstance(valor, str):
        return None

    valor = valor.strip()

    return valor.casefold() if valor else None


def comparar(sast, dast):
    """Compara atributos explícitos e informa evidências."""

    campos = (
        "endpoint",
        "metodo",
        "parametro",
        "cwe",
    )

    normalizadores = {
        "endpoint": normalizar_endpoint,
        "metodo": normalizar_metodo,
        "parametro": normalizar_parametro,
        "cwe": normalizar_cwe,
    }

    iguais = []
    divergentes = []
    ausentes = []

    for campo in campos:
        normalizar = normalizadores[campo]

        a = normalizar(sast.get(campo))
        b = normalizar(dast.get(campo))

        if a is None or b is None:
            ausentes.append(campo)

        elif a == b:
            iguais.append(campo)

        else:
            divergentes.append(campo)

    if divergentes:
        classificacao = "NAO_DETERMINADA"

    elif len(iguais) == 4:
        classificacao = "CONFIRMADA"

    elif (
        "endpoint" in iguais
        and len(iguais) >= 2
    ):
        classificacao = "POSSIVEL"

    else:
        classificacao = "NAO_DETERMINADA"

    return {
        "classificacao": classificacao,
        "atributos_iguais": iguais,
        "atributos_divergentes": divergentes,
        "atributos_ausentes": ausentes,
    }


def correlacionar(achados, alertas):
    """Executa comparação sem alterar entradas."""

    saida = []

    for indice, achado in enumerate(achados):
        correspondencias = []

        for indice_alerta, alerta in enumerate(alertas):
            resultado = comparar(achado, alerta)

            if resultado["classificacao"] != "NAO_DETERMINADA":
                correspondencias.append({
                    "alerta_indice": indice_alerta,
                    **resultado,
                })

        if any(
            item["classificacao"] == "CONFIRMADA"
            for item in correspondencias
        ):
            classificacao = "CONFIRMADA"

        elif correspondencias:
            classificacao = "POSSIVEL"

        else:
            classificacao = "NAO_DETERMINADA"

        saida.append({
            "achado_indice": indice,
            "classificacao": classificacao,
            "correspondencias": correspondencias,
        })

    return saida
