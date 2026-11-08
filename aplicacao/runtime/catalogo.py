from __future__ import annotations

import json
import os
from pathlib import Path


def raiz_saidas() -> Path:
    return Path(
        os.getenv(
            "VERITASSEC_SAIDAS_DIR",
            str(
                Path.home()
                / "Documentos"
                / "Projetos"
                / "VeritasSec-Agent-Saidas"
            ),
        )
    ).expanduser().resolve()


def listar_vereditos() -> list[dict]:
    raiz = (
        raiz_saidas()
        / "resultados"
        / "pacotes-veredito"
    )

    if not raiz.exists():
        return []

    itens = []

    for arquivo in sorted(
        raiz.glob("*.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    ):
        try:
            dados = json.loads(
                arquivo.read_text(
                    encoding="utf-8"
                )
            )
        except (
            OSError,
            json.JSONDecodeError,
        ):
            continue

        itens.append(
            {
                "id": arquivo.stem,
                "projeto": dados.get("projeto"),
                "regra": dados.get("regra"),
                "cwe": dados.get("cwe"),
                "estado": dados.get("estado"),
                "estrategia": dados.get(
                    "estrategia"
                ),
                "fingerprint": dados.get(
                    "fingerprint_achado"
                ),
                "evidencia_dinamica": dados.get(
                    "evidencia_dinamica",
                    False,
                ),
                "evidencia_oraculo": dados.get(
                    "evidencia_oraculo",
                    False,
                ),
                "criado_em": dados.get(
                    "criado_em"
                ),
            }
        )

    return itens
