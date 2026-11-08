"""Regras mínimas e determinísticas de veredito."""

from aplicacao.dominio.enums import (
    MotivoTerminacao,
    TipoEvidencia,
    TipoVeredito,
)
from aplicacao.dominio.modelos import Investigacao, Veredito


def emitir_evidencia_insuficiente(
    investigacao: Investigacao,
    motivo: MotivoTerminacao,
    justificativa: str,
) -> Veredito:

    if motivo in {
        MotivoTerminacao.EVIDENCIA_SUFICIENTE_CONFIRMADA,
        MotivoTerminacao.EVIDENCIA_SUFICIENTE_REFUTADA,
    }:
        raise ValueError(
            "motivo incompatível com evidência insuficiente"
        )

    return Veredito(
        tipo=TipoVeredito.EVIDENCIA_INSUFICIENTE,
        motivo_terminacao=motivo,
        justificativa=justificativa,
        evidencia_ids=[
            evidencia.id
            for evidencia in investigacao.evidencias
        ],
        requer_revisao_humana=True,
    )


def pode_confirmar_explorabilidade(
    investigacao: Investigacao,
) -> bool:

    tipos = {
        evidencia.tipo
        for evidencia in investigacao.evidencias
    }

    return {
        TipoEvidencia.EXECUCAO_DINAMICA,
        TipoEvidencia.ORACULO,
    }.issubset(tipos)


def confirmar_explorabilidade(
    investigacao: Investigacao,
    justificativa: str,
) -> Veredito:

    if not pode_confirmar_explorabilidade(investigacao):
        raise ValueError(
            "explorabilidade exige evidência dinâmica e oráculo"
        )

    return Veredito(
        tipo=TipoVeredito.CONFIRMADO_EXPLORAVEL,
        motivo_terminacao=(
            MotivoTerminacao.EVIDENCIA_SUFICIENTE_CONFIRMADA
        ),
        justificativa=justificativa,
        evidencia_ids=[
            evidencia.id
            for evidencia in investigacao.evidencias
        ],
    )


def refutar_sob_teste(
    investigacao: Investigacao,
    justificativa: str,
    condicoes_testadas: list[str],
    condicoes_nao_testadas: list[str] | None = None,
) -> Veredito:

    if not condicoes_testadas:
        raise ValueError(
            "refutação exige condições efetivamente testadas"
        )

    return Veredito(
        tipo=TipoVeredito.REFUTADO_SOB_TESTE,
        motivo_terminacao=(
            MotivoTerminacao.EVIDENCIA_SUFICIENTE_REFUTADA
        ),
        justificativa=justificativa,
        evidencia_ids=[
            evidencia.id
            for evidencia in investigacao.evidencias
        ],
        condicoes_testadas=condicoes_testadas,
        condicoes_nao_testadas=condicoes_nao_testadas or [],
    )
