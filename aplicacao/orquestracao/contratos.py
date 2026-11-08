"""Porta de orquestração independente do framework agentic."""

from abc import ABC, abstractmethod

from aplicacao.dominio.modelos import (
    HipoteseVulnerabilidade,
    Investigacao,
    PlanoInvestigacao,
)


class InterfaceOrquestrador(ABC):

    @abstractmethod
    async def formular_hipotese(
        self,
        investigacao: Investigacao,
    ) -> HipoteseVulnerabilidade:
        raise NotImplementedError

    @abstractmethod
    async def planejar(
        self,
        investigacao: Investigacao,
    ) -> PlanoInvestigacao:
        raise NotImplementedError
