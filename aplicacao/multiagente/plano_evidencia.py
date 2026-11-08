from __future__ import annotations

from .capacidades_canonicas import (
    canonicalizar_capacidade,
)


from dataclasses import dataclass
from typing import Any

from .controle_cognitivo import (
    DecisaoPoliticaCognitiva,
    aplicar_politica_cognitiva,
    extrair_solicitacoes_cognitivas,
)


@dataclass(frozen=True)
class PlanoAquisicaoEvidencia:
    hipoteses: tuple[str, ...]
    lacunas: tuple[str, ...]
    estrategia: str
    decisoes_politica: tuple[
        DecisaoPoliticaCognitiva,
        ...,
    ]

    def model_dump(self) -> dict[str, Any]:
        return {
            "hipoteses": list(
                self.hipoteses
            ),
            "lacunas": list(
                self.lacunas
            ),
            "estrategia": self.estrategia,
            "decisoes_politica": [
                {
                    "agente": x.agente,
                    "capacidade": (
                        x.capacidade
                    ),
                    "autorizada": (
                        x.autorizada
                    ),
                    "motivo": x.motivo,
                    "sementes": list(
                        x.sementes
                    ),
                }
                for x
                in self.decisoes_politica
            ],
        }


def _campo(
    decisao: Any,
    *nomes: str,
) -> Any:
    for nome in nomes:
        if isinstance(
            decisao,
            dict,
        ):
            valor = decisao.get(
                nome
            )
        else:
            valor = getattr(
                decisao,
                nome,
                None,
            )

        if valor:
            return valor

    return None


def _strings(
    valor: Any,
) -> tuple[str, ...]:
    if not valor:
        return ()

    if isinstance(valor, str):
        valor = [valor]

    if not isinstance(
        valor,
        (
            list,
            tuple,
            set,
        ),
    ):
        return ()

    saida = []

    for item in valor:
        texto = str(item).strip()

        if texto and texto not in saida:
            saida.append(
                texto[:1000]
            )

    return tuple(saida)


def construir_plano_aquisicao(
    *,
    decisoes_por_agente: list[
        tuple[str, Any]
    ],
    capacidades_registradas: set[str],
    capacidades_autorizadas: set[str],
    execucao_dinamica_permitida: bool,
) -> PlanoAquisicaoEvidencia:

    hipoteses: list[str] = []
    lacunas: list[str] = []
    estrategias: list[str] = []
    solicitacoes = []

    for agente, decisao in (
        decisoes_por_agente
    ):
        for item in _strings(
            _campo(
                decisao,
                "hipoteses",
                "hipotese",
                "hipotese_causal",
            )
        ):
            if item not in hipoteses:
                hipoteses.append(item)

        for item in _strings(
            _campo(
                decisao,
                "lacunas_evidencia",
                "evidencias_ausentes",
                "lacunas",
            )
        ):
            if item not in lacunas:
                lacunas.append(item)

        estrategia = _campo(
            decisao,
            "estrategia_validacao",
            "estrategia",
            "proximo_passo",
        )

        if estrategia:
            texto = str(
                estrategia
            ).strip()

            if (
                texto
                and texto
                not in estrategias
            ):
                estrategias.append(
                    texto[:1000]
                )

        solicitacoes.extend(
            extrair_solicitacoes_cognitivas(
                agente=agente,
                decisao=decisao,
            )
        )

    decisoes = aplicar_politica_cognitiva(
        solicitacoes,
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

    return PlanoAquisicaoEvidencia(
        hipoteses=tuple(hipoteses),
        lacunas=tuple(lacunas),
        estrategia="\n".join(
            estrategias
        ),
        decisoes_politica=decisoes,
    )
