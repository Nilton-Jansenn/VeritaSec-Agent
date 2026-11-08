import hashlib
import json
import time
from pathlib import Path
from typing import Any

from aplicacao.nucleo.configuracoes import configuracoes


def gerar_hash(objeto: Any) -> str:
    serializado = json.dumps(
        objeto,
        ensure_ascii=False,
        sort_keys=True,
        default=str,
    )

    return hashlib.sha256(serializado.encode("utf-8")).hexdigest()


def registrar_auditoria_ia(
    entrada: dict,
    saida: dict | None,
    erro: str | None,
    provedor: str,
    modelo: str,
    duracao_ms: int,
    caminho: str | None = None,
) -> None:
    caminho_efetivo = caminho or configuracoes.CAMINHO_AUDITORIA_IA

    Path(caminho_efetivo).parent.mkdir(parents=True, exist_ok=True)

    evento = {
        "timestamp": int(time.time()),
        "provedor": provedor,
        "modelo": modelo,
        "hash_entrada": gerar_hash(entrada),
        "hash_saida": gerar_hash(saida) if saida else None,
        "duracao_ms": duracao_ms,
        "erro": erro,
    }

    with open(caminho_efetivo, "a", encoding="utf-8") as arquivo:
        arquivo.write(json.dumps(evento, ensure_ascii=False) + "\n")
