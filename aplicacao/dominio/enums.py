"""Enumerações centrais do domínio de investigação."""

from enum import Enum


class EstadoInvestigacao(str, Enum):
    CANDIDATO_ESTATICO = "candidato_estatico"
    HIPOTESE_FORMULADA = "hipotese_formulada"
    EVIDENCIA_EM_AQUISICAO = "evidencia_em_aquisicao"
    EVIDENCIA_SUFICIENTE = "evidencia_suficiente"
    EVIDENCIA_INSUFICIENTE = "evidencia_insuficiente"
    FINALIZADA = "finalizada"


class TipoVeredito(str, Enum):
    CONFIRMADO_EXPLORAVEL = "confirmado_exploravel"
    REFUTADO_SOB_TESTE = "refutado_sob_teste"
    EVIDENCIA_INSUFICIENTE = "evidencia_insuficiente"


class MotivoTerminacao(str, Enum):
    EVIDENCIA_SUFICIENTE_CONFIRMADA = (
        "evidencia_suficiente_confirmada"
    )
    EVIDENCIA_SUFICIENTE_REFUTADA = (
        "evidencia_suficiente_refutada"
    )
    ORCAMENTO_ESGOTADO = "orcamento_esgotado"
    TEMPO_ESGOTADO = "tempo_esgotado"
    FERRAMENTA_INDISPONIVEL = "ferramenta_indisponivel"
    ACAO_NAO_AUTORIZADA = "acao_nao_autorizada"
    CONFLITO_NAO_RESOLVIDO = "conflito_nao_resolvido"
    ALVO_INDISPONIVEL = "alvo_indisponivel"
    ERRO_DE_EXECUCAO = "erro_de_execucao"
    ESCALONADO_PARA_HUMANO = "escalonado_para_humano"


class TipoEvidencia(str, Enum):
    ESTATICA = "estatica"
    CONTEXTO_CODIGO = "contexto_codigo"
    FLUXO_DADOS = "fluxo_dados"
    REVISAO_CODIGO_SEGURO = "revisao_codigo_seguro"
    EXECUCAO_DINAMICA = "execucao_dinamica"
    ORACULO = "oraculo"
    DOCUMENTACAO = "documentacao"


class EstadoAcao(str, Enum):
    PLANEJADA = "planejada"
    AUTORIZADA = "autorizada"
    EXECUTADA = "executada"
    BLOQUEADA = "bloqueada"
    FALHOU = "falhou"


class RiscoAcao(str, Enum):
    BAIXO = "baixo"
    MEDIO = "medio"
    ALTO = "alto"


class TipoFerramenta(str, Enum):
    SARIF = "sarif"
    BUSCA_CODIGO = "busca_codigo"
    REVISAO_CODIGO_SEGURO = "revisao_codigo_seguro"
    EXECUCAO_DINAMICA = "execucao_dinamica"
    DOCUMENTACAO = "documentacao"


class EstadoFerramenta(str, Enum):
    DISPONIVEL = "disponivel"
    INDISPONIVEL = "indisponivel"


class TipoLacunaEvidencia(str, Enum):
    CONTEXTO_CODIGO = "contexto_codigo"
    VALIDACAO_ENTRADA = "validacao_entrada"
    AUTORIZACAO = "autorizacao"
    FLUXO_DADOS = "fluxo_dados"
    EXECUCAO_DINAMICA = "execucao_dinamica"
    ORACULO = "oraculo"
