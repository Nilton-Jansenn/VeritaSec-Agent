from __future__ import annotations

from typing import Any


CLASSES = {
    "VERDADEIRO_POSITIVO",
    "FALSO_POSITIVO",
    "INCONCLUSIVO",
}


def _classe(
    valor: Any,
) -> str | None:

    texto = (
        str(valor)
        .strip()
        .upper()
        .replace("-", "_")
        .replace(" ", "_")
    )

    aliases = {
        "VP":
            "VERDADEIRO_POSITIVO",

        "TRUE_POSITIVE":
            "VERDADEIRO_POSITIVO",

        "FP":
            "FALSO_POSITIVO",

        "FALSE_POSITIVE":
            "FALSO_POSITIVO",

        "INCONCLUSIVE":
            "INCONCLUSIVO",
    }

    texto = aliases.get(
        texto,
        texto,
    )

    return (
        texto
        if texto in CLASSES
        else None
    )


def _veredito(
    resultado: Any,
) -> str:

    encontrados = []


    def visitar(
        obj,
        caminho="",
    ):

        if isinstance(obj, dict):

            for chave, valor in obj.items():

                nome = str(
                    chave
                ).lower()

                novo = (
                    f"{caminho}.{nome}"
                    if caminho
                    else nome
                )

                if isinstance(
                    valor,
                    str,
                ):

                    classe = _classe(
                        valor
                    )

                    if classe:
                        score = 0

                        if nome == "veredito_final":
                            score += 100

                        elif nome == "veredito":
                            score += 80

                        if "final" in novo:
                            score += 20

                        if any(
                            x in novo
                            for x in (
                                "llm",
                                "modelo",
                                "painel",
                            )
                        ):
                            score -= 200

                        encontrados.append(
                            (
                                score,
                                classe,
                            )
                        )

                visitar(
                    valor,
                    novo,
                )

        elif isinstance(obj, list):

            for valor in obj:
                visitar(
                    valor,
                    caminho,
                )


    visitar(resultado)

    if not encontrados:
        return "INCONCLUSIVO"

    encontrados.sort(
        key=lambda x: x[0],
        reverse=True,
    )

    return encontrados[0][1]


def _coletar(
    resultado: Any,
    tokens: tuple[str, ...],
    limite: int = 50,
) -> list[str]:

    itens = []


    def adicionar(
        item,
    ):
        texto = str(
            item
        ).strip()

        if not texto:
            return

        texto = texto[:1200]

        if texto not in itens:
            itens.append(texto)


    def visitar(
        obj,
        caminho="",
    ):

        if len(itens) >= limite:
            return

        if isinstance(obj, dict):

            for chave, valor in obj.items():

                nome = str(
                    chave
                ).lower()

                novo = (
                    f"{caminho}.{nome}"
                    if caminho
                    else nome
                )

                if any(
                    token in novo
                    for token in tokens
                ):

                    if isinstance(
                        valor,
                        (
                            str,
                            int,
                            float,
                            bool,
                        ),
                    ):
                        adicionar(
                            f"{novo}={valor}"
                        )

                    elif isinstance(
                        valor,
                        list,
                    ):
                        for x in valor:

                            if isinstance(
                                x,
                                (
                                    str,
                                    int,
                                    float,
                                    bool,
                                ),
                            ):
                                adicionar(
                                    f"{novo}={x}"
                                )

                visitar(
                    valor,
                    novo,
                )

        elif isinstance(obj, list):

            for valor in obj:
                visitar(
                    valor,
                    caminho,
                )


    visitar(resultado)

    return itens[:limite]


def construir_fundamentacao_tecnica(
    resultado: dict[str, Any],
) -> dict[str, Any]:

    veredito = _veredito(
        resultado
    )

    favoraveis = _coletar(
        resultado,
        (
            "evidencia",
            "evidência",
            "oracle",
            "oraculo",
            "runtime",
            "source",
            "sink",
            "fluxo",
            "reach",
            "confirm",
            "reprodu",
            "hash",
        ),
    )

    refutacao = _coletar(
        resultado,
        (
            "refut",
            "sanit",
            "validacao",
            "validação",
            "guard",
            "canonical",
            "protec",
            "objec",
        ),
    )

    ausentes = _coletar(
        resultado,
        (
            "ausente",
            "lacuna",
            "insuf",
            "falt",
            "indispon",
            "nao_reprodu",
            "não_reprodu",
        ),
    )

    if (
        veredito
        == "VERDADEIRO_POSITIVO"
    ):
        explicacao = (
            "A classificação VERDADEIRO_POSITIVO "
            "requer sustentação técnica por evidências "
            "objetivas correlacionadas. Parecer de LLM, "
            "SAST ou alerta ZAP isoladamente não é prova."
        )

    elif (
        veredito
        == "FALSO_POSITIVO"
    ):
        explicacao = (
            "A classificação FALSO_POSITIVO requer "
            "refutação técnica da hipótese. Ausência "
            "de reprodução, sozinha, não constitui FP."
        )

    else:
        explicacao = (
            "A classificação INCONCLUSIVO indica que "
            "as evidências disponíveis são insuficientes "
            "para confirmar e também insuficientes para "
            "refutar a hipótese. As lacunas devem ser "
            "explicitamente registradas."
        )

    return {
        "veredito":
            veredito,

        "explicacao_tecnica":
            explicacao,

        "evidencias_favoraveis":
            favoraveis,

        "evidencias_refutacao":
            refutacao,

        "evidencias_ausentes":
            ausentes,

        "regras": [
            "SAST isolado não confirma.",
            "LLM isolada não confirma.",
            "ZAP isolado não confirma.",
            (
                "Consenso de modelos "
                "não constitui prova."
            ),
            (
                "NAO_REPRODUZIDO isolado "
                "não implica FALSO_POSITIVO."
            ),
        ],
    }


def anexar_fundamentacao_tecnica(
    resultado: Any,
) -> Any:

    if not isinstance(
        resultado,
        dict,
    ):
        return resultado

    novo = dict(
        resultado
    )

    novo[
        "fundamentacao_tecnica"
    ] = construir_fundamentacao_tecnica(
        novo
    )

    return novo
