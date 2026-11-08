from __future__ import annotations

from typing import Any

from .plano_evidencia import (
    construir_plano_aquisicao,
)

from .seeds_cognitivas import (
    aplicar_sementes_ao_plano,
    extrair_sementes_tipadas,
)


def construir_plano_aquisicao_com_seeds(
    *,
    decisoes_por_agente: list[
        tuple[str, dict[str, Any]]
    ],
    capacidades_registradas: set[str],
    capacidades_autorizadas: set[str],
    execucao_dinamica_permitida: bool,
):

    sementes, auditoria = (
        extrair_sementes_tipadas(
            decisoes_por_agente
        )
    )

    plano_original = (
        construir_plano_aquisicao(
            decisoes_por_agente=(
                decisoes_por_agente
            ),
            capacidades_registradas=(
                capacidades_registradas
            ),
            capacidades_autorizadas=(
                capacidades_autorizadas
            ),
            execucao_dinamica_permitida=(
                execucao_dinamica_permitida
            ),
        )
    )

    plano_final = (
        aplicar_sementes_ao_plano(
            plano_original,
            sementes=sementes,
            capacidades_autorizadas=(
                capacidades_autorizadas
            ),
        )
    )

    assert (
        type(plano_final)
        is type(plano_original)
    )

    return (
        plano_final,
        {
            "sementes_validadas": list(
                sementes
            ),
            "auditoria": auditoria,
            "origem": (
                "DecisaoAgenteLLM."
                "sementes_sugeridas"
            ),
            "texto_livre_interpretado": False,
            "observacoes_interpretadas": False,
            "shell_interpretado": False,
            "tipo_plano_preservado": True,
        },
    )
