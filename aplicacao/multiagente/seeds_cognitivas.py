from __future__ import annotations

from copy import deepcopy
from dataclasses import (
    fields,
    is_dataclass,
    replace,
)
from typing import Any


LIMITE_SEMENTES = 16
LIMITE_TAMANHO_SEMENTE = 512

CAPACIDADES_COM_SEEDS = frozenset(
    {
        "path_traversal",
        "busca_evolucionaria",
        "oraculo_path_traversal",
    }
)


def validar_sementes_cognitivas(
    valor: Any,
) -> dict[str, Any]:

    validas: list[str] = []
    rejeitadas: list[
        dict[str, str]
    ] = []

    if valor is None:
        valor = []

    if not isinstance(
        valor,
        (list, tuple),
    ):
        return {
            "sementes_validas": [],
            "rejeitadas": [
                {
                    "valor": repr(valor)[:120],
                    "motivo": "TIPO_INVALIDO",
                }
            ],
        }

    for indice, item in enumerate(valor):

        if indice >= LIMITE_SEMENTES:
            rejeitadas.append(
                {
                    "valor": str(item)[:120],
                    "motivo": "LIMITE_QUANTIDADE",
                }
            )
            continue

        if not isinstance(
            item,
            str,
        ):
            rejeitadas.append(
                {
                    "valor": repr(item)[:120],
                    "motivo": "TIPO_INVALIDO",
                }
            )
            continue

        if not item:
            rejeitadas.append(
                {
                    "valor": "",
                    "motivo": "VAZIA",
                }
            )
            continue

        if "\x00" in item:
            rejeitadas.append(
                {
                    "valor": repr(item)[:120],
                    "motivo": "NUL",
                }
            )
            continue

        if (
            len(item)
            > LIMITE_TAMANHO_SEMENTE
        ):
            rejeitadas.append(
                {
                    "valor": item[:120],
                    "motivo": "TAMANHO",
                }
            )
            continue

        if item not in validas:
            validas.append(item)

    return {
        "sementes_validas": validas,
        "rejeitadas": rejeitadas,
        "limite_quantidade": LIMITE_SEMENTES,
        "limite_tamanho": LIMITE_TAMANHO_SEMENTE,
    }


def extrair_sementes_tipadas(
    decisoes_por_agente: list[
        tuple[str, dict[str, Any]]
    ],
) -> tuple[
    tuple[str, ...],
    list[dict[str, Any]],
]:

    acumuladas: list[str] = []
    auditoria: list[
        dict[str, Any]
    ] = []

    for agente, decisao in (
        decisoes_por_agente
    ):

        if not isinstance(
            decisao,
            dict,
        ):
            continue

        # IMPORTANTE:
        # somente o campo estruturado.
        resultado = validar_sementes_cognitivas(
            decisao.get(
                "sementes_sugeridas",
                [],
            )
        )

        auditoria.append(
            {
                "agente": agente,
                **resultado,
            }
        )

        for seed in resultado[
            "sementes_validas"
        ]:
            if seed not in acumuladas:
                acumuladas.append(seed)

            if (
                len(acumuladas)
                >= LIMITE_SEMENTES
            ):
                break

        if (
            len(acumuladas)
            >= LIMITE_SEMENTES
        ):
            break

    return (
        tuple(acumuladas),
        auditoria,
    )


def _capacidade_do_objeto(
    obj: Any,
) -> str | None:

    if isinstance(obj, dict):
        valor = obj.get(
            "capacidade"
        )

    else:
        valor = getattr(
            obj,
            "capacidade",
            None,
        )

    return (
        valor
        if isinstance(valor, str)
        else None
    )


def _transformar(
    obj: Any,
    *,
    sementes: tuple[str, ...],
    capacidades_autorizadas: set[str],
) -> Any:
    """
    Reconstrói preservando o tipo real.

    Compatível com:
    - dataclasses;
    - Pydantic model_copy;
    - dict;
    - list;
    - tuple;
    - demais objetos imutáveis.

    Não depende de model_validate().
    """

    capacidade = (
        _capacidade_do_objeto(
            obj
        )
    )

    # --------------------------------------------------------
    # DICT
    # --------------------------------------------------------

    if isinstance(obj, dict):

        novo = {}

        for chave, valor in obj.items():

            if (
                chave == "sementes"
                and capacidade
                in CAPACIDADES_COM_SEEDS
            ):
                if (
                    capacidade
                    in capacidades_autorizadas
                    and sementes
                ):
                    novo[chave] = list(
                        sementes
                    )
                else:
                    novo[chave] = []

            else:
                novo[chave] = _transformar(
                    valor,
                    sementes=sementes,
                    capacidades_autorizadas=(
                        capacidades_autorizadas
                    ),
                )

        return novo

    # --------------------------------------------------------
    # LIST / TUPLE
    # --------------------------------------------------------

    if isinstance(obj, list):
        return [
            _transformar(
                item,
                sementes=sementes,
                capacidades_autorizadas=(
                    capacidades_autorizadas
                ),
            )
            for item in obj
        ]

    if isinstance(obj, tuple):
        return tuple(
            _transformar(
                item,
                sementes=sementes,
                capacidades_autorizadas=(
                    capacidades_autorizadas
                ),
            )
            for item in obj
        )

    # --------------------------------------------------------
    # DATACLASS
    # --------------------------------------------------------

    if (
        is_dataclass(obj)
        and not isinstance(
            obj,
            type,
        )
    ):

        atualizacoes = {}

        for campo in fields(obj):

            valor = getattr(
                obj,
                campo.name,
            )

            if (
                campo.name == "sementes"
                and capacidade
                in CAPACIDADES_COM_SEEDS
            ):
                if (
                    capacidade
                    in capacidades_autorizadas
                    and sementes
                ):
                    atualizacoes[
                        campo.name
                    ] = tuple(
                        sementes
                    )

                else:
                    atualizacoes[
                        campo.name
                    ] = ()

            else:
                atualizacoes[
                    campo.name
                ] = _transformar(
                    valor,
                    sementes=sementes,
                    capacidades_autorizadas=(
                        capacidades_autorizadas
                    ),
                )

        return replace(
            obj,
            **atualizacoes,
        )

    # --------------------------------------------------------
    # PYDANTIC / MODELOS COM model_copy
    # --------------------------------------------------------

    model_copy = getattr(
        obj,
        "model_copy",
        None,
    )

    model_fields = getattr(
        type(obj),
        "model_fields",
        None,
    )

    if (
        callable(model_copy)
        and isinstance(
            model_fields,
            dict,
        )
    ):

        atualizacoes = {}

        for nome in model_fields:

            valor = getattr(
                obj,
                nome,
            )

            if (
                nome == "sementes"
                and capacidade
                in CAPACIDADES_COM_SEEDS
            ):
                atualizacoes[nome] = (
                    list(sementes)
                    if (
                        capacidade
                        in capacidades_autorizadas
                        and sementes
                    )
                    else []
                )

            else:
                atualizacoes[
                    nome
                ] = _transformar(
                    valor,
                    sementes=sementes,
                    capacidades_autorizadas=(
                        capacidades_autorizadas
                    ),
                )

        return model_copy(
            update=atualizacoes
        )

    # --------------------------------------------------------
    # OBJETO COM __dict__
    #
    # Usar cópia, nunca alterar original diretamente.
    # --------------------------------------------------------

    if hasattr(
        obj,
        "__dict__",
    ):

        copia = deepcopy(obj)

        for nome, valor in vars(
            copia
        ).items():

            if (
                nome == "sementes"
                and capacidade
                in CAPACIDADES_COM_SEEDS
            ):
                try:
                    setattr(
                        copia,
                        nome,
                        (
                            tuple(sementes)
                            if (
                                capacidade
                                in capacidades_autorizadas
                                and sementes
                            )
                            else ()
                        ),
                    )

                except Exception:
                    pass

            else:
                try:
                    setattr(
                        copia,
                        nome,
                        _transformar(
                            valor,
                            sementes=sementes,
                            capacidades_autorizadas=(
                                capacidades_autorizadas
                            ),
                        ),
                    )

                except Exception:
                    pass

        return copia

    return obj


def aplicar_sementes_ao_plano(
    plano: Any,
    *,
    sementes: tuple[str, ...],
    capacidades_autorizadas: set[str],
):
    """
    Preserva o tipo original de PlanoAquisicaoEvidencia.

    A seed:
    - não autoriza capability;
    - não muda sandbox;
    - não muda alvo;
    - não muda URL;
    - não vira shell.
    """

    return _transformar(
        plano,
        sementes=sementes,
        capacidades_autorizadas=(
            capacidades_autorizadas
        ),
    )
