from __future__ import annotations

from threading import local
from typing import Any, Callable


_contexto = local()

_emissor: (
    Callable[
        [str, dict[str, Any]],
        None,
    ]
    | None
) = None


def registrar_emissor(
    emissor: Callable[
        [str, dict[str, Any]],
        None,
    ]
    | None,
) -> None:

    global _emissor
    _emissor = emissor


def vincular_execucao(
    job_id: str | None,
) -> None:

    _contexto.job_id = job_id



# VERITASSEC_CONTEXTO_ACHADO_20261022
def vincular_achado(
    achado_id: str | None,
) -> None:
    _contexto.achado_id = achado_id


def achado_atual() -> str | None:
    return getattr(
        _contexto,
        "achado_id",
        None,
    )


def job_atual() -> str | None:

    return getattr(
        _contexto,
        "job_id",
        None,
    )


def emitir_progresso_operacional(
    *,
    etapa: str | None = None,
    agente: str | None = None,
    provedor: str | None = None,
    detalhe: str | None = None,
) -> None:

    job_id = job_atual()

    if (
        not job_id
        or _emissor is None
    ):
        return

    dados: dict[str, Any] = {}

    # Identificador interno para filtrar eventos
    # de achados concorrentes.
    identificador = achado_atual()

    if identificador is not None:
        dados["_achado_telemetria"] = identificador


    if etapa is not None:
        dados["etapa_atual"] = str(etapa)

    if agente is not None:
        dados["agente_atual"] = str(agente)

    if provedor is not None:
        dados["provedor_atual"] = str(provedor)

    if detalhe is not None:
        dados["detalhe_atual"] = str(detalhe)

    try:
        _emissor(
            job_id,
            dados,
        )
    except Exception:
        # Telemetria jamais altera a decisão
        # de segurança nem derruba a análise.
        return
