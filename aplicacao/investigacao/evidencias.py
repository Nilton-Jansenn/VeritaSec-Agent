"""Registro e integridade de evidências."""

import hashlib
import json
from typing import Any

from aplicacao.dominio.modelos import Evidencia


def hash_evidencia(conteudo: Any) -> str:
    serializado = json.dumps(
        conteudo,
        ensure_ascii=False,
        sort_keys=True,
        default=str,
        separators=(",", ":"),
    ).encode("utf-8")

    return hashlib.sha256(serializado).hexdigest()


def adicionar_evidencia(
    evidencias: list[Evidencia],
    evidencia: Evidencia,
) -> list[Evidencia]:

    if any(item.id == evidencia.id for item in evidencias):
        raise ValueError("evidência duplicada")

    return [*evidencias, evidencia]
