"""
Módulo: extrator_exposicoes.py

Objetivo:
---------
Executar uma varredura contextual complementar no arquivo relacionado
ao achado atual, buscando evidências, exposições, red flags e sinais
de insegurança que possam auxiliar a inferência contextual realizada
pela LLM.

IMPORTANTE:
-----------
Este módulo NÃO é um SAST.

Ele apenas coleta evidências observáveis para apoiar a inferência
contextual da LLM.
"""

from __future__ import annotations

import logging
import os
import re
from typing import Any

logger = logging.getLogger(__name__)


TAMANHO_MAXIMO_ARQUIVO = 2 * 1024 * 1024
MAXIMO_EXPOSICOES = 100
MAXIMO_CARACTERES_LINHA = 300


EXTENSOES_ANALISAVEIS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".java",
    ".kt",
    ".go",
    ".php",
    ".rb",
    ".cs",
    ".c",
    ".cpp",
    ".h",
    ".hpp",
    ".swift",
    ".yaml",
    ".yml",
    ".json",
    ".env",
    ".ini",
    ".cfg",
    ".conf",
    ".txt",
    ".properties",
    ".dockerfile",
    ".xml",
    ".sh",
    ".bash",
    ".zsh",
}


PADROES_EXPOSICOES = [
    {
        "tipo": "secret_keyword",
        "descricao": "Possível segredo/credencial hardcoded",
        "regex": r"(password|passwd|secret|token|apikey|api_key|jwt|credential)",
    },
    {
        "tipo": "verify_false",
        "descricao": "Validação TLS desabilitada",
        "regex": r"verify\s*=\s*False",
    },
    {
        "tipo": "debug_true",
        "descricao": "Modo debug habilitado",
        "regex": r"debug\s*=\s*True",
    },
    {
        "tipo": "console_log",
        "descricao": "Console log potencialmente sensível",
        "regex": r"console\.log\s*\(",
    },
    {
        "tipo": "stacktrace",
        "descricao": "Possível exposição de stacktrace",
        "regex": r"(traceback|stacktrace|printStackTrace)",
    },
    {
        "tipo": "md5",
        "descricao": "Uso de MD5",
        "regex": r"\bmd5\b",
    },
    {
        "tipo": "sha1",
        "descricao": "Uso de SHA1",
        "regex": r"\bsha1\b",
    },
    {
        "tipo": "eval",
        "descricao": "Uso de eval",
        "regex": r"\beval\s*\(",
    },
    {
        "tipo": "exec",
        "descricao": "Uso de exec",
        "regex": r"\bexec\s*\(",
    },
    {
        "tipo": "subprocess",
        "descricao": "Execução de subprocesso",
        "regex": r"\bsubprocess\b",
    },
    {
        "tipo": "shell_true",
        "descricao": "shell=True identificado",
        "regex": r"shell\s*=\s*True",
    },
    {
        "tipo": "cors_permissivo",
        "descricao": "CORS potencialmente permissivo",
        "regex": r"Access-Control-Allow-Origin.*\*",
    },
    {
        "tipo": "todo_security",
        "descricao": "TODO/FIXME relacionado à segurança",
        "regex": r"(TODO|FIXME).*(security|auth|token|password|jwt)",
    },
    {
        "tipo": "comentario_inseguro",
        "descricao": "Comentário inseguro",
        "regex": r"(bypass|temporario|hack|nao seguro|unsafe)",
    },
]


def arquivo_eh_analisavel(caminho_arquivo: str) -> bool:
    """
    Verifica se o arquivo possui extensão analisável.

    Retorna:
    --------
    bool
        True quando o arquivo deve ser analisado.
    """

    extensao = os.path.splitext(caminho_arquivo)[1].lower()

    return extensao in EXTENSOES_ANALISAVEIS


def truncar_linha(linha: str) -> str:
    """
    Limita tamanho da linha para evitar explosão contextual.
    """

    linha = linha.strip()

    if len(linha) <= MAXIMO_CARACTERES_LINHA:
        return linha

    return linha[:MAXIMO_CARACTERES_LINHA] + " ... [TRUNCADO]"


def extrair_exposicoes_arquivo(
    caminho_arquivo: str,
) -> list[dict[str, Any]]:
    """
    Executa busca de exposições/red flags em um arquivo específico.

    Importante:
    -----------
    Não classifica vulnerabilidade.
    Apenas coleta sinais observáveis.
    """

    exposicoes: list[dict[str, Any]] = []

    if not caminho_arquivo:
        logger.warning("Caminho de arquivo vazio.")
        return exposicoes

    if not os.path.exists(caminho_arquivo):
        logger.warning("Arquivo não encontrado: %s", caminho_arquivo)
        return exposicoes

    if not arquivo_eh_analisavel(caminho_arquivo):
        logger.info(
            "Arquivo ignorado por extensão não analisável: %s",
            caminho_arquivo,
        )
        return exposicoes

    try:
        tamanho = os.path.getsize(caminho_arquivo)

        if tamanho > TAMANHO_MAXIMO_ARQUIVO:
            logger.warning(
                "Arquivo excede tamanho máximo permitido: %s",
                caminho_arquivo,
            )
            return exposicoes

    except Exception as erro:
        logger.exception(
            "Erro ao verificar tamanho do arquivo: %s",
            erro,
        )
        return exposicoes

    try:
        with open(
            caminho_arquivo,
            "r",
            encoding="utf-8",
            errors="ignore",
        ) as arquivo:
            linhas = arquivo.readlines()

    except Exception as erro:
        logger.exception(
            "Erro ao ler arquivo %s: %s",
            caminho_arquivo,
            erro,
        )
        return exposicoes

    for numero_linha, linha in enumerate(linhas, start=1):
        if len(exposicoes) >= MAXIMO_EXPOSICOES:
            logger.warning("Limite máximo de exposições atingido.")
            break

        linha_limpa = linha.strip()

        if not linha_limpa:
            continue

        for padrao in PADROES_EXPOSICOES:
            try:
                encontrou = re.search(
                    padrao["regex"],
                    linha_limpa,
                    flags=re.IGNORECASE,
                )

            except Exception as erro:
                logger.exception(
                    "Erro regex em padrão %s: %s",
                    padrao["tipo"],
                    erro,
                )
                continue

            if not encontrou:
                continue

            exposicoes.append(
                {
                    "tipo": padrao["tipo"],
                    "descricao": padrao["descricao"],
                    "arquivo": caminho_arquivo,
                    "linha": numero_linha,
                    "trecho": truncar_linha(linha_limpa),
                }
            )

    logger.info(
        "Extraídas %s exposições do arquivo %s",
        len(exposicoes),
        caminho_arquivo,
    )

    return exposicoes


def extrair_exposicoes_codigo(
    caminho_arquivo: str,
) -> list[dict[str, Any]]:
    """
    Função de compatibilidade usada pelo rotas.py.

    Mantém o nome esperado pela aplicação sem alterar a lógica principal
    do extrator.

    Internamente, delega para extrair_exposicoes_arquivo().
    """

    return extrair_exposicoes_arquivo(caminho_arquivo)


def resumir_exposicoes(
    exposicoes: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Gera resumo agregado das exposições encontradas.

    Este resumo serve para o prompt analítico e para rastreabilidade.
    Não confirma vulnerabilidade.
    """

    if not exposicoes:
        return {
            "total": 0,
            "por_tipo": {},
            "tipos_identificados": [],
        }

    por_tipo: dict[str, int] = {}

    for exposicao in exposicoes:
        tipo = str(exposicao.get("tipo") or "exposicao_complementar").strip()

        por_tipo[tipo] = por_tipo.get(tipo, 0) + 1

    return {
        "total": len(exposicoes),
        "por_tipo": por_tipo,
        "tipos_identificados": sorted(por_tipo.keys()),
    }
