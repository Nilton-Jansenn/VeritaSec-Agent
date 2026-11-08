from __future__ import annotations

from dataclasses import dataclass

from aplicacao.dominio.enums import TipoEvidencia
from aplicacao.dominio.modelos import Investigacao


@dataclass(frozen=True)
class EstadoCorrelacao:
    possui_estatica: bool
    possui_dinamica: bool
    possui_oraculo: bool
    ids_dinamicos: tuple[str, ...]
    ids_oraculos: tuple[str, ...]


def correlacionar(
    investigacao: Investigacao,
) -> EstadoCorrelacao:

    estaticas = []
    dinamicas = []
    oraculos = []

    for evidencia in investigacao.evidencias:

        if evidencia.tipo in {
            TipoEvidencia.ESTATICA,
            TipoEvidencia.CONTEXTO_CODIGO,
            TipoEvidencia.FLUXO_DADOS,
            TipoEvidencia.REVISAO_CODIGO_SEGURO,
        }:
            estaticas.append(evidencia.id)

        elif (
            evidencia.tipo
            == TipoEvidencia.EXECUCAO_DINAMICA
        ):
            dinamicas.append(evidencia.id)

        elif evidencia.tipo == TipoEvidencia.ORACULO:
            oraculos.append(evidencia.id)

    return EstadoCorrelacao(
        possui_estatica=bool(estaticas),
        possui_dinamica=bool(dinamicas),
        possui_oraculo=bool(oraculos),
        ids_dinamicos=tuple(dinamicas),
        ids_oraculos=tuple(oraculos),
    )
