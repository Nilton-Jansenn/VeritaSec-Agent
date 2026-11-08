"""
Módulo: normalizador_achados_complementares.py

Responsabilidade:
-----------------
Converter exposições/red flags coletadas pelos extratores complementares
em entidades normalizadas chamadas:

    achados complementares para LLM

Essas entidades são persistíveis, exportáveis e contabilizáveis.

Decisão metodológica:
---------------------
Este módulo NÃO confirma vulnerabilidades.

Ele NÃO:
- define explorabilidade;
- define verdadeiro positivo;
- define falso positivo;
- substitui SAST;
- substitui DAST;
- atribui CWE definitivo;
- atribui severidade final.

Ele apenas transforma evidências observáveis em registros estruturados
para ampliar o universo de inferência contextual da LLM.

Fluxo esperado:
---------------
extrator_exposicoes_projeto.py
    ↓
normalizar_exposicoes_para_achados()
    ↓
persistir_achado_complementar()
    ↓
gerador_graficos.py
    ↓
métricas/artigo

Correção importante:
--------------------
Este módulo expõe obrigatoriamente a função:

    normalizar_exposicoes_para_achados

porque o rotas.py importa exatamente esse nome.

Também aplica deduplicação estrutural por:

    tipo + arquivo + linha + trecho

Isso preserva ocorrências legítimas em arquivos/linhas diferentes, mas impede
persistência duplicada da mesma ocorrência exata.
"""

from __future__ import annotations

import hashlib
import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


TIPO_ORIGEM_PADRAO = "complementar_para_llm"
ORIGEM_PADRAO = "varredura_complementar_projeto"


SEVERIDADE_SUGERIDA_POR_TIPO = {
    "secret_keyword": "baixa",
    "secret_exposto": "alta",
    "token": "alta",
    "password": "alta",
    "api_key": "alta",
    "jwt_hardcoded": "alta",
    "connection_string": "alta",
    "verify_false": "media",
    "debug_true": "media",
    "shell_true": "alta",
    "subprocess": "media",
    "eval": "alta",
    "exec": "alta",
    "cors_permissivo": "media",
    "console_log": "baixa",
    "stacktrace": "media",
    "md5": "media",
    "sha1": "media",
    "todo_security": "baixa",
    "comentario_inseguro": "baixa",
}


def _valor_textual(
    item: dict[str, Any],
    campos: list[str],
    padrao: str = "",
) -> str:
    """
    Obtém o primeiro valor textual disponível em uma lista de campos.

    Motivo:
    -------
    Os extratores podem retornar nomes diferentes para o mesmo conceito.

    Exemplo:
    --------
    arquivo pode chegar como:
    - arquivo
    - caminho
    - caminho_arquivo
    - path
    - uri
    """

    for campo in campos:
        valor = item.get(campo)

        if valor is not None and str(valor).strip():
            return str(valor).strip()

    return padrao


def _valor_inteiro(
    item: dict[str, Any],
    campos: list[str],
) -> int | None:
    """
    Obtém o primeiro valor inteiro disponível em uma lista de campos.

    Retorna None quando não for possível converter.
    """

    for campo in campos:
        valor = item.get(campo)

        if valor is None or valor == "":
            continue

        try:
            return int(valor)
        except (TypeError, ValueError):
            continue

    return None


def _normalizar_tipo(tipo: str | None) -> str:
    """
    Normaliza o tipo da exposição para uso em banco, gráficos e métricas.
    """

    if not tipo:
        return "exposicao_complementar"

    tipo = str(tipo).strip().lower()
    tipo = tipo.replace(" ", "_")
    tipo = tipo.replace("-", "_")
    tipo = tipo.replace("/", "_")
    tipo = tipo.replace(".", "_")

    return tipo or "exposicao_complementar"


def _normalizar_trecho_para_chave(trecho: str | None) -> str:
    """
    Normaliza trecho para deduplicação estrutural.

    Importante:
    -----------
    Esta normalização é usada apenas para comparar duplicidade exata.

    Ela NÃO remove a ocorrência real persistida.
    """

    if not trecho:
        return ""

    return " ".join(str(trecho).strip().lower().split())


def _serializar_estavel(valor: Any) -> str:
    """
    Serializa uma estrutura de forma estável para gerar hash determinístico.

    Isso melhora rastreabilidade e reprodutibilidade.
    """

    try:
        return json.dumps(
            valor,
            ensure_ascii=False,
            sort_keys=True,
            default=str,
        )
    except Exception:
        return str(valor)


def _gerar_identificador_complementar(
    id_execucao: int | None,
    indice: int,
    tipo: str,
    arquivo: str,
    linha: int | None,
    trecho: str,
    evidencia_original: dict[str, Any],
) -> str:
    """
    Gera identificador estável para o achado complementar.

    O identificador não afirma vulnerabilidade. Ele apenas rastreia uma
    evidência complementar normalizada.
    """

    base_hash = {
        "id_execucao": id_execucao,
        "indice": indice,
        "tipo": tipo,
        "arquivo": arquivo,
        "linha": linha,
        "trecho": trecho,
        "evidencia_original": evidencia_original,
    }

    digest = hashlib.sha256(_serializar_estavel(base_hash).encode("utf-8")).hexdigest()[
        :12
    ]

    if id_execucao:
        return f"COMP-{id_execucao}-{indice:05d}-{digest}"

    return f"COMP-SEMEXEC-{indice:05d}-{digest}"


def _severidade_sugerida(tipo: str) -> str | None:
    """
    Sugere severidade operacional para priorização visual.

    Importante:
    -----------
    Esta severidade NÃO é severidade final de vulnerabilidade.

    Ela serve apenas como sinal auxiliar de priorização.
    """

    return SEVERIDADE_SUGERIDA_POR_TIPO.get(tipo)


def _montar_chave_deduplicacao(exposicao: dict[str, Any]) -> tuple[str, str, str, str]:
    """
    Monta chave de deduplicação estrutural.

    Regra:
    ------
    Remove apenas duplicidade exata.

    Preserva corretamente:
    - mesmo tipo em arquivos diferentes;
    - mesmo tipo em linhas diferentes;
    - mesmo tipo no mesmo arquivo com trechos diferentes.

    Deduplica apenas:
    - mesmo tipo;
    - mesmo arquivo;
    - mesma linha;
    - mesmo trecho normalizado.
    """

    tipo = _normalizar_tipo(
        _valor_textual(
            exposicao,
            [
                "tipo",
                "tipo_origem",
                "categoria",
                "classificacao_complementar",
                "regra",
            ],
            "exposicao_complementar",
        )
    )

    arquivo = _valor_textual(
        exposicao,
        [
            "arquivo",
            "caminho",
            "caminho_arquivo",
            "path",
            "uri",
        ],
        "",
    )

    linha = _valor_inteiro(
        exposicao,
        [
            "linha",
            "linha_inicio",
            "linha_inicial",
            "start_line",
        ],
    )

    trecho = _valor_textual(
        exposicao,
        [
            "trecho",
            "codigo",
            "trecho_codigo",
            "linha_codigo",
            "conteudo",
        ],
        "",
    )

    return (
        tipo,
        arquivo.strip(),
        str(linha or ""),
        _normalizar_trecho_para_chave(trecho),
    )


def normalizar_exposicao_para_achado(
    exposicao: dict[str, Any],
    indice: int,
    id_execucao: int | None = None,
    raiz_projeto: str | None = None,
    nome_sistema: str | None = None,
) -> dict[str, Any]:
    """
    Normaliza uma única exposição em achado complementar para LLM.

    Parâmetros:
    -----------
    exposicao:
        Dicionário produzido por extrator_exposicoes.py ou
        extrator_exposicoes_projeto.py.

    indice:
        Índice sequencial usado para rastreabilidade.

    id_execucao:
        ID da execução persistida.

    raiz_projeto:
        Caminho raiz do projeto analisado.

    nome_sistema:
        Nome amigável do sistema analisado.

    Retorno:
    --------
    dict
        Achado complementar pronto para persistência.
    """

    if not isinstance(exposicao, dict):
        exposicao = {"valor_original": str(exposicao)}

    tipo = _normalizar_tipo(
        _valor_textual(
            exposicao,
            [
                "tipo",
                "tipo_origem",
                "categoria",
                "classificacao_complementar",
                "regra",
            ],
            "exposicao_complementar",
        )
    )

    descricao = _valor_textual(
        exposicao,
        [
            "descricao",
            "mensagem",
            "detalhe",
            "regra",
            "titulo",
        ],
        "Exposição complementar identificada para inferência contextual da LLM.",
    )

    arquivo = _valor_textual(
        exposicao,
        [
            "arquivo",
            "caminho",
            "caminho_arquivo",
            "path",
            "uri",
        ],
        "",
    )

    linha = _valor_inteiro(
        exposicao,
        [
            "linha",
            "linha_inicio",
            "linha_inicial",
            "start_line",
        ],
    )

    trecho = _valor_textual(
        exposicao,
        [
            "trecho",
            "codigo",
            "trecho_codigo",
            "linha_codigo",
            "conteudo",
        ],
        "",
    )

    severidade_sugerida = _valor_textual(
        exposicao,
        [
            "severidade_sugerida",
            "severidade",
        ],
        "",
    )

    if not severidade_sugerida:
        severidade_sugerida = _severidade_sugerida(tipo)

    identificador_achado = _gerar_identificador_complementar(
        id_execucao=id_execucao,
        indice=indice,
        tipo=tipo,
        arquivo=arquivo,
        linha=linha,
        trecho=trecho,
        evidencia_original=exposicao,
    )

    return {
        "id_execucao": id_execucao,
        "identificador_achado": identificador_achado,
        "tipo_origem": TIPO_ORIGEM_PADRAO,
        "origem": ORIGEM_PADRAO,
        "nome_sistema": nome_sistema,
        "raiz_projeto": raiz_projeto,
        "tipo": tipo,
        "descricao": descricao,
        "arquivo": arquivo,
        "linha": linha,
        "trecho": trecho,
        "severidade_sugerida": severidade_sugerida,
        "evidencia_original": exposicao,
        "observacao_metodologica": (
            "Este item não representa vulnerabilidade confirmada. "
            "Ele é uma evidência contextual complementar, normalizada como "
            "entidade persistível para ampliar o universo de inferência da LLM."
        ),
    }


def normalizar_exposicoes_para_achados(
    exposicoes: list[dict[str, Any]],
    id_execucao: int | None = None,
    raiz_projeto: str | None = None,
    nome_sistema: str | None = None,
) -> list[dict[str, Any]]:
    """
    Normaliza uma lista de exposições em achados complementares para LLM.

    Esta é a função principal usada pelo rotas.py.

    Deduplicação:
    -------------
    Remove apenas duplicidades exatas com base em:

        tipo + arquivo + linha + trecho

    Isso é importante porque podem existir achados legítimos:
    - iguais em arquivos diferentes;
    - iguais em linhas diferentes;
    - iguais no mesmo arquivo com trechos diferentes.

    O que não pode ocorrer:
    -----------------------
    Persistir a mesma ocorrência exata mais de uma vez.

    Retorno:
    --------
    list[dict]
        Lista de achados complementares prontos para:
        - persistência;
        - exportação;
        - gráficos;
        - métricas.
    """

    if not exposicoes:
        logger.info("Nenhuma exposição complementar recebida para normalização.")
        return []

    achados: list[dict[str, Any]] = []
    vistos: set[tuple[str, str, str, str]] = set()

    total_recebido = len(exposicoes)
    total_duplicados = 0
    total_invalidos = 0

    for exposicao in exposicoes:
        if not isinstance(exposicao, dict):
            total_invalidos += 1
            exposicao = {"valor_original": str(exposicao)}

        chave = _montar_chave_deduplicacao(exposicao)

        if chave in vistos:
            total_duplicados += 1
            continue

        vistos.add(chave)

        try:
            achado = normalizar_exposicao_para_achado(
                exposicao=exposicao,
                indice=len(achados) + 1,
                id_execucao=id_execucao,
                raiz_projeto=raiz_projeto,
                nome_sistema=nome_sistema,
            )

            achados.append(achado)

        except Exception:
            total_invalidos += 1
            logger.exception(
                "Falha ao normalizar exposição complementar. chave=%s",
                chave,
            )

    logger.info(
        (
            "Normalização de complementares concluída. "
            "recebidos=%s unicos=%s duplicados_removidos=%s invalidos=%s"
        ),
        total_recebido,
        len(achados),
        total_duplicados,
        total_invalidos,
    )

    return achados


def normalizar_exposicoes_complementares(
    exposicoes: list[dict[str, Any]],
    id_execucao: int | None = None,
    raiz_projeto: str | None = None,
    nome_sistema: str | None = None,
) -> list[dict[str, Any]]:
    """
    Alias de compatibilidade.

    Mantém compatibilidade caso algum módulo antigo ainda chame:

        normalizar_exposicoes_complementares()

    Internamente delega para:

        normalizar_exposicoes_para_achados()
    """

    return normalizar_exposicoes_para_achados(
        exposicoes=exposicoes,
        id_execucao=id_execucao,
        raiz_projeto=raiz_projeto,
        nome_sistema=nome_sistema,
    )
