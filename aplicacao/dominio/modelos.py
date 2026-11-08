"""Contratos tipados centrais do VeritasSec-Agent."""

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator

from aplicacao.dominio.enums import (
    EstadoAcao,
    EstadoInvestigacao,
    MotivoTerminacao,
    RiscoAcao,
    TipoEvidencia,
    TipoVeredito,
)


def agora_utc() -> datetime:
    return datetime.now(timezone.utc)


class ReferenciaAchado(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    projeto: str
    regra: str
    arquivo: str
    linha: int | None = Field(default=None, ge=1)
    cwe: str | None = None
    mensagem: str
    fingerprint: str | None = None


class HipoteseVulnerabilidade(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    achado_id: str
    tipo: str
    descricao: str
    propriedade_seguranca: str
    precondicoes: list[str] = Field(default_factory=list)
    evidencias_necessarias: list[str] = Field(default_factory=list)
    confianca: float = Field(ge=0.0, le=1.0)
    criada_em: datetime = Field(default_factory=agora_utc)


class Evidencia(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    hipotese_id: str
    tipo: TipoEvidencia
    origem: str
    descricao: str
    observacao: str
    hash_sha256: str | None = None
    reproduzivel: bool = False
    metadados: dict[str, Any] = Field(default_factory=dict)
    coletada_em: datetime = Field(default_factory=agora_utc)


class AcaoInvestigacao(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    ferramenta: str
    objetivo: str
    parametros: dict[str, Any] = Field(default_factory=dict)
    risco: RiscoAcao = RiscoAcao.BAIXO
    estado: EstadoAcao = EstadoAcao.PLANEJADA
    custo_estimado: int = Field(default=1, ge=0)


class OrcamentoInvestigacao(BaseModel):
    max_acoes: int = Field(default=20, ge=1)
    max_tempo_segundos: int = Field(default=600, ge=1)
    max_chamadas_llm: int = Field(default=10, ge=0)
    max_execucoes_dinamicas: int = Field(default=20, ge=0)

    acoes_consumidas: int = Field(default=0, ge=0)
    chamadas_llm_consumidas: int = Field(default=0, ge=0)
    execucoes_dinamicas_consumidas: int = Field(default=0, ge=0)

    def possui_orcamento(self) -> bool:
        return (
            self.acoes_consumidas < self.max_acoes
            and self.chamadas_llm_consumidas
            < self.max_chamadas_llm
            and self.execucoes_dinamicas_consumidas
            < self.max_execucoes_dinamicas
        )


class EscopoAutorizado(BaseModel):
    projeto: str
    caminhos_permitidos: list[str] = Field(default_factory=list)
    ferramentas_permitidas: set[str] = Field(default_factory=set)
    execucao_dinamica_permitida: bool = False
    rede_permitida: bool = False

    @field_validator("projeto")
    @classmethod
    def projeto_nao_vazio(cls, valor: str) -> str:
        valor = valor.strip()

        if not valor:
            raise ValueError("projeto não pode ser vazio")

        return valor


class PlanoInvestigacao(BaseModel):
    hipotese_id: str
    objetivo: str
    acoes: list[AcaoInvestigacao] = Field(default_factory=list)


class Veredito(BaseModel):
    tipo: TipoVeredito
    motivo_terminacao: MotivoTerminacao
    justificativa: str
    evidencia_ids: list[str] = Field(default_factory=list)
    condicoes_testadas: list[str] = Field(default_factory=list)
    condicoes_nao_testadas: list[str] = Field(default_factory=list)
    requer_revisao_humana: bool = False
    emitido_em: datetime = Field(default_factory=agora_utc)


class Investigacao(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    achado: ReferenciaAchado
    hipotese: HipoteseVulnerabilidade | None = None
    estado: EstadoInvestigacao = EstadoInvestigacao.CANDIDATO_ESTATICO
    escopo: EscopoAutorizado
    orcamento: OrcamentoInvestigacao = Field(
        default_factory=OrcamentoInvestigacao
    )
    plano: PlanoInvestigacao | None = None
    evidencias: list[Evidencia] = Field(default_factory=list)
    veredito: Veredito | None = None
    criada_em: datetime = Field(default_factory=agora_utc)
    atualizada_em: datetime = Field(default_factory=agora_utc)


class LacunaEvidencia(BaseModel):
    tipo: str
    descricao: str
    prioridade: int = Field(default=50, ge=0, le=100)
    satisfeita: bool = False


class RegistroProveniencia(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    investigacao_id: str
    acao: str
    componente: str
    entrada_resumida: str | None = None
    saida_resumida: str | None = None
    sucesso: bool
    hash_sha256: str | None = None
    registrado_em: datetime = Field(default_factory=agora_utc)


class ResultadoFerramenta(BaseModel):
    ferramenta: str
    sucesso: bool
    descricao: str
    evidencias: list[Evidencia] = Field(default_factory=list)
    metadados: dict[str, Any] = Field(default_factory=dict)


class EstadoInvestigacaoPersistido(BaseModel):
    investigacao: Investigacao
    lacunas: list[LacunaEvidencia] = Field(default_factory=list)
    proveniencia: list[RegistroProveniencia] = Field(default_factory=list)


class DecisaoInvestigador(BaseModel):
    """Saída estruturada do agente.

    Não representa chain-of-thought. Contém somente decisão
    operacional auditável necessária ao sistema.
    """

    tipo_hipotese: str
    descricao_hipotese: str
    propriedade_seguranca: str
    precondicoes: list[str] = Field(default_factory=list)
    evidencias_necessarias: list[str] = Field(default_factory=list)
    lacunas_prioritarias: list[str] = Field(default_factory=list)
    proxima_ferramenta_sugerida: str | None = None
    justificativa_resumida: str
    confianca: float = Field(ge=0.0, le=1.0)


class DecisaoCritico(BaseModel):
    evidencia_suficiente: bool
    conflitos: list[str] = Field(default_factory=list)
    evidencias_ausentes: list[str] = Field(default_factory=list)
    recomendacao: str
    justificativa_resumida: str


class EstadoLoopAutonomo(BaseModel):
    iteracao: int = Field(default=0, ge=0)
    encerrado: bool = False
    motivo: str | None = None
    ultima_acao: str | None = None
