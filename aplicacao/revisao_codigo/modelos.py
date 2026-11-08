from pydantic import BaseModel, Field


class ObservacaoControle(BaseModel):
    controle: str
    observado: bool
    ocorrencias: list[int] = Field(default_factory=list)
    observacao: str


class ResultadoRevisaoCodigo(BaseModel):
    arquivo: str
    controles: list[ObservacaoControle]
    limitacoes: list[str] = Field(default_factory=list)
