from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class ClasseGroundTruth(StrEnum):
    POSITIVO = "positivo"
    NEGATIVO = "negativo"


class ClasseSistema(StrEnum):
    CONFIRMADO = "confirmado"
    REFUTADO = "refutado"
    EVIDENCIA_INSUFICIENTE = "evidencia_insuficiente"
    ERRO = "erro"
    NAO_AVALIADO = "nao_avaliado"


class RegistroGroundTruth(BaseModel):
    projeto: str = Field(min_length=1)
    arquivo: str = Field(min_length=1)
    regra: str = Field(min_length=1)
    linha: int | None = Field(default=None, ge=1)
    cwe: str | None = None
    trecho: str | None = None
    classe: ClasseGroundTruth


class RegistroSistema(BaseModel):
    projeto: str = Field(min_length=1)
    arquivo: str = Field(min_length=1)
    regra: str = Field(min_length=1)
    linha: int | None = Field(default=None, ge=1)
    cwe: str | None = None
    trecho: str | None = None
    classe: ClasseSistema
    origem: str = Field(min_length=1)


class Pareamento(BaseModel):
    chave: str
    ground_truth: RegistroGroundTruth | None = None
    sistema: RegistroSistema | None = None

    @property
    def pareado(self) -> bool:
        return (
            self.ground_truth is not None
            and self.sistema is not None
        )


class MetricasExperimentais(BaseModel):
    total_ground_truth: int
    total_resultados_sistema: int
    total_pareados: int
    nao_pareados_ground_truth: int
    nao_pareados_sistema: int

    tp: int
    fp: int
    tn: int
    fn: int

    inconclusivos: int
    erros: int
    nao_avaliados: int

    precisao: float | None = None
    revocacao: float | None = None
    especificidade: float | None = None
    f1: float | None = None
