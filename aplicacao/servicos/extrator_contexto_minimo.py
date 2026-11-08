"""
Arquivo: extrator_contexto_minimo.py

Projeto:
--------
VeritasSec

Objetivo:
---------
Reduzir o contexto enviado para a LLM, priorizando trechos com maior
probabilidade de vulnerabilidade.

Problema que este módulo resolve:
---------------------------------
Enviar arquivos inteiros ou contexto expandido demais para a LLM aumenta:
- custo;
- latência;
- ruído;
- chance de resposta genérica;
- chance de falso positivo;
- chance de a LLM focar em código não vulnerável.

Estratégia:
-----------
A partir do achado SARIF/enriquecido, este módulo monta um contexto mínimo com:

1. regra SAST;
2. mensagem do achado;
3. arquivo e linhas;
4. trecho principal;
5. janela pequena ao redor da linha vulnerável;
6. possíveis indicadores de source, sink e sanitização;
7. score heurístico de explorabilidade inicial.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

# ==========================================================
# PADRÕES HEURÍSTICOS
# ==========================================================

PADROES_SOURCE = [
    r"\brequest\b",
    r"\breq\.",
    r"\bparams\b",
    r"\bquery\b",
    r"\bbody\b",
    r"\bheaders\b",
    r"\bcookies\b",
    r"\binput\b",
    r"\buserInput\b",
    r"\bargv\b",
    r"\bgetParameter\b",
    r"\bget_param\b",
    r"\$_GET\b",
    r"\$_POST\b",
    r"\$_REQUEST\b",
]

PADROES_SINK = [
    r"\bexecute\s*\(",
    r"\bquery\s*\(",
    r"\braw\s*\(",
    r"\bfindOne\s*\(",
    r"\bfindAll\s*\(",
    r"\bSELECT\b",
    r"\bINSERT\b",
    r"\bUPDATE\b",
    r"\bDELETE\b",
    r"\beval\s*\(",
    r"\bexec\s*\(",
    r"\bos\.system\s*\(",
    r"\bsubprocess\b",
    r"\bshell\s*=\s*True\b",
    r"\binnerHTML\b",
    r"\bdangerouslySetInnerHTML\b",
    r"\bdocument\.write\b",
    r"\bopen\s*\(",
    r"\bmd5\b",
    r"\bsha1\b",
    r"\bverify\s*=\s*False\b",
]

PADROES_SANITIZACAO = [
    r"\bsanitize\b",
    r"\bescape\b",
    r"\bvalidate\b",
    r"\bvalidator\b",
    r"\bclean\b",
    r"\bencode\b",
    r"\bhtmlspecialchars\b",
    r"\bpreparedStatement\b",
    r"\bPreparedStatement\b",
    r"\bparameterized\b",
    r"\bbind_param\b",
    r"\bbindValue\b",
    r"\bparseInt\b",
    r"\bNumber\s*\(",
    r"\ballowlist\b",
    r"\bwhitelist\b",
]

PADROES_CONTROLE_COMPENSATORIO = [
    r"\bauth\b",
    r"\bauthoriz",
    r"\bpermission\b",
    r"\brole\b",
    r"\bcsrf\b",
    r"\brateLimit\b",
    r"\brate_limit\b",
    r"\blogging\b",
    r"\baudit\b",
]


@dataclass
class EvidenciasContextoMinimo:
    """
    Representa evidências heurísticas extraídas do trecho enviado à LLM.
    """

    entrada_usuario: bool
    sink_critico: bool
    sanitizacao_detectada: bool
    controle_compensatorio: bool
    score_explorabilidade: int
    nivel_explorabilidade: str


def _texto_tem_padrao(texto: str, padroes: list[str]) -> bool:
    """
    Verifica se algum padrão regex aparece no texto.
    """

    texto = texto or ""

    for padrao in padroes:
        if re.search(padrao, texto, flags=re.IGNORECASE):
            return True

    return False


def _limitar_caracteres(texto: str, limite: int) -> str:
    """
    Limita o tamanho do texto enviado para a LLM.
    """

    texto = texto or ""

    if len(texto) <= limite:
        return texto

    return texto[:limite] + "\n\n[CONTEXTO_TRUNCADO_PELO_VERITASSEC_PARA_REDUZIR_RUIDO]"


def _extrair_janela_por_linha(
    contexto_expandido: str,
    linha_alvo: int | None,
    linhas_antes: int,
    linhas_depois: int,
) -> str:
    """
    Extrai uma pequena janela ao redor da linha vulnerável.
    """

    if not contexto_expandido:
        return ""

    if not linha_alvo:
        return contexto_expandido

    linhas = contexto_expandido.splitlines()

    indice_estimado = linha_alvo - 1

    if indice_estimado < 0 or indice_estimado >= len(linhas):
        return contexto_expandido

    inicio = max(0, indice_estimado - linhas_antes)
    fim = min(len(linhas), indice_estimado + linhas_depois + 1)

    return "\n".join(linhas[inicio:fim])


def _calcular_score_explorabilidade(
    entrada_usuario: bool,
    sink_critico: bool,
    sanitizacao_detectada: bool,
    controle_compensatorio: bool,
    trecho_codigo_presente: bool,
    regra_sast_presente: bool,
) -> tuple[int, str]:
    """
    Calcula score heurístico de explorabilidade.
    """

    score = 0

    if entrada_usuario:
        score += 25

    if sink_critico:
        score += 30

    if trecho_codigo_presente:
        score += 15

    if regra_sast_presente:
        score += 10

    if sanitizacao_detectada:
        score -= 25

    if controle_compensatorio:
        score -= 15

    score = max(0, min(100, score))

    if score <= 30:
        nivel = "baixa_evidencia"
    elif score <= 60:
        nivel = "evidencia_moderada"
    elif score <= 85:
        nivel = "forte_evidencia"
    else:
        nivel = "explorabilidade_provavel"

    return score, nivel


def extrair_evidencias_contexto_minimo(
    texto_analise: str,
    regra_sast: str | None = None,
) -> EvidenciasContextoMinimo:
    """
    Extrai evidências heurísticas do contexto mínimo.
    """

    texto_analise = texto_analise or ""

    entrada_usuario = _texto_tem_padrao(texto_analise, PADROES_SOURCE)

    sink_critico = _texto_tem_padrao(texto_analise, PADROES_SINK)

    sanitizacao_detectada = _texto_tem_padrao(
        texto_analise,
        PADROES_SANITIZACAO,
    )

    controle_compensatorio = _texto_tem_padrao(
        texto_analise,
        PADROES_CONTROLE_COMPENSATORIO,
    )

    trecho_codigo_presente = bool(texto_analise.strip())

    regra_sast_presente = bool((regra_sast or "").strip())

    score, nivel = _calcular_score_explorabilidade(
        entrada_usuario=entrada_usuario,
        sink_critico=sink_critico,
        sanitizacao_detectada=sanitizacao_detectada,
        controle_compensatorio=controle_compensatorio,
        trecho_codigo_presente=trecho_codigo_presente,
        regra_sast_presente=regra_sast_presente,
    )

    return EvidenciasContextoMinimo(
        entrada_usuario=entrada_usuario,
        sink_critico=sink_critico,
        sanitizacao_detectada=sanitizacao_detectada,
        controle_compensatorio=controle_compensatorio,
        score_explorabilidade=score,
        nivel_explorabilidade=nivel,
    )


def montar_payload_contexto_minimo(
    achado_enriquecido: Any,
    linhas_antes: int = 5,
    linhas_depois: int = 5,
    limite_caracteres: int = 6000,
) -> dict:
    """
    Monta payload mínimo para envio à LLM.
    """

    identificador_achado = getattr(
        achado_enriquecido,
        "identificador_achado",
        None,
    )

    identificador_regra = getattr(
        achado_enriquecido,
        "identificador_regra",
        None,
    )

    mensagem = getattr(
        achado_enriquecido,
        "mensagem",
        None,
    )

    nivel = getattr(
        achado_enriquecido,
        "nivel",
        None,
    )

    caminho_arquivo = getattr(
        achado_enriquecido,
        "caminho_arquivo",
        None,
    )

    linha_inicial = getattr(
        achado_enriquecido,
        "linha_inicial",
        None,
    )

    linha_final = getattr(
        achado_enriquecido,
        "linha_final",
        None,
    )

    trecho_codigo = (
        getattr(
            achado_enriquecido,
            "trecho_codigo",
            "",
        )
        or ""
    )

    contexto_expandido = (
        getattr(
            achado_enriquecido,
            "contexto_expandido",
            "",
        )
        or ""
    )

    contexto_relacionado = (
        getattr(
            achado_enriquecido,
            "contexto_relacionado",
            "",
        )
        or ""
    )

    arquivos_relacionados = (
        getattr(
            achado_enriquecido,
            "arquivos_relacionados",
            [],
        )
        or []
    )

    janela_codigo = _extrair_janela_por_linha(
        contexto_expandido=contexto_expandido,
        linha_alvo=linha_inicial,
        linhas_antes=linhas_antes,
        linhas_depois=linhas_depois,
    )

    if not janela_codigo.strip():
        janela_codigo = trecho_codigo

    contexto_relacionado_reduzido = _limitar_caracteres(
        contexto_relacionado,
        1200,
    )

    texto_para_evidencias = "\n".join(
        [
            str(mensagem or ""),
            str(identificador_regra or ""),
            janela_codigo,
            contexto_relacionado_reduzido,
        ]
    )

    evidencias = extrair_evidencias_contexto_minimo(
        texto_analise=texto_para_evidencias,
        regra_sast=identificador_regra,
    )

    contexto_minimo = _limitar_caracteres(
        "\n".join(
            [
                "=== TRECHO PRINCIPAL / JANELA DO ACHADO ===",
                janela_codigo,
                "",
                "=== CONTEXTO RELACIONADO REDUZIDO ===",
                contexto_relacionado_reduzido,
            ]
        ),
        limite_caracteres,
    )

    return {
        "identificador_achado": identificador_achado,
        "identificador_regra": identificador_regra,
        "mensagem": mensagem,
        "nivel": nivel,
        "caminho_arquivo": caminho_arquivo,
        "linha_inicial": linha_inicial,
        "linha_final": linha_final,
        # Trecho mínimo principal.
        "trecho_codigo": janela_codigo,
        # Contexto reduzido.
        "contexto_expandido": contexto_minimo,
        "arquivos_relacionados": arquivos_relacionados[:5],
        "contexto_relacionado": contexto_relacionado_reduzido,
        # Metadados extras para métricas e relatório científico.
        "modo_contexto": "minimo_direcionado",
        "linhas_antes": linhas_antes,
        "linhas_depois": linhas_depois,
        "limite_caracteres_contexto": limite_caracteres,
        "evidencias_explorabilidade": {
            "entrada_usuario": evidencias.entrada_usuario,
            "sink_critico": evidencias.sink_critico,
            "sanitizacao_detectada": evidencias.sanitizacao_detectada,
            "controle_compensatorio": (evidencias.controle_compensatorio),
            "score_explorabilidade": (evidencias.score_explorabilidade),
            "nivel_explorabilidade": (evidencias.nivel_explorabilidade),
        },
    }
