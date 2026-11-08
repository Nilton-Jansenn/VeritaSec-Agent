"""Implementação funcional independente de LLM/framework.

Serve como baseline e fallback determinístico da camada agentic.
"""

from aplicacao.dominio.modelos import (
    HipoteseVulnerabilidade,
    Investigacao,
    PlanoInvestigacao,
)
from aplicacao.investigacao.planejador import PlanejadorAdaptativo


class OrquestradorDeterministico:

    async def formular_hipotese(
        self,
        investigacao: Investigacao,
    ) -> HipoteseVulnerabilidade:

        achado = investigacao.achado

        tipo = (
            achado.cwe
            or achado.regra
            or "vulnerabilidade_desconhecida"
        )

        return HipoteseVulnerabilidade(
            achado_id=achado.id,
            tipo=tipo,
            descricao=(
                "O achado pode representar uma condição "
                "de segurança relevante e requer aquisição "
                "adicional de evidências."
            ),
            propriedade_seguranca=(
                "A entrada controlável não deve alcançar "
                "operação sensível sem controles adequados."
            ),
            precondicoes=[
                "o caminho reportado deve existir",
                "o trecho deve ser alcançável",
            ],
            evidencias_necessarias=[
                "contexto de código",
                "controles de validação",
                "fluxo até operação sensível",
            ],
            confianca=0.5,
        )

    async def planejar(
        self,
        investigacao: Investigacao,
    ) -> PlanoInvestigacao:

        return PlanejadorAdaptativo().planejar(
            investigacao,
            [],
        )
