from __future__ import annotations

import hashlib
import re
from pathlib import PurePosixPath

from .modelos import (
    RegistroGroundTruth,
    RegistroSistema,
)


def _normalizar_texto(valor: str | None) -> str:
    if not valor:
        return ""

    return " ".join(
        valor.strip().lower().split()
    )


def _normalizar_arquivo(valor: str) -> str:
    texto = valor.replace("\\", "/").strip()

    try:
        return str(
            PurePosixPath(texto)
        ).lower()
    except Exception:
        return texto.lower()


def _normalizar_cwe(valor: str | None) -> str:
    if not valor:
        return ""

    texto = valor.upper().strip()

    numero = re.search(
        r"CWE[-:\s]*(\d+)",
        texto,
    )

    if numero:
        return "CWE-" + numero.group(1)

    return texto


def material_canonico(
    registro: RegistroGroundTruth
    | RegistroSistema,
) -> str:

    partes = [
        _normalizar_texto(
            registro.projeto
        ),
        _normalizar_arquivo(
            registro.arquivo
        ),
        _normalizar_texto(
            registro.regra
        ),
        str(
            registro.linha
            if registro.linha is not None
            else ""
        ),
        _normalizar_cwe(
            registro.cwe
        ),
        _normalizar_texto(
            registro.trecho
        ),
    ]

    return "\x1f".join(partes)


def chave_achado(
    registro: RegistroGroundTruth
    | RegistroSistema,
) -> str:

    return hashlib.sha256(
        material_canonico(
            registro
        ).encode("utf-8")
    ).hexdigest()
