from __future__ import annotations

from fastapi import APIRouter

from .modelos import AchadoMultiagente
from .orquestrador import OrquestradorMultiagente
from .persistencia import persistir_resultado


roteador_multiagente = APIRouter(
    prefix="/api/v1/multiagente",
    tags=["VeritasSec-Agent Multiagente"],
)


@roteador_multiagente.get(
    "/arquitetura"
)
def arquitetura():

    return (
        OrquestradorMultiagente()
        .arquitetura()
    )


@roteador_multiagente.get(
    "/capacidades"
)
def capacidades():

    motor = OrquestradorMultiagente()

    return motor.executor.capacidades()


@roteador_multiagente.post(
    "/investigar"
)
def investigar(
    achado: AchadoMultiagente,
):

    motor = OrquestradorMultiagente()

    resultado = motor.investigar(
        achado
    )

    persistencia = persistir_resultado(
        resultado
    )

    return {
        "resultado": resultado,
        "persistencia": persistencia,
    }
