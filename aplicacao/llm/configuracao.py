from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PerfilLLM:
    context_length: int = 8192
    max_output_tokens: int = 512
    max_concurrency_local: int = 1
    evidence_chunk_tokens: int = 1200
    max_evidence_chunks: int = 4
    summary_max_tokens: int = 384
    history_max_messages: int = 6
    cache_ttl_seconds: int = 1800


def _parse_env(path: Path) -> dict[str, str]:
    dados: dict[str, str] = {}

    if not path.exists():
        return dados

    for raw in path.read_text(
        encoding="utf-8"
    ).splitlines():
        linha = raw.strip()

        if (
            not linha
            or linha.startswith("#")
            or "=" not in linha
        ):
            continue

        chave, valor = linha.split("=", 1)

        chave = chave.strip()

        if chave.startswith("VERITASSEC_"):
            dados[chave] = valor.strip()

    return dados


def carregar_perfil(
    path: str | Path | None = None,
) -> PerfilLLM:
    arquivo = (
        Path(path).expanduser()
        if path is not None
        else (
            Path.home()
            / ".config"
            / "veritassec"
            / "local-llm.env"
        )
    )

    env = _parse_env(arquivo)

    def inteiro(
        nome: str,
        padrao: int,
    ) -> int:
        valor = int(
            env.get(nome, str(padrao))
        )

        if valor <= 0:
            raise ValueError(
                f"{nome} deve ser > 0"
            )

        return valor

    return PerfilLLM(
        context_length=inteiro(
            "VERITASSEC_LOCAL_CONTEXT_LENGTH",
            8192,
        ),
        max_output_tokens=inteiro(
            "VERITASSEC_LOCAL_MAX_OUTPUT_TOKENS",
            512,
        ),
        max_concurrency_local=inteiro(
            "VERITASSEC_LOCAL_MAX_CONCURRENCY",
            1,
        ),
        evidence_chunk_tokens=inteiro(
            "VERITASSEC_CONTEXT_EVIDENCE_CHUNK_TOKENS",
            1200,
        ),
        max_evidence_chunks=inteiro(
            "VERITASSEC_CONTEXT_MAX_EVIDENCE_CHUNKS",
            4,
        ),
        summary_max_tokens=inteiro(
            "VERITASSEC_CONTEXT_SUMMARY_MAX_TOKENS",
            384,
        ),
        history_max_messages=inteiro(
            "VERITASSEC_CONTEXT_HISTORY_MAX_MESSAGES",
            6,
        ),
        cache_ttl_seconds=inteiro(
            "VERITASSEC_CACHE_TTL_SECONDS",
            1800,
        ),
    )
