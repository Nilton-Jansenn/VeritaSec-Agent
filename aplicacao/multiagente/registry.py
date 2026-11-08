from __future__ import annotations

import os
from dataclasses import dataclass

from agno.agent import Agent

from .modelos import PapelAgente


@dataclass(frozen=True)
class DefinicaoAgente:
    papel: PapelAgente
    nome: str
    funcao: str
    instrucoes: tuple[str, ...]


DEFINICOES = (
    DefinicaoAgente(
        PapelAgente.ORQUESTRADOR,
        "VeritasSec Orquestrador",
        (
            "Controlar investigação, escopo, orçamento, "
            "delegação e término."
        ),
        (
            "Nunca amplie o escopo autorizado.",
            "Não invente evidências.",
            "Delegue aquisição de evidência aos agentes especializados.",
            "Conclusão de agente não confirma vulnerabilidade.",
        ),
    ),

    DefinicaoAgente(
        PapelAgente.ANALISTA_CODIGO,
        "VeritasSec Analista de Código",
        (
            "Analisar contexto estático, origem, sink, "
            "validações e fluxo relevante."
        ),
        (
            "Baseie decisões somente em código ou evidência fornecida.",
            "Diferencie observação de inferência.",
            "Não execute comandos.",
        ),
    ),

    DefinicaoAgente(
        PapelAgente.SUPERFICIE_ATAQUE,
        "VeritasSec Superfície de Ataque",
        (
            "Avaliar alcançabilidade, entrada controlável, "
            "precondições e superfície exposta."
        ),
        (
            "Não presuma alcançabilidade.",
            "Registre precondições ausentes.",
            "Não amplie o alvo.",
        ),
    ),

    DefinicaoAgente(
        PapelAgente.HIPOTESES,
        "VeritasSec Hipóteses",
        (
            "Converter achados em hipóteses causais "
            "testáveis e refutáveis."
        ),
        (
            "Produza hipóteses testáveis.",
            "Identifique evidências necessárias.",
            "Não declare confirmação.",
        ),
    ),

    DefinicaoAgente(
        PapelAgente.PLANEJADOR,
        "VeritasSec Planejador",
        (
            "Escolher a próxima aquisição de evidência "
            "considerando lacunas, custo, risco e orçamento."
        ),
        (
            "Escolha somente ferramentas autorizadas.",
            "Priorize ganho de informação.",
            "Não execute ferramentas diretamente.",
        ),
    ),

    DefinicaoAgente(
        PapelAgente.VALIDACAO,
        "VeritasSec Validação",
        (
            "Coordenar experimentos controlados e interpretar "
            "resultados produzidos por executores determinísticos."
        ),
        (
            "Não execute shell.",
            "Use somente ferramentas registradas.",
            "Não confunda erro ou crash com exploração.",
            "Exija oráculo para confirmação dinâmica.",
        ),
    ),

    DefinicaoAgente(
        PapelAgente.CRITICO,
        "VeritasSec Crítico Adversarial",
        (
            "Tentar refutar hipótese e veredito, procurar "
            "conflitos e exigir suficiência de evidência."
        ),
        (
            "Tente refutar a conclusão proposta.",
            "Evidência negativa não prova ausência universal.",
            "Confirmação exige execução observável e oráculo.",
        ),
    ),
)


class RegistroAgentes:

    def __init__(self) -> None:
        self._agentes: dict[PapelAgente, Agent] = {}

        for definicao in DEFINICOES:
            self._agentes[definicao.papel] = self._criar(
                definicao
            )

    @staticmethod
    def _criar(definicao: DefinicaoAgente) -> Agent:
        kwargs = {
            "id": f"veritassec-{definicao.papel.value}",
            "name": definicao.nome,
            "description": definicao.funcao,
            "instructions": list(definicao.instrucoes),
        }

        # Não hardcodamos OpenAI aqui.
        #
        # A aplicação operacional continuará usando sua camada
        # configurável de provedor. As instâncias Agno representam
        # os agentes reais e seus contratos; a chamada de modelo
        # é mediada pela camada existente.
        return Agent(**kwargs)

    def obter(self, papel: PapelAgente) -> Agent:
        return self._agentes[papel]

    def todos(self) -> dict[PapelAgente, Agent]:
        return dict(self._agentes)

    def quantidade(self) -> int:
        return len(self._agentes)


REGISTRO_AGENTES = RegistroAgentes()
