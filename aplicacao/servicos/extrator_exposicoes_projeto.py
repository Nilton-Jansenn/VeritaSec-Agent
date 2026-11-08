"""
Módulo: extrator_exposicoes_projeto.py

Objetivo:
---------
Executar varredura complementar ampla no projeto inteiro, coletando
exposições, red flags, más práticas e sinais contextuais para apoiar
a inferência da LLM no modo analítico.

Importante:
-----------
Este módulo NÃO é um SAST.

Ele NÃO:
- confirma vulnerabilidade;
- define explorabilidade;
- classifica TP/FP;
- atribui CWE definitivo;
- substitui DAST;
- substitui revisão humana.

Ele apenas coleta evidências observáveis e retorna uma estrutura consolidada.

Compatibilidade:
----------------
Este módulo espera que extrator_exposicoes.py forneça:

    extrair_exposicoes_codigo(caminho_arquivo: str) -> list[dict]

Ou seja: uma lista simples de exposições por arquivo.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from aplicacao.servicos.extrator_exposicoes import extrair_exposicoes_codigo

logger = logging.getLogger(__name__)


# Limites defensivos para evitar explosão contextual.
MAXIMO_ARQUIVOS_ANALISADOS = 300
MAXIMO_EXPOSICOES_PROJETO = 100
TAMANHO_MAXIMO_ARQUIVO_BYTES = 2 * 1024 * 1024


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


def arquivo_pode_ser_analisado(caminho: Path) -> bool:
    """
    Verifica se um arquivo pode ser analisado.

    Regra metodológica:
    -------------------
    Não ignoramos diretórios por padrão.

    O controle ocorre por:
    - existência;
    - tipo arquivo;
    - extensão;
    - tamanho máximo.

    Isso preserva a ideia de Secure Code Review amplo sem permitir explosão
    operacional.
    """

    if not caminho.exists():
        return False

    if not caminho.is_file():
        return False

    extensao = caminho.suffix.lower()

    if extensao not in EXTENSOES_ANALISAVEIS:
        return False

    try:
        tamanho = caminho.stat().st_size
    except OSError:
        return False

    if tamanho > TAMANHO_MAXIMO_ARQUIVO_BYTES:
        return False

    return True


def extrair_exposicoes_projeto(
    raiz_projeto: str,
    maximo_arquivos: int = MAXIMO_ARQUIVOS_ANALISADOS,
    maximo_exposicoes: int = MAXIMO_EXPOSICOES_PROJETO,
) -> dict[str, Any]:
    """
    Executa varredura complementar no projeto inteiro.

    Parâmetros:
    -----------
    raiz_projeto:
        Caminho raiz do projeto analisado.

    maximo_arquivos:
        Quantidade máxima de arquivos analisados.

    maximo_exposicoes:
        Quantidade máxima de exposições retornadas no projeto inteiro.

    Retorno:
    --------
    dict
        Estrutura consolidada com:
        - raiz_projeto;
        - arquivos_analisados;
        - arquivos_com_exposicoes;
        - quantidade_exposicoes;
        - exposicoes;
        - arquivos;
        - limites.
    """

    raiz = Path(raiz_projeto).resolve()

    arquivos_analisados = 0
    arquivos_com_exposicoes: list[dict[str, Any]] = []
    exposicoes_encontradas: list[dict[str, Any]] = []

    if not raiz.exists():
        logger.warning("Raiz do projeto não encontrada: %s", raiz)

        return {
            "raiz_projeto": str(raiz),
            "arquivos_analisados": 0,
            "arquivos_com_exposicoes": 0,
            "quantidade_exposicoes": 0,
            "exposicoes": [],
            "arquivos": [],
            "limites": {
                "maximo_arquivos": maximo_arquivos,
                "maximo_exposicoes": maximo_exposicoes,
                "tamanho_maximo_arquivo_bytes": TAMANHO_MAXIMO_ARQUIVO_BYTES,
            },
            "observacao_metodologica": (
                "Raiz do projeto não encontrada. Nenhuma exposição complementar "
                "foi coletada."
            ),
        }

    if not raiz.is_dir():
        logger.warning("Raiz informada não é diretório: %s", raiz)

        return {
            "raiz_projeto": str(raiz),
            "arquivos_analisados": 0,
            "arquivos_com_exposicoes": 0,
            "quantidade_exposicoes": 0,
            "exposicoes": [],
            "arquivos": [],
            "limites": {
                "maximo_arquivos": maximo_arquivos,
                "maximo_exposicoes": maximo_exposicoes,
                "tamanho_maximo_arquivo_bytes": TAMANHO_MAXIMO_ARQUIVO_BYTES,
            },
            "observacao_metodologica": (
                "Raiz informada não é diretório. Nenhuma exposição complementar "
                "foi coletada."
            ),
        }

    logger.info(
        "Iniciando varredura complementar do projeto. raiz=%s maximo_arquivos=%s maximo_exposicoes=%s",
        raiz,
        maximo_arquivos,
        maximo_exposicoes,
    )

    for caminho in raiz.rglob("*"):
        if arquivos_analisados >= maximo_arquivos:
            logger.warning(
                "Limite de arquivos analisados atingido: %s",
                maximo_arquivos,
            )
            break

        if len(exposicoes_encontradas) >= maximo_exposicoes:
            logger.warning(
                "Limite de exposições do projeto atingido: %s",
                maximo_exposicoes,
            )
            break

        if not arquivo_pode_ser_analisado(caminho):
            continue

        arquivos_analisados += 1

        try:
            exposicoes_arquivo = extrair_exposicoes_codigo(
                caminho_arquivo=str(caminho),
            )

        except Exception as exc:
            logger.warning(
                "Falha ao extrair exposições do arquivo %s: %s",
                caminho,
                exc,
            )
            continue

        if not exposicoes_arquivo:
            continue

        if not isinstance(exposicoes_arquivo, list):
            logger.warning(
                "Extrator retornou formato inesperado para %s: %s",
                caminho,
                type(exposicoes_arquivo),
            )
            continue

        espaco_restante = maximo_exposicoes - len(exposicoes_encontradas)

        exposicoes_limitadas = exposicoes_arquivo[:espaco_restante]

        exposicoes_encontradas.extend(exposicoes_limitadas)

        arquivos_com_exposicoes.append(
            {
                "arquivo": str(caminho),
                "quantidade_exposicoes": len(exposicoes_limitadas),
                "exposicoes": exposicoes_limitadas,
            }
        )

    resultado = {
        "raiz_projeto": str(raiz),
        "arquivos_analisados": arquivos_analisados,
        "arquivos_com_exposicoes": len(arquivos_com_exposicoes),
        "quantidade_exposicoes": len(exposicoes_encontradas),
        "exposicoes": exposicoes_encontradas,
        "arquivos": arquivos_com_exposicoes,
        "limites": {
            "maximo_arquivos": maximo_arquivos,
            "maximo_exposicoes": maximo_exposicoes,
            "tamanho_maximo_arquivo_bytes": TAMANHO_MAXIMO_ARQUIVO_BYTES,
        },
        "observacao_metodologica": (
            "As exposições coletadas não representam vulnerabilidades confirmadas. "
            "Elas são sinais contextuais para ampliar o universo de inferência "
            "da LLM no modo analítico."
        ),
    }

    logger.info(
        "Varredura complementar finalizada. arquivos_analisados=%s arquivos_com_exposicoes=%s exposicoes=%s",
        resultado["arquivos_analisados"],
        resultado["arquivos_com_exposicoes"],
        resultado["quantidade_exposicoes"],
    )

    return resultado
