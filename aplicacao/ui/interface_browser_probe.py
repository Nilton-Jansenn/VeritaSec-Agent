from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from threading import Lock

from fastapi import Query


_ARQUIVO = Path(
    "/tmp/veritassec-browser-probe.log"
)

_LOCK = Lock()


def registrar_browser_probe(
    etapa: str = Query(
        min_length=1,
        max_length=200,
    ),
):
    agora = (
        datetime.now(
            timezone.utc
        )
        .isoformat()
    )

    linha = (
        f"{agora} | {etapa}\n"
    )

    with _LOCK:

        with _ARQUIVO.open(
            "a",
            encoding="utf-8",
        ) as f:

            f.write(
                linha
            )

    return {
        "status":
            "OK",

        "etapa":
            etapa,
    }


def ler_browser_probe():

    if not _ARQUIVO.exists():

        return {
            "linhas":
                [],
        }

    return {
        "linhas":
            _ARQUIVO.read_text(
                encoding="utf-8",
                errors="replace",
            ).splitlines(),
    }


def limpar_browser_probe():

    try:

        _ARQUIVO.unlink()

    except FileNotFoundError:

        pass

    return {
        "status":
            "LIMPO",
    }
