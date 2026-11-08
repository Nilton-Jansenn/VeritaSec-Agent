from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


def agora_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


class PapelAgente(str, Enum):
    ORQUESTRADOR = "orquestrador"
    ANALISTA_CODIGO = "analista_codigo"
    SUPERFICIE_ATAQUE = "superficie_ataque"
    HIPOTESES = "hipoteses"
    PLANEJADOR = "planejador"
    VALIDACAO = "validacao"
    CRITICO = "critico_adversarial"


class EstadoPasso(str, Enum):
    CONCLUIDO = "concluido"
    BLOQUEADO = "bloqueado"
    INCONCLUSIVO = "inconclusivo"
    ERRO = "erro"


class EventoAgente(BaseModel):
    sequencia: int
    agente: PapelAgente
    funcao: str
    decisao: str
    ferramenta: str | None = None
    estado: EstadoPasso = EstadoPasso.CONCLUIDO

    entrada: dict[str, Any] = Field(default_factory=dict)
    saida: dict[str, Any] = Field(default_factory=dict)

    evidencias: list[str] = Field(default_factory=list)

    timestamp: str = Field(default_factory=agora_utc)


class AchadoMultiagente(BaseModel):
    id: str

    regra: str = ""
    cwe: str | None = None
    mensagem: str = ""

    arquivo: str = ""
    linha: int | None = None

    endpoint: str | None = None
    metodo_http: str | None = None

    metadados: dict[str, Any] = Field(default_factory=dict)

    # VERITASSEC_DAST_SETE_AGENTES_V2
    evidencias_dast_correlacionadas: dict[str, Any] = Field(
        default_factory=dict
    )

    # Execução dinâmica somente mediante autorização explícita.
    execucao_dinamica_permitida: bool = False

    # Diretório isolado autorizado para validações locais.
    raiz_sandbox: str | None = None

    # Casos iniciais controlados para busca evolucionária.
    sementes: list[str] = Field(default_factory=list)

    # Orçamento máximo da investigação.
    max_iteracoes: int = Field(default=3, ge=1, le=10)

    # Validação HTTP somente sobre alvo explicitamente fornecido.
    base_url_http: str | None = None

    # Caminho HTTP relativo ao alvo autorizado.
    caminho_http: str | None = None

    # Marcador determinístico esperado no recurso protegido.
    marcador_recurso: str | None = None



class ResultadoMultiagente(BaseModel):
    achado_id: str

    agentes_executados: list[PapelAgente]
    trilha: list[EventoAgente]

    ferramentas_planejadas: list[str] = Field(default_factory=list)
    ferramentas_executadas: list[str] = Field(default_factory=list)

    evidencias: list[str] = Field(default_factory=list)

    hipotese: dict[str, Any] = Field(default_factory=dict)
    lacunas: list[str] = Field(default_factory=list)

    evidencia_dinamica: bool = False
    evidencia_oraculo: bool = False

    estado_final: str
    motivo_termino: str

    iteracoes: int = 1

    inicio: str
    fim: str


class ArquiteturaMultiagente(BaseModel):
    framework: str
    quantidade_agentes: int
    agentes: list[dict[str, str]]
    ferramentas_deterministicas: list[str]
    regra_confirmacao: str


class DecisaoAgenteLLM(BaseModel):
    """
    Saída estruturada de um agente LLM.

    Esta saída nunca confirma vulnerabilidade por si só.
    """
    decisao: str
    observacoes: list[str] = Field(default_factory=list)
    ferramentas_sugeridas: list[str] = Field(default_factory=list)
    sementes_sugeridas: list[str] = Field(default_factory=list, max_length=16)
    requer_evidencia_adicional: bool = True
    confianca: float = Field(default=0.0, ge=0.0, le=1.0)


class RegistroRaciocinioAgente(BaseModel):
    """
    Metadados auditáveis da execução cognitiva.

    Nenhum prompt secreto ou API key é persistido.
    """
    modo: str
    provedor: str | None = None
    modelo: str | None = None
    chamada_modelo_realizada: bool = False
    fallback_deterministico: bool = False
    erro: str | None = None
    decisao: DecisaoAgenteLLM
