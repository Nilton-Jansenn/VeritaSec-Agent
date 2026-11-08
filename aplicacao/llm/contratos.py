from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Mapping, Protocol


def _mapping_vazio() -> Mapping[str, Any]:
    return {}


@dataclass(frozen=True)
class Evidencia:
    id: str
    conteudo: str
    fonte: str = ""
    metadados: Mapping[str, Any] = field(
        default_factory=_mapping_vazio
    )


@dataclass(frozen=True)
class UsoTokens:
    entrada: int | None = None
    saida: int | None = None
    total: int | None = None


@dataclass(frozen=True)
class SolicitacaoLLM:
    prompt_sistema: str
    prompt_usuario: str
    evidencias: tuple[Evidencia, ...] = ()
    max_tokens_saida: int = 512
    temperatura: float = 0.0
    esquema_resposta: Mapping[str, Any] | None = None
    metadados: Mapping[str, Any] = field(
        default_factory=_mapping_vazio
    )

    @property
    def deterministica(self) -> bool:
        return self.temperatura == 0.0


@dataclass(frozen=True)
class RespostaLLM:
    texto: str
    provedor: str
    modelo: str
    uso: UsoTokens = field(default_factory=UsoTokens)
    metadados: Mapping[str, Any] = field(
        default_factory=_mapping_vazio
    )


class ProvedorLLM(Protocol):
    nome: str
    modelo: str
    escopo: str

    def gerar(
        self,
        solicitacao: SolicitacaoLLM,
    ) -> RespostaLLM:
        ...


CallbackLLM = Callable[
    [SolicitacaoLLM],
    RespostaLLM | str,
]
