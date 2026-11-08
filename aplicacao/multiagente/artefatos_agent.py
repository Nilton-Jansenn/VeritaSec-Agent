from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def sha256(path: Path) -> str:
    h = hashlib.sha256()

    with path.open("rb") as f:
        for bloco in iter(
            lambda: f.read(65536),
            b"",
        ):
            h.update(bloco)

    return h.hexdigest()


def persistir_resultado_agent(
    resultado: dict[str, Any],
) -> dict[str, Any]:

    raiz = Path(
        os.environ.get(
            "VERITASSEC_SAIDAS_DIR",
            str(
                Path.home()
                / "Documentos"
                / "Projetos"
                / "VeritasSec-Agent-Saidas"
            ),
        )
    )

    ts = datetime.now(
        timezone.utc
    ).strftime("%Y%m%d-%H%M%S-%f")

    out = (
        raiz
        / "resultados"
        / "multiagente"
        / ts
    )

    out.mkdir(
        parents=True,
        exist_ok=False,
    )

    investigacao = out / "investigacao.json"
    trilha = out / "trilha-agentes.jsonl"
    resumo = out / "resumo.json"

    investigacao.write_text(
        json.dumps(
            resultado,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    with trilha.open(
        "w",
        encoding="utf-8",
    ) as f:
        for evento in resultado.get(
            "trilha",
            [],
        ):
            f.write(
                json.dumps(
                    evento,
                    ensure_ascii=False,
                )
                + "\n"
            )

    resumo.write_text(
        json.dumps(
            {
                "achado_id": resultado.get(
                    "achado_id"
                ),
                "estado_final": resultado.get(
                    "estado_final"
                ),
                "motivo_termino": resultado.get(
                    "motivo_termino"
                ),
                "agentes_executados": resultado.get(
                    "agentes_executados"
                ),
                "ferramentas_planejadas": resultado.get(
                    "ferramentas_planejadas"
                ),
                "ferramentas_executadas": resultado.get(
                    "ferramentas_executadas"
                ),
                "evidencia_dinamica": resultado.get(
                    "evidencia_dinamica"
                ),
                "evidencia_oraculo": resultado.get(
                    "evidencia_oraculo"
                ),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    arquivos = [
        investigacao,
        trilha,
        resumo,
    ]

    hashes = {
        p.name: sha256(p)
        for p in arquivos
    }

    sums = out / "SHA256SUMS.txt"

    sums.write_text(
        "".join(
            f"{digest}  {nome}\n"
            for nome, digest
            in hashes.items()
        ),
        encoding="utf-8",
    )

    return {
        "diretorio": str(out),
        "arquivos": [
            str(p)
            for p in arquivos
        ],
        "hashes": hashes,
        "sha256sums": str(sums),
    }
