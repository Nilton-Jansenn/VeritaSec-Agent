import asyncio
import tempfile
import unittest
from pathlib import Path

from aplicacao.dominio.modelos import (
    EscopoAutorizado,
    ReferenciaAchado,
)
from aplicacao.investigacao.motor import MotorInvestigacao
from aplicacao.persistencia.investigacoes import (
    RepositorioInvestigacoesJson,
)


class TestMotor(unittest.TestCase):

    def test_fluxo_inicial(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)

            (raiz / "app.py").write_text(
                """
def download(path):
    return open(path).read()
""",
                encoding="utf-8",
            )

            repo = RepositorioInvestigacoesJson(
                raiz / "estado"
            )

            motor = MotorInvestigacao(
                raiz,
                repo,
            )

            estado = asyncio.run(
                motor.criar(
                    ReferenciaAchado(
                        projeto="teste",
                        regra="path-traversal",
                        arquivo="app.py",
                        linha=2,
                        cwe="CWE-22",
                        mensagem=(
                            "possível path traversal"
                        ),
                    ),
                    EscopoAutorizado(
                        projeto="teste",
                        caminhos_permitidos=[
                            "app.py"
                        ],
                        ferramentas_permitidas={
                            "busca_codigo",
                            "revisao_codigo_seguro",
                        },
                    ),
                )
            )

            self.assertIsNotNone(
                estado.investigacao.hipotese
            )

            self.assertTrue(
                estado.lacunas
            )

            self.assertTrue(
                estado.investigacao.plano.acoes
            )

            estado = motor.executar_proxima_acao(
                estado
            )

            self.assertEqual(
                len(
                    estado.investigacao.evidencias
                ),
                1,
            )

            self.assertTrue(
                estado.proveniencia
            )


if __name__ == "__main__":
    unittest.main()
