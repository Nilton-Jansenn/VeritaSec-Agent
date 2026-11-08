from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

from .modelos import ResultadoMultiagente


def raiz_resultados() -> Path:
    base = os.getenv(
        "VERITASSEC_SAIDAS_DIR",
        str(
            Path.home()
            / "Documentos"
            / "Projetos"
            / "VeritasSec-Agent-Saidas"
        ),
    )

    raiz = (
        Path(base)
        / "resultados"
        / "multiagente"
    )

    raiz.mkdir(
        parents=True,
        exist_ok=True,
    )

    return raiz


def persistir_resultado(
    resultado: ResultadoMultiagente,
) -> dict[str, str]:

    conteudo = resultado.model_dump_json(
        indent=2,
    )

    digest = hashlib.sha256(
        conteudo.encode("utf-8")
    ).hexdigest()

    nome = (
        resultado.achado_id
        .replace("/", "_")
        .replace("\\", "_")
    )

    arquivo = raiz_resultados() / (
        f"{nome}-{digest[:12]}.json"
    )

    arquivo.write_text(
        conteudo,
        encoding="utf-8",
    )

    hash_file = arquivo.with_suffix(
        ".json.sha256"
    )

    hash_file.write_text(
        f"{digest}  {arquivo.name}\n",
        encoding="utf-8",
    )

    return {
        "arquivo": str(arquivo),
        "sha256": digest,
    }
