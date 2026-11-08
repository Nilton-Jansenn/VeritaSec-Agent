from __future__ import annotations

from copy import deepcopy
from typing import Any


DINAMICAS = frozenset(
    {
        "path_traversal",
        "busca_evolucionaria",
        "oraculo_path_traversal",
        "runtime_http",
        "autorizacao_http",
        "oraculo_autorizacao",
    }
)


def _valor(
    obj: Any,
    nome: str,
    default=None,
):
    if isinstance(obj, dict):
        return obj.get(nome, default)

    return getattr(
        obj,
        nome,
        default,
    )


def construir_contexto_adaptativo(
    *,
    achado: Any,
    dados: dict[str, Any],
) -> dict[str, Any]:

    politica = dados.get(
        "politica_escopo",
        {},
    )

    if not isinstance(
        politica,
        dict,
    ):
        politica = {}

    scr = dados.get(
        "scr",
        {},
    )

    if not isinstance(
        scr,
        dict,
    ):
        scr = {}

    seeds_info = dados.get(
        "seeds_cognitivas",
        {},
    )

    if not isinstance(
        seeds_info,
        dict,
    ):
        seeds_info = {}

    autorizadas = list(
        politica.get(
            "capacidades_autorizadas",
            [],
        )
    )

    sementes = list(
        seeds_info.get(
            "sementes_validadas",
            [],
        )
    )

    if not sementes:
        sementes = list(
            _valor(
                achado,
                "sementes",
                [],
            )
            or []
        )

    return {
        "finding_id": _valor(
            achado,
            "id",
            "",
        ),
        "regra": _valor(
            achado,
            "regra",
            "",
        ),
        "cwe": _valor(
            achado,
            "cwe",
            None,
        ),
        "arquivo": _valor(
            achado,
            "arquivo",
            "",
        ),
        "linha": _valor(
            achado,
            "linha",
            None,
        ),
        "scr": deepcopy(scr),
        "hipotese": deepcopy(
            dados.get(
                "hipotese",
                {},
            )
        ),
        "lacunas": deepcopy(
            dados.get(
                "lacunas",
                [],
            )
        ),
        "plano": deepcopy(
            dados.get(
                "plano_aquisicao_evidencia",
                {},
            )
        ),
        "aquisicao_inicial": deepcopy(
            dados.get(
                "aquisicao_evidencia",
                {},
            )
        ),
        "capacidades_autorizadas": autorizadas,
        "sementes_tipadas": sementes,
        "evidencia_estatica": True,
        "plausibilidade_semantica": (
            scr.get(
                "nivel_sustentacao"
            )
            in {
                "PLAUSIVEL",
                "PARCIAL",
            }
        ),
        "execucao_dinamica_permitida": bool(
            _valor(
                achado,
                "execucao_dinamica_permitida",
                False,
            )
        ),
        "raiz_sandbox": _valor(
            achado,
            "raiz_sandbox",
            None,
        ),
        "base_url_http": _valor(
            achado,
            "base_url_http",
            None,
        ),
        "caminho_http": _valor(
            achado,
            "caminho_http",
            None,
        ),
        "marcador_recurso": _valor(
            achado,
            "marcador_recurso",
            None,
        ),
        "max_iteracoes": int(
            _valor(
                achado,
                "max_iteracoes",
                3,
            )
            or 3
        ),
    }


class PlanejadorFindingAdaptativo:

    def __init__(
        self,
        contexto_base: dict[str, Any],
    ) -> None:

        self.contexto_base = deepcopy(
            contexto_base
        )

        self.rodada = 0

    def __call__(
        self,
        contexto: dict[str, Any],
    ) -> dict[str, Any]:

        self.rodada += 1

        atual = deepcopy(
            self.contexto_base
        )

        if isinstance(
            contexto,
            dict,
        ):
            atual.update(
                deepcopy(contexto)
            )

        autorizadas = set(
            atual.get(
                "capacidades_autorizadas",
                [],
            )
        )

        sementes = list(
            atual.get(
                "sementes_tipadas",
                [],
            )
        )

        if (
            "path_traversal"
            in autorizadas
            and atual.get(
                "raiz_sandbox"
            )
            and sementes
        ):
            return {
                "capacidade": (
                    "path_traversal"
                ),
                "parametros": {
                    "hipotese_id": (
                        atual.get(
                            "finding_id",
                            "finding",
                        )
                    ),
                    "raiz_sandbox": (
                        atual[
                            "raiz_sandbox"
                        ]
                    ),
                    "sementes": sementes,
                    "max_geracoes": min(
                        6,
                        max(
                            1,
                            int(
                                atual.get(
                                    "max_iteracoes",
                                    3,
                                )
                            ),
                        ),
                    ),
                },
                "rodada": self.rodada,
                "origem": (
                    "planejador_finding"
                ),
            }

        if (
            "autorizacao_http"
            in autorizadas
            and atual.get(
                "base_url_http"
            )
            and atual.get(
                "caminho_http"
            )
            and atual.get(
                "marcador_recurso"
            )
        ):
            return {
                "capacidade": (
                    "autorizacao_http"
                ),
                "parametros": {
                    "base_url": (
                        atual[
                            "base_url_http"
                        ]
                    ),
                    "caminho": (
                        atual[
                            "caminho_http"
                        ]
                    ),
                    "marcador": (
                        atual[
                            "marcador_recurso"
                        ]
                    ),
                },
                "rodada": self.rodada,
                "origem": (
                    "planejador_finding"
                ),
            }

        return {
            "capacidade": None,
            "parametros": {},
            "rodada": self.rodada,
            "origem": (
                "planejador_finding"
            ),
            "sem_acao": True,
        }


class AutorizadorFindingAdaptativo:

    def __init__(
        self,
        capacidades_autorizadas: set[str],
    ) -> None:

        self.capacidades_autorizadas = set(
            capacidades_autorizadas
        )

    def __call__(
        self,
        pedido: dict[str, Any],
    ) -> dict[str, Any]:

        if not isinstance(
            pedido,
            dict,
        ):
            return {
                "autorizada": False,
                "motivo": (
                    "PEDIDO_INVALIDO"
                ),
            }

        capacidade = pedido.get(
            "capacidade"
        )

        autorizada = bool(
            isinstance(
                capacidade,
                str,
            )
            and capacidade
            in self.capacidades_autorizadas
        )

        return {
            **pedido,
            "autorizada": autorizada,
            "motivo_autorizacao": (
                "AUTORIZADA_POLITICA_M25"
                if autorizada
                else "ACAO_NAO_AUTORIZADA"
            ),
        }


def construir_callbacks_ciclo(
    *,
    achado: Any,
    dados: dict[str, Any],
):

    contexto = construir_contexto_adaptativo(
        achado=achado,
        dados=dados,
    )

    autorizadas = set(
        contexto.get(
            "capacidades_autorizadas",
            [],
        )
    )

    return (
        contexto,
        PlanejadorFindingAdaptativo(
            contexto
        ),
        AutorizadorFindingAdaptativo(
            autorizadas
        ),
    )


def possui_dinamica_autorizada(
    contexto: dict[str, Any],
) -> bool:

    return bool(
        set(
            contexto.get(
                "capacidades_autorizadas",
                [],
            )
        )
        & DINAMICAS
    )
