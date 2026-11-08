"""Serviço central da investigação."""

from datetime import datetime, timezone

from aplicacao.dominio.enums import (
    EstadoAcao,
    EstadoInvestigacao,
)
from aplicacao.dominio.modelos import (
    AcaoInvestigacao,
    Evidencia,
    Investigacao,
)
from aplicacao.investigacao.evidencias import (
    adicionar_evidencia,
)
from aplicacao.investigacao.politica import (
    DecisaoPolitica,
    PoliticaExecucao,
)


class ServicoInvestigacao:

    def __init__(
        self,
        politica: PoliticaExecucao | None = None,
    ) -> None:
        self.politica = politica or PoliticaExecucao()

    def autorizar_acao(
        self,
        investigacao: Investigacao,
        acao: AcaoInvestigacao,
    ) -> DecisaoPolitica:

        decisao = self.politica.avaliar(
            acao,
            investigacao.escopo,
            investigacao.orcamento,
        )

        acao.estado = (
            EstadoAcao.AUTORIZADA
            if decisao.autorizada
            else EstadoAcao.BLOQUEADA
        )

        return decisao

    def registrar_evidencia(
        self,
        investigacao: Investigacao,
        evidencia: Evidencia,
    ) -> None:

        investigacao.evidencias = adicionar_evidencia(
            investigacao.evidencias,
            evidencia,
        )

        investigacao.estado = (
            EstadoInvestigacao.EVIDENCIA_EM_AQUISICAO
        )

        investigacao.atualizada_em = datetime.now(
            timezone.utc
        )
