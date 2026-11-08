from __future__ import annotations

import re

from pathlib import Path
from typing import Any


MAX_ARQUIVO_CHARS = 120_000
MAX_REFERENCIAS = 40
MAX_ARQUIVOS_BUSCA = 500


def _simbolo_proximo(
    linhas: list[str],
    indice: int,
) -> str | None:

    padrao = re.compile(
        r"""
        (?:
            function\s+
            |
            const\s+
            |
            let\s+
            |
            var\s+
            |
            class\s+
        )
        ([A-Za-z_$][A-Za-z0-9_$]*)
        """,
        re.X,
    )

    inicio = max(
        0,
        indice - 25,
    )

    for pos in range(
        indice,
        inicio - 1,
        -1,
    ):

        match = padrao.search(
            linhas[pos]
        )

        if match:
            return match.group(1)

    return None


def adquirir_contexto_expandido(
    *,
    arquivo: str,
    linha: int | None,
    projeto: str,
) -> dict[str, Any]:

    alvo = Path(
        arquivo
    ).expanduser().resolve()

    raiz = Path(
        projeto
    ).expanduser().resolve()

    try:
        alvo.relative_to(
            raiz
        )
    except ValueError:

        return {
            "executada": False,
            "motivo": "ARQUIVO_FORA_DO_PROJETO",
        }

    if not alvo.is_file():

        return {
            "executada": False,
            "motivo": "ARQUIVO_INEXISTENTE",
        }

    texto = alvo.read_text(
        encoding="utf-8",
        errors="replace",
    )

    linhas = texto.splitlines()

    indice = (
        max(
            0,
            int(linha) - 1,
        )
        if linha
        else 0
    )

    indice = min(
        indice,
        max(
            0,
            len(linhas) - 1,
        ),
    )

    simbolo = _simbolo_proximo(
        linhas,
        indice,
    )

    referencias = []

    if simbolo:

        arquivos_vistos = 0

        for candidato in raiz.rglob(
            "*"
        ):

            if (
                arquivos_vistos
                >= MAX_ARQUIVOS_BUSCA
            ):
                break

            if not candidato.is_file():
                continue

            if candidato.suffix.lower() not in {
                ".ts",
                ".js",
                ".tsx",
                ".jsx",
                ".html",
                ".pug",
            }:
                continue

            arquivos_vistos += 1

            try:
                conteudo = candidato.read_text(
                    encoding="utf-8",
                    errors="replace",
                )
            except OSError:
                continue

            for numero, linha_texto in enumerate(
                conteudo.splitlines(),
                start=1,
            ):

                if simbolo not in linha_texto:
                    continue

                referencias.append({
                    "arquivo":
                        str(candidato),

                    "linha":
                        numero,

                    "trecho":
                        linha_texto[:1000],
                })

                if (
                    len(referencias)
                    >= MAX_REFERENCIAS
                ):
                    break

            if (
                len(referencias)
                >= MAX_REFERENCIAS
            ):
                break

    return {
        "executada": True,
        "arquivo": str(alvo),
        "linha": linha,
        "simbolo_proximo": simbolo,
        "arquivo_completo":
            texto[:MAX_ARQUIVO_CHARS],
        "arquivo_truncado":
            len(texto)
            > MAX_ARQUIVO_CHARS,
        "referencias":
            referencias,
        "referencias_quantidade":
            len(referencias),
    }
