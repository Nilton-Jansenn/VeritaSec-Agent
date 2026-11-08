"""Política determinística de autorização."""

from dataclasses import dataclass

from aplicacao.dominio.modelos import (
    AcaoInvestigacao,
    EscopoAutorizado,
    OrcamentoInvestigacao,
)


@dataclass(frozen=True)
class DecisaoPolitica:
    autorizada: bool
    motivo: str


class PoliticaExecucao:
    """O agente nunca define o próprio escopo operacional."""

    def avaliar(
        self,
        acao: AcaoInvestigacao,
        escopo: EscopoAutorizado,
        orcamento: OrcamentoInvestigacao,
    ) -> DecisaoPolitica:

        if not orcamento.possui_orcamento():
            return DecisaoPolitica(
                False,
                "orçamento de investigação esgotado",
            )

        if acao.ferramenta not in escopo.ferramentas_permitidas:
            return DecisaoPolitica(
                False,
                "ferramenta não autorizada pelo escopo",
            )

        if (
            acao.ferramenta == "execucao_dinamica"
            and not escopo.execucao_dinamica_permitida
        ):
            return DecisaoPolitica(
                False,
                "execução dinâmica não autorizada",
            )

        return DecisaoPolitica(
            True,
            "ação autorizada",
        )
