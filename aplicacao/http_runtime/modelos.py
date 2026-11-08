from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import (
    BaseModel,
    Field,
    HttpUrl,
)


class MetodoHttp(StrEnum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"


class AlvoHttpAutorizado(BaseModel):
    base_url: str = Field(min_length=1)

    permitir_loopback: bool = True
    permitir_rede_privada: bool = False
    permitir_rede_publica: bool = False


class CasoHttp(BaseModel):
    metodo: MetodoHttp
    caminho: str = Field(
        min_length=1,
        pattern=r"^/",
    )

    headers: dict[str, str] = Field(
        default_factory=dict
    )

    parametros: dict[str, str] = Field(
        default_factory=dict
    )

    json_body: dict[str, Any] | None = None


class ObservacaoHttp(BaseModel):
    status_code: int = Field(
        ge=100,
        le=599,
    )

    headers: dict[str, str] = Field(
        default_factory=dict
    )

    corpo: str = ""

    duracao_ms: float = Field(ge=0)

    url: str

    identidade: str | None = None


class ResultadoOraculoHttp(BaseModel):
    violado: bool
    propriedade: str
    justificativa: str
    evidencias: dict[str, Any] = Field(
        default_factory=dict
    )
