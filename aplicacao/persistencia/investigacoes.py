"""Persistência JSON atômica para estado de investigação."""

from __future__ import annotations

import os
from pathlib import Path

from aplicacao.dominio.modelos import (
    EstadoInvestigacaoPersistido,
)


class RepositorioInvestigacoesJson:

    def __init__(
        self,
        diretorio: str | Path,
    ) -> None:

        self.diretorio = Path(
            diretorio
        ).resolve()

        self.diretorio.mkdir(
            parents=True,
            exist_ok=True,
        )

    def _arquivo(
        self,
        investigacao_id: str,
    ) -> Path:

        if not investigacao_id:
            raise ValueError(
                "id de investigação vazio"
            )

        seguro = "".join(
            caractere
            for caractere in investigacao_id
            if caractere.isalnum()
            or caractere in "-_"
        )

        if seguro != investigacao_id:
            raise ValueError(
                "id de investigação inválido"
            )

        return self.diretorio / f"{seguro}.json"

    def salvar(
        self,
        estado: EstadoInvestigacaoPersistido,
    ) -> Path:

        destino = self._arquivo(
            estado.investigacao.id
        )

        temporario = destino.with_suffix(
            ".json.tmp"
        )

        conteudo = estado.model_dump_json(
            indent=2,
        )

        temporario.write_text(
            conteudo,
            encoding="utf-8",
        )

        os.replace(
            temporario,
            destino,
        )

        return destino

    def carregar(
        self,
        investigacao_id: str,
    ) -> EstadoInvestigacaoPersistido:

        arquivo = self._arquivo(
            investigacao_id
        )

        if not arquivo.is_file():
            raise FileNotFoundError(arquivo)

        return (
            EstadoInvestigacaoPersistido
            .model_validate_json(
                arquivo.read_text(
                    encoding="utf-8"
                )
            )
        )
