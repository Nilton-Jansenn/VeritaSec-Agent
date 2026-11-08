from __future__ import annotations

from dataclasses import dataclass
from .capacidades_canonicas import canonicalizar_capacidade
from typing import Any, Iterable


CAPACIDADES_COGNITIVAS_PERMITIDAS = frozenset({
    "busca_codigo",
    "revisao_codigo_seguro",
    "path_traversal",
    "runtime_http",
    "autorizacao_http",
    "busca_evolucionaria",
    "zap",
    "oraculo_path_traversal",
    "oraculo_autorizacao",
    "proveniencia",
})


@dataclass(frozen=True)
class SolicitacaoCognitiva:
    agente: str
    capacidade: str
    justificativa: str
    sementes: tuple[str, ...] = ()


@dataclass(frozen=True)
class DecisaoPoliticaCognitiva:
    agente: str
    capacidade: str
    autorizada: bool
    motivo: str
    sementes: tuple[str, ...]


def _texto(valor: Any) -> str:
    if valor is None:
        return ""

    return str(valor).strip()


def _lista_strings(
    valor: Any,
    *,
    max_itens: int = 32,
    max_tamanho: int = 512,
) -> tuple[str, ...]:

    if valor is None:
        return ()

    if isinstance(valor, str):
        itens = [valor]

    elif isinstance(
        valor,
        (
            list,
            tuple,
            set,
        ),
    ):
        itens = list(valor)

    else:
        return ()

    saida: list[str] = []

    for item in itens:
        texto = _texto(item)

        if not texto:
            continue

        # Controle de tamanho: decisão da LLM não pode produzir
        # entrada arbitrariamente grande para ferramentas.
        texto = texto[:max_tamanho]

        if texto not in saida:
            saida.append(texto)

        if len(saida) >= max_itens:
            break

    return tuple(saida)


def _campo(
    decisao: Any,
    nome: str,
    default: Any = None,
) -> Any:

    if isinstance(decisao, dict):
        return decisao.get(
            nome,
            default,
        )

    return getattr(
        decisao,
        nome,
        default,
    )


def extrair_solicitacoes_cognitivas(
    *,
    agente: str,
    decisao: Any,
) -> tuple[SolicitacaoCognitiva, ...]:
    """
    Traduz a saída cognitiva em solicitações declarativas.

    Esta função NÃO executa ferramenta alguma.
    """

    ferramentas = (
        _campo(
            decisao,
            "ferramentas_sugeridas",
        )
        or _campo(
            decisao,
            "capacidades_sugeridas",
        )
        or _campo(
            decisao,
            "capacidades",
        )
        or ()
    )

    sementes = (
        _campo(
            decisao,
            "sementes",
        )
        or _campo(
            decisao,
            "seeds",
        )
        or ()
    )

    justificativa = (
        _texto(
            _campo(
                decisao,
                "justificativa",
            )
        )
        or _texto(
            _campo(
                decisao,
                "estrategia",
            )
        )
        or _texto(
            _campo(
                decisao,
                "decisao",
            )
        )
    )

    ferramentas_limpas = _lista_strings(
        ferramentas,
        max_itens=16,
        max_tamanho=128,
    )

    sementes_limpas = _lista_strings(
        sementes,
        max_itens=32,
        max_tamanho=512,
    )

    return tuple(
        SolicitacaoCognitiva(
            agente=agente,
            capacidade=capacidade,
            justificativa=justificativa[
                :1000
            ],
            sementes=sementes_limpas,
        )
        for capacidade
        in ferramentas_limpas
    )


def aplicar_politica_cognitiva(
    solicitacoes: Iterable[
        SolicitacaoCognitiva
    ],
    *,
    capacidades_registradas: Iterable[str],
    capacidades_autorizadas: Iterable[str],
    execucao_dinamica_permitida: bool,
    max_solicitacoes: int = 16,
) -> tuple[
    DecisaoPoliticaCognitiva,
    ...,
]:
    """
    Política determinística.

    A LLM solicita.
    A política decide.

    Nenhuma capacidade inexistente ou não autorizada é
    executável.
    """

    registradas = {
        str(x)
        for x in capacidades_registradas
    }

    autorizadas = {
        str(x)
        for x in capacidades_autorizadas
    }

    saida: list[
        DecisaoPoliticaCognitiva
    ] = []

    dinamicas = {
        "path_traversal",
        "runtime_http",
        "autorizacao_http",
        "busca_evolucionaria",
        "zap",
        "oraculo_path_traversal",
        "oraculo_autorizacao",
    }

    for solicitacao in solicitacoes:
        if len(saida) >= max_solicitacoes:
            break

        # VERITASSEC_ETAPA03_NORMALIZACAO_SEGURA
        # Apenas nomes previamente reconhecidos pelo
        # normalizador podem ser convertidos.
        # A conversao NAO concede autorizacao.
        capacidade_original = solicitacao.capacidade
        capacidade_canonica = canonicalizar_capacidade(
            capacidade_original
        )
        capacidade = (
            capacidade_canonica
            if capacidade_canonica is not None
            else capacidade_original
        )

        if (
            capacidade
            not in
            CAPACIDADES_COGNITIVAS_PERMITIDAS
        ):
            autorizada = False
            motivo = (
                "CAPACIDADE_FORA_DA_ALLOWLIST"
            )

        elif capacidade not in registradas:
            autorizada = False
            motivo = (
                "CAPACIDADE_NAO_REGISTRADA"
            )

        elif capacidade not in autorizadas:
            autorizada = False
            motivo = (
                "CAPACIDADE_NAO_AUTORIZADA"
            )

        elif (
            capacidade in dinamicas
            and not
            execucao_dinamica_permitida
        ):
            autorizada = False
            motivo = (
                "EXECUCAO_DINAMICA_NAO_AUTORIZADA"
            )

        else:
            autorizada = True
            motivo = "AUTORIZADA"

        saida.append(
            DecisaoPoliticaCognitiva(
                agente=solicitacao.agente,
                capacidade=capacidade,
                autorizada=autorizada,
                motivo=motivo,
                sementes=(
                    solicitacao.sementes
                    if autorizada
                    else ()
                ),
            )
        )

    return tuple(saida)
