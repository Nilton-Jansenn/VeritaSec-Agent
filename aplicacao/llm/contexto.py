from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from .contratos import Evidencia
from .tokenizacao import (
    EstimadorTokens,
    EstimadorTokensConservador,
)


class ErroOrcamentoContexto(RuntimeError):
    pass


def normalizar_conteudo(texto: str) -> str:
    return "\n".join(
        linha.rstrip()
        for linha in texto
        .replace("\r\n", "\n")
        .replace("\r", "\n")
        .split("\n")
    ).strip()


def hash_evidencia(evidencia: Evidencia) -> str:
    return sha256(
        normalizar_conteudo(
            evidencia.conteudo
        ).encode("utf-8")
    ).hexdigest()


@dataclass(frozen=True)
class ProvenienciaEvidencia:
    id: str
    fonte: str
    sha256: str


@dataclass(frozen=True)
class PacoteContexto:
    incluidas: tuple[Evidencia, ...]
    omitidas_ids: tuple[str, ...]
    duplicadas_ids: tuple[str, ...]
    tokens_estimados: int
    truncado: bool
    proveniencia: tuple[ProvenienciaEvidencia, ...]


@dataclass(frozen=True)
class PoliticaContexto:
    max_tokens_entrada: int = 6000
    max_tokens_por_evidencia: int = 1200
    max_evidencias: int = 4
    overhead_base_tokens: int = 64
    overhead_por_evidencia_tokens: int = 24


class GerenciadorContexto:
    def __init__(
        self,
        politica: PoliticaContexto | None = None,
        estimador: EstimadorTokens | None = None,
    ) -> None:
        self.politica = (
            politica or PoliticaContexto()
        )

        self.estimador = (
            estimador or EstimadorTokensConservador()
        )

    def preparar(
        self,
        prompt_sistema: str,
        prompt_usuario: str,
        evidencias: tuple[Evidencia, ...],
    ) -> PacoteContexto:
        p = self.politica

        total = (
            self.estimador.estimar(prompt_sistema)
            + self.estimador.estimar(prompt_usuario)
            + p.overhead_base_tokens
        )

        if total > p.max_tokens_entrada:
            raise ErroOrcamentoContexto(
                "Prompts base excedem o orcamento"
            )

        incluidas: list[Evidencia] = []
        omitidas: list[str] = []
        duplicadas: list[str] = []
        proveniencia: list[ProvenienciaEvidencia] = []
        vistos: set[str] = set()

        for evidencia in evidencias:
            digest = hash_evidencia(evidencia)

            proveniencia.append(
                ProvenienciaEvidencia(
                    id=evidencia.id,
                    fonte=evidencia.fonte,
                    sha256=digest,
                )
            )

            if digest in vistos:
                duplicadas.append(evidencia.id)
                continue

            vistos.add(digest)

            custo = (
                self.estimador.estimar(
                    evidencia.conteudo
                )
                + p.overhead_por_evidencia_tokens
            )

            if custo > p.max_tokens_por_evidencia:
                omitidas.append(evidencia.id)
                continue

            if len(incluidas) >= p.max_evidencias:
                omitidas.append(evidencia.id)
                continue

            if total + custo > p.max_tokens_entrada:
                omitidas.append(evidencia.id)
                continue

            incluidas.append(evidencia)
            total += custo

        return PacoteContexto(
            incluidas=tuple(incluidas),
            omitidas_ids=tuple(omitidas),
            duplicadas_ids=tuple(duplicadas),
            tokens_estimados=total,
            truncado=bool(omitidas),
            proveniencia=tuple(proveniencia),
        )
