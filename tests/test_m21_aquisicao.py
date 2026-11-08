from aplicacao.multiagente.aquisicao_evidencia import (
    ExecutorAquisicaoEvidencia,
    OrcamentoInvestigacao,
)


class ExecutorFake:

    def buscar_codigo(
        self,
        achado=None,
        sementes=None,
    ):
        return {
            "encontrado": True,
            "sementes": sementes,
        }

    def validar_path_traversal(
        self,
        achado=None,
        sementes=None,
    ):
        return {
            "violacao": (
                sementes[0]
                == "../fora.txt"
            ),
            "entrada":
                sementes[0],
        }


def test_negada_nao_executa():
    motor = (
        ExecutorAquisicaoEvidencia(
            ExecutorFake()
        )
    )

    r = motor.executar_plano(
        achado=object(),
        plano={
            "decisoes_politica": [
                {
                    "capacidade":
                        "path_traversal",
                    "autorizada":
                        False,
                    "motivo":
                        "EXECUCAO_DINAMICA_NAO_AUTORIZADA",
                    "sementes": [
                        "../fora.txt"
                    ],
                }
            ]
        },
    )

    assert (
        r["orcamento"][
            "acoes_executadas"
        ]
        == 0
    )

    assert (
        r["resultados"][0][
            "executada"
        ]
        is False
    )


def test_estatica_autorizada_executa():
    motor = (
        ExecutorAquisicaoEvidencia(
            ExecutorFake()
        )
    )

    r = motor.executar_plano(
        achado=object(),
        plano={
            "decisoes_politica": [
                {
                    "capacidade":
                        "busca_codigo",
                    "autorizada":
                        True,
                    "motivo":
                        "AUTORIZADA",
                    "sementes": [
                        "sink"
                    ],
                }
            ]
        },
    )

    item = r[
        "resultados"
    ][0]

    assert (
        item["executada"]
        is True
    )

    assert (
        item["resultado"][
            "encontrado"
        ]
        is True
    )


def test_seed_chega_executor():
    motor = (
        ExecutorAquisicaoEvidencia(
            ExecutorFake()
        )
    )

    r = motor.executar_plano(
        achado=object(),
        plano={
            "decisoes_politica": [
                {
                    "capacidade":
                        "path_traversal",
                    "autorizada":
                        True,
                    "motivo":
                        "AUTORIZADA",
                    "sementes": [
                        "../fora.txt"
                    ],
                }
            ]
        },
    )

    item = r[
        "resultados"
    ][0]

    assert (
        item["resultado"][
            "entrada"
        ]
        == "../fora.txt"
    )

    assert (
        item["resultado"][
            "violacao"
        ]
        is True
    )


def test_orcamento():
    motor = (
        ExecutorAquisicaoEvidencia(
            ExecutorFake(),
            orcamento=(
                OrcamentoInvestigacao(
                    max_acoes=1
                )
            ),
        )
    )

    plano = {
        "decisoes_politica": [
            {
                "capacidade":
                    "busca_codigo",
                "autorizada": True,
                "motivo":
                    "AUTORIZADA",
                "sementes": [],
            },
            {
                "capacidade":
                    "busca_codigo",
                "autorizada": True,
                "motivo":
                    "AUTORIZADA",
                "sementes": [],
            },
        ]
    }

    r = motor.executar_plano(
        achado=object(),
        plano=plano,
    )

    assert (
        r["orcamento"][
            "acoes_executadas"
        ]
        == 1
    )

    assert (
        r["criterio_parada"]
        == "ORCAMENTO_ESGOTADO"
    )
