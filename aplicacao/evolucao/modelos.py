from __future__ import annotations

from pydantic import BaseModel, Field


class CasoDeTeste(BaseModel):
    valor: str
    geracao: int = Field(ge=0)
    origem: str
    aptidao: float = 0.0


class ConfiguracaoEvolutiva(BaseModel):
    max_geracoes: int = Field(
        default=5,
        ge=1,
        le=100,
    )

    tamanho_populacao: int = Field(
        default=12,
        ge=2,
        le=1000,
    )

    semente_aleatoria: int = 2026

    parar_ao_confirmar: bool = True


class ResultadoEvolutivo(BaseModel):
    confirmado: bool
    geracoes_executadas: int
    execucoes: int
    melhor: CasoDeTeste
    historico_melhor_aptidao: list[float]
