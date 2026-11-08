from __future__ import annotations

from typing import Any


def dump(
    valor: Any,
) -> Any:

    if isinstance(valor, dict):
        return {
            str(k): dump(v)
            for k, v in valor.items()
        }

    if isinstance(
        valor,
        (
            list,
            tuple,
            set,
        ),
    ):
        return [
            dump(x)
            for x in valor
        ]

    if hasattr(
        valor,
        "model_dump",
    ):
        try:
            return dump(
                valor.model_dump(
                    mode="json"
                )
            )
        except Exception:
            pass

    if hasattr(
        valor,
        "__dict__",
    ):
        try:
            return dump(
                vars(valor)
            )
        except Exception:
            pass

    return valor


def construir_contexto_fase1(
    *,
    achado: Any,
    hipotese: Any,
    superficie: Any,
    scr: Any,
    evidencias: Any,
    painel: Any,
) -> dict[str, Any]:

    return {
        "fase":
            "pre_execucao",

        "objetivo":
            (
                "Refutar a hipótese antes "
                "do planejamento dinâmico."
            ),

        "achado":
            dump(achado),

        "hipotese":
            dump(hipotese),

        "superficie":
            dump(superficie),

        "scr":
            dump(scr),

        "evidencias":
            dump(evidencias),

        "painel_multimodelo":
            dump(painel),

        "questoes_adversariais": [
            "A source é controlável?",
            "O sink é alcançável?",
            (
                "Há sanitização, validação, "
                "canonicalização ou guard?"
            ),
            (
                "Existe pré-condição "
                "não demonstrada?"
            ),
            (
                "Existe caminho alternativo "
                "mais seguro?"
            ),
            (
                "Existe explicação alternativa "
                "para a evidência?"
            ),
            (
                "Que evidência confirmaria "
                "objetivamente?"
            ),
            (
                "Que evidência refutaria "
                "objetivamente?"
            ),
        ],
    }


def consolidar_fase1(
    *,
    registro_agente: Any,
    painel: dict[str, Any],
) -> dict[str, Any]:

    registro = dump(
        registro_agente
    )

    decisao = (
        registro.get(
            "decisao",
            {},
        )
        if isinstance(
            registro,
            dict,
        )
        else {}
    )

    observacoes = decisao.get(
        "observacoes",
        [],
    )

    if isinstance(
        observacoes,
        str,
    ):
        observacoes = [
            observacoes
        ]

    lacunas = list(
        painel.get(
            "lacunas",
            [],
        )
    )

    if (
        decisao.get(
            "requer_evidencia_adicional",
            False,
        )
    ):
        for observacao in observacoes:
            texto = str(
                observacao
            ).strip()

            if texto:
                item = (
                    "critico_fase1:"
                    + texto[:500]
                )

                if item not in lacunas:
                    lacunas.append(item)

    return {
        "fase":
            "pre_execucao",

        "raciocinio_agente":
            registro,

        "painel_multimodelo":
            painel,

        "lacunas":
            lacunas,

        "hipoteses_candidatas":
            painel.get(
                "hipoteses_candidatas",
                [],
            ),

        "objecoes":
            painel.get(
                "objecoes",
                [],
            ),

        "autoridade_decisoria":
            False,
    }


def aplicar_fase1_na_hipotese(
    *,
    hipotese: dict[str, Any],
    fase1: dict[str, Any],
) -> None:

    hipotese[
        "critica_adversarial_fase1"
    ] = fase1

    ausentes = hipotese.get(
        "evidencias_ausentes",
        [],
    )

    if isinstance(
        ausentes,
        str,
    ):
        ausentes = [ausentes]

    if not isinstance(
        ausentes,
        list,
    ):
        ausentes = []

    for lacuna in fase1.get(
        "lacunas",
        [],
    ):

        item = str(
            lacuna
        ).strip()

        if (
            item
            and item not in ausentes
        ):
            ausentes.append(item)

    hipotese[
        "evidencias_ausentes"
    ] = ausentes

    candidatas = fase1.get(
        "hipoteses_candidatas",
        [],
    )

    if candidatas:
        hipotese[
            "hipoteses_multimodelo"
        ] = candidatas

    objecoes = fase1.get(
        "objecoes",
        [],
    )

    if objecoes:
        hipotese[
            "objecoes_adversariais_fase1"
        ] = objecoes
