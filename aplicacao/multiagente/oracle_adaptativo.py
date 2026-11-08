from __future__ import annotations

from hashlib import sha256
import json
from typing import Any


def _hash_resultado(
    resultado: Any,
) -> str:
    return sha256(
        json.dumps(
            resultado,
            sort_keys=True,
            default=str,
        ).encode()
    ).hexdigest()


def avaliar_resultado(p):
    capacidade = str(
        p.get(
            "capacidade",
            "",
        )
    )

    resultado = p.get(
        "resultado"
    )

    hash_evidencia = _hash_resultado(
        resultado
    )

    if not isinstance(
        resultado,
        dict,
    ):
        return {
            "capacidade": capacidade,
            "observavel": False,
            "violacao": False,
            "hash_evidencia": hash_evidencia,
            "fonte_oracle": None,
        }

    if resultado.get(
        "executada"
    ) is False:
        return {
            "capacidade": capacidade,
            "observavel": False,
            "violacao": False,
            "hash_evidencia": hash_evidencia,
            "fonte_oracle": None,
        }

    evidencia_dinamica = resultado.get(
        "evidencia_dinamica"
    )

    evidencia_oraculo = resultado.get(
        "evidencia_oraculo"
    )

    if (
        evidencia_dinamica
        and evidencia_oraculo
    ):
        return {
            "capacidade": capacidade,
            "observavel": True,
            "violacao": (resultado.get("violacao_confirmada") is True),
            "hash_evidencia": hash_evidencia,
            "fonte_oracle": "evidencia_oraculo",
        }

    oracle_recursivo = resultado.get(
        "oracle"
    )

    if isinstance(
        oracle_recursivo,
        dict,
    ):
        if (
            "violacao_confirmada"
            in oracle_recursivo
        ):
            return {
                "capacidade": capacidade,
                "observavel": True,
                "violacao": (oracle_recursivo.get("violacao_confirmada") is True),
                "hash_evidencia": hash_evidencia,
                "fonte_oracle": "oracle_recursivo",
            }

    if capacidade == "busca_codigo":
        return {
            "capacidade": capacidade,
            "observavel": bool(
                resultado.get(
                    "executada",
                    False,
                )
            ),
            "violacao": False,
            "hash_evidencia": hash_evidencia,
            "fonte_oracle": None,
        }

    return {
        "capacidade": capacidade,
        "observavel": False,
        "violacao": False,
        "hash_evidencia": hash_evidencia,
        "fonte_oracle": None,
    }
