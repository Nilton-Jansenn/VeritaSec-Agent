"""Adaptador Agno isolado do domínio VeritasSec.

Nenhum componente de domínio depende diretamente de Agno.
A resposta do modelo é aceita somente se validada pelo
schema Pydantic DecisaoInvestigador.
"""

from __future__ import annotations

import os
from typing import Any, Callable

from agno.agent import Agent
from agno.models.openai import OpenAIResponses

from aplicacao.dominio.modelos import (
    DecisaoInvestigador,
    HipoteseVulnerabilidade,
    Investigacao,
    PlanoInvestigacao,
)
from aplicacao.investigacao.lacunas import identificar_lacunas
from aplicacao.investigacao.planejador import PlanejadorAdaptativo


class ErroSaidaAgente(RuntimeError):
    pass


class AdaptadorAgnoInvestigador:

    def __init__(
        self,
        runner: Callable[[str], Any] | None = None,
        model_id: str | None = None,
    ) -> None:

        self.model_id = (
            model_id
            or os.getenv(
                "VERITASSEC_AGNO_MODEL",
                "gpt-5.6",
            )
        )

        self._runner = runner
        self._agent: Agent | None = None

    def _construir_agent(self) -> Agent:
        if self._agent is None:
            self._agent = Agent(
                id="veritassec-investigador",
                name="VeritasSec Investigador",
                model=OpenAIResponses(
                    id=self.model_id
                ),
                description=(
                    "Analise achados de segurança como "
                    "hipóteses que precisam de evidências. "
                    "Não declare vulnerabilidade confirmada "
                    "sem evidência dinâmica e oráculo."
                ),
                instructions=[
                    (
                        "Produza somente decisão estruturada "
                        "conforme o schema."
                    ),
                    (
                        "Não execute comandos, não amplie "
                        "escopo e não invente evidências."
                    ),
                    (
                        "Indique explicitamente evidências "
                        "ausentes e próxima ferramenta."
                    ),
                ],
                output_schema=DecisaoInvestigador,
            )

        return self._agent

    def _prompt(
        self,
        investigacao: Investigacao,
    ) -> str:

        achado = investigacao.achado

        return (
            "Analise o achado abaixo como hipótese de "
            "vulnerabilidade.\n"
            f"Regra: {achado.regra}\n"
            f"CWE: {achado.cwe or 'não informado'}\n"
            f"Arquivo: {achado.arquivo}\n"
            f"Linha: {achado.linha or 'não informada'}\n"
            f"Mensagem: {achado.mensagem}\n"
            "Determine propriedade de segurança, "
            "precondições e evidências necessárias."
        )

    async def _executar(
        self,
        prompt: str,
    ) -> DecisaoInvestigador:

        if self._runner is not None:
            resultado = self._runner(prompt)

            if hasattr(resultado, "__await__"):
                resultado = await resultado

            if isinstance(
                resultado,
                DecisaoInvestigador,
            ):
                return resultado

            if isinstance(resultado, dict):
                return DecisaoInvestigador.model_validate(
                    resultado
                )

            raise ErroSaidaAgente(
                "runner não retornou saída estruturada"
            )

        agente = self._construir_agent()

        resposta = await agente.arun(prompt)

        conteudo = resposta.content

        if not isinstance(
            conteudo,
            DecisaoInvestigador,
        ):
            raise ErroSaidaAgente(
                "Agno não retornou DecisaoInvestigador "
                "validada"
            )

        return conteudo

    async def formular_hipotese(
        self,
        investigacao: Investigacao,
    ) -> HipoteseVulnerabilidade:

        decisao = await self._executar(
            self._prompt(investigacao)
        )

        return HipoteseVulnerabilidade(
            achado_id=investigacao.achado.id,
            tipo=decisao.tipo_hipotese,
            descricao=decisao.descricao_hipotese,
            propriedade_seguranca=(
                decisao.propriedade_seguranca
            ),
            precondicoes=decisao.precondicoes,
            evidencias_necessarias=(
                decisao.evidencias_necessarias
            ),
            confianca=decisao.confianca,
        )

    async def planejar(
        self,
        investigacao: Investigacao,
    ) -> PlanoInvestigacao:

        lacunas = identificar_lacunas(
            investigacao
        )

        return PlanejadorAdaptativo().planejar(
            investigacao,
            lacunas,
        )
