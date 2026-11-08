"""Leitura e busca local com confinamento ao projeto."""

from __future__ import annotations

from pathlib import Path


class ErroEscopoCodigo(ValueError):
    pass


class FerramentaCodigo:

    def __init__(
        self,
        raiz_projeto: str | Path,
    ) -> None:
        self.raiz = Path(
            raiz_projeto
        ).resolve()

    def resolver(
        self,
        caminho: str,
    ) -> Path:

        candidato = (
            self.raiz / caminho
        ).resolve()

        try:
            candidato.relative_to(self.raiz)
        except ValueError as exc:
            raise ErroEscopoCodigo(
                "caminho fora do projeto autorizado"
            ) from exc

        return candidato

    def ler(
        self,
        caminho: str,
        limite_bytes: int = 200_000,
    ) -> str:

        arquivo = self.resolver(caminho)

        if not arquivo.is_file():
            raise FileNotFoundError(arquivo)

        tamanho = arquivo.stat().st_size

        if tamanho > limite_bytes:
            raise ValueError(
                "arquivo excede limite de leitura"
            )

        return arquivo.read_text(
            encoding="utf-8",
            errors="replace",
        )

    def buscar(
        self,
        caminho: str,
        termos: list[str],
    ) -> dict[str, list[int]]:

        conteudo = self.ler(caminho)
        linhas = conteudo.splitlines()

        resultado: dict[str, list[int]] = {}

        for termo in termos:
            ocorrencias = [
                indice
                for indice, linha in enumerate(
                    linhas,
                    start=1,
                )
                if termo.lower() in linha.lower()
            ]

            resultado[termo] = ocorrencias

        return resultado
