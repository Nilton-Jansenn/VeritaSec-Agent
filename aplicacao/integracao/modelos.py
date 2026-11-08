from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from aplicacao.dominio.modelos import (
    EstadoInvestigacaoPersistido,
)


class TipoValidacaoM6(StrEnum):
    ESTATICA = "estatica"
    PATH_TRAVERSAL = "path_traversal"
    AUTORIZACAO_HTTP = "autorizacao_http"


class EstadoEtapaM6(StrEnum):
    EXECUTADA = "executada"
    BLOQUEADA = "bloqueada"
    NAO_APLICAVEL = "nao_aplicavel"
    FALHOU = "falhou"


class RegistroEtapaM6(BaseModel):
    etapa: str
    estado: EstadoEtapaM6
    componente: str
    resumo: str
    metadados: dict[str, Any] = Field(
        default_factory=dict
    )


class ResultadoPipelineM6(BaseModel):
    investigacao: EstadoInvestigacaoPersistido
    etapas: list[RegistroEtapaM6] = Field(
        default_factory=list
    )

    evidencia_dinamica: bool = False
    evidencia_oraculo: bool = False

    propriedade_violada: bool = False
    confirmacao_permitida: bool = False

    validacoes_executadas: list[
        TipoValidacaoM6
    ] = Field(default_factory=list)

    observacoes: list[str] = Field(
        default_factory=list
    )
