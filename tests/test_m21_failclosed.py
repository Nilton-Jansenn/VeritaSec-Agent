from aplicacao.multiagente.aquisicao_evidencia import (
    ExecutorAquisicaoEvidencia,
)


class ExecutorHostil:

    def shell(self):
        raise AssertionError(
            "SHELL_CHAMADO"
        )


def test_shell_negado_nao_chega_executor():
    motor = (
        ExecutorAquisicaoEvidencia(
            ExecutorHostil()
        )
    )

    r = motor.executar_plano(
        achado=object(),
        plano={
            "decisoes_politica": [
                {
                    "capacidade":
                        "shell",
                    "autorizada":
                        False,
                    "motivo":
                        "CAPACIDADE_FORA_DA_ALLOWLIST",
                    "sementes": [],
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
