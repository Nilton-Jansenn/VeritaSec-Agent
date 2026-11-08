"""API isolada do núcleo de investigação.

O roteador pode ser incorporado à aplicação principal depois
da validação de regressão da M2.
"""

from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from aplicacao.dominio.modelos import (
    EscopoAutorizado,
    ReferenciaAchado,
)
from aplicacao.investigacao.motor import MotorInvestigacao
from aplicacao.persistencia.investigacoes import (
    RepositorioInvestigacoesJson,
)


router = APIRouter(
    prefix="/api/v1/investigacoes",
    tags=["investigacoes"],
)


class CriarInvestigacaoRequest(BaseModel):
    achado: ReferenciaAchado
    escopo: EscopoAutorizado


def construir_motor(
    raiz_projeto: Path,
    diretorio_estado: Path,
) -> MotorInvestigacao:

    return MotorInvestigacao(
        raiz_projeto=raiz_projeto,
        repositorio=RepositorioInvestigacoesJson(
            diretorio_estado
        ),
    )


@router.get("/health")
def health():
    return {
        "status": "ok",
        "componente": "investigacoes",
    }


@router.get("/{investigacao_id}")
def consultar_investigacao(
    investigacao_id: str,
):
    raise HTTPException(
        status_code=501,
        detail=(
            "repositório de runtime deve ser injetado "
            "pela composição da aplicação"
        ),
    )
