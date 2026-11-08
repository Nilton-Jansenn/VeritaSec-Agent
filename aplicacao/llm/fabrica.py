from __future__ import annotations

from .cache import CacheMemoriaTTL
from .configuracao import (
    PerfilLLM,
    carregar_perfil,
)
from .contexto import (
    GerenciadorContexto,
    PoliticaContexto,
)
from .contratos import ProvedorLLM
from .gestor import (
    GerenciadorExecucaoLLM,
    PoliticaExecucaoLLM,
    RegistroProvedores,
)


def criar_registro_provedores(
    *,
    local: ProvedorLLM | None = None,
    gpt: ProvedorLLM | None = None,
    gemini: ProvedorLLM | None = None,
) -> RegistroProvedores:
    registro = RegistroProvedores()

    if local is not None:
        registro.registrar(
            "local",
            local,
        )

    if gpt is not None:
        registro.registrar(
            "gpt",
            gpt,
        )

    if gemini is not None:
        registro.registrar(
            "gemini",
            gemini,
        )

    return registro


def criar_gestor_padrao(
    registro: RegistroProvedores,
    perfil: PerfilLLM | None = None,
    max_tokens_saida_por_agente: dict[
        str,
        int,
    ] | None = None,
) -> GerenciadorExecucaoLLM:
    perfil = (
        perfil
        or carregar_perfil()
    )

    reserva = (
        perfil.max_output_tokens
        + 512
    )

    max_entrada = max(
        512,
        min(
            6144,
            perfil.context_length - reserva,
        ),
    )

    contexto = GerenciadorContexto(
        PoliticaContexto(
            max_tokens_entrada=max_entrada,
            max_tokens_por_evidencia=(
                perfil.evidence_chunk_tokens
            ),
            max_evidencias=(
                perfil.max_evidence_chunks
            ),
        )
    )

    cache = CacheMemoriaTTL(
        ttl_segundos=(
            perfil.cache_ttl_seconds
        )
    )

    politica = PoliticaExecucaoLLM(
        max_tokens_saida=(
            perfil.max_output_tokens
        ),
        concorrencia_local=(
            perfil.max_concurrency_local
        ),
        max_tokens_saida_por_agente=(
            max_tokens_saida_por_agente
            or {}
        ),
    )

    return GerenciadorExecucaoLLM(
        registro=registro,
        contexto=contexto,
        cache=cache,
        politica=politica,
    )
