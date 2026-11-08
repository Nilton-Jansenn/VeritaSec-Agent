from __future__ import annotations

import re
import unicodedata


CAPACIDADES_CANONICAS = frozenset({
    "busca_codigo",
    "revisao_codigo_seguro",
    "proveniencia",
    "runtime_http",
    "autorizacao_http",
    "path_traversal",
    "busca_evolucionaria",
    "oraculo_path_traversal",
    "oraculo_autorizacao",
})


def normalizar_texto(
    valor: str,
) -> str:

    texto = unicodedata.normalize(
        "NFKD",
        str(valor),
    )

    texto = "".join(
        c
        for c in texto
        if not unicodedata.combining(c)
    )

    texto = texto.lower()

    texto = re.sub(
        r"[^a-z0-9]+",
        " ",
        texto,
    )

    return " ".join(
        texto.split()
    )


ALIASES = {
    "analise codigo estatica":
        "revisao_codigo_seguro",

    "analise de codigo estatica":
        "revisao_codigo_seguro",

    "analise de codigo fonte":
        "revisao_codigo_seguro",

    "analise de codigo fonte detalhada":
        "revisao_codigo_seguro",

    "agente para analise de codigo fonte detalhada":
        "revisao_codigo_seguro",

    "agente de analise de codigo":
        "revisao_codigo_seguro",

    "analisador de codigo fonte":
        "revisao_codigo_seguro",

    "revisao manual de codigo":
        "revisao_codigo_seguro",

    "revisao manual de codigo fonte":
        "revisao_codigo_seguro",

    "revisao de codigo":
        "revisao_codigo_seguro",

    "security code review":
        "revisao_codigo_seguro",

    "analise de fluxo de dados":
        "revisao_codigo_seguro",

    "data flow analysis":
        "revisao_codigo_seguro",

    "analise fluxo dados":
        "revisao_codigo_seguro",

    "analise de componentes de frontend":
        "revisao_codigo_seguro",

    "frontend component analysis":
        "revisao_codigo_seguro",

    "leitor de conteudo de arquivo":
        "busca_codigo",

    "leitura de arquivo":
        "busca_codigo",

    "leitura de codigo":
        "busca_codigo",

    "busca no codigo":
        "busca_codigo",

    "teste http":
        "runtime_http",

    "runtime http":
        "runtime_http",

    "analise dinamica da aplicacao":
        "runtime_http",

    "analise dinamica de aplicacao":
        "runtime_http",

    "analise dinamica dast":
        "runtime_http",

    "dast":
        "runtime_http",

    "analise de comportamento em tempo de execucao":
        "runtime_http",

    "runtime behavior analysis":
        "runtime_http",

    "teste de autorizacao":
        "autorizacao_http",

    "teste de autorizacao http":
        "autorizacao_http",

    "broken access control":
        "autorizacao_http",

    "bola":
        "autorizacao_http",

    "path traversal":
        "path_traversal",

    "directory traversal":
        "path_traversal",

    "travessia de diretorio":
        "path_traversal",

    "proveniencia":
        "proveniencia",

    "analise de proveniencia":
        "proveniencia",
}


def canonicalizar_capacidade(
    capacidade: str,
) -> str | None:

    if not isinstance(
        capacidade,
        str,
    ):
        return None

    original = capacidade.strip()

    if original in CAPACIDADES_CANONICAS:
        return original

    texto = normalizar_texto(
        original
    )

    direta = ALIASES.get(
        texto
    )

    if direta:
        return direta

    if (
        (
            "codigo" in texto
            or "fluxo de dados" in texto
            or "data flow" in texto
        )
        and (
            "analise" in texto
            or "revisao" in texto
            or "rastrear" in texto
        )
    ):
        return "revisao_codigo_seguro"

    if (
        "arquivo" in texto
        and (
            "leitor" in texto
            or "conteudo" in texto
            or "leitura" in texto
        )
    ):
        return "busca_codigo"

    if (
        "path traversal" in texto
        or "directory traversal" in texto
    ):
        return "path_traversal"

    if (
        "autoriz" in texto
        and (
            "http" in texto
            or "acesso" in texto
        )
    ):
        return "autorizacao_http"

    if (
        "dast" in texto
        or (
            "dinamica" in texto
            and (
                "aplicacao" in texto
                or "runtime" in texto
            )
        )
    ):
        return "runtime_http"

    return None


def canonicalizar_lista(
    capacidades,
) -> tuple[str, ...]:

    resultado = []

    for capacidade in capacidades or ():

        canonica = canonicalizar_capacidade(
            capacidade
        )

        if (
            canonica
            and canonica not in resultado
        ):
            resultado.append(
                canonica
            )

    return tuple(
        resultado
    )
