import tempfile
import unittest
from pathlib import Path

from aplicacao.ferramentas.codigo import FerramentaCodigo
from aplicacao.revisao_codigo.motor import (
    MotorRevisaoCodigoSeguro,
)


class TestRevisaoCodigo(unittest.TestCase):

    def test_revisao(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)

            (raiz / "app.py").write_text(
                """
def download(path):
    sanitized = validate(path)
    return open(sanitized).read()
""",
                encoding="utf-8",
            )

            motor = MotorRevisaoCodigoSeguro(
                FerramentaCodigo(raiz)
            )

            resultado = motor.revisar(
                "app.py"
            )

            controles = {
                item.controle: item
                for item in resultado.controles
            }

            self.assertTrue(
                controles[
                    "validacao_ou_sanitizacao"
                ].observado
            )

            self.assertTrue(
                controles[
                    "sink_de_caminho"
                ].observado
            )

            self.assertTrue(
                resultado.limitacoes
            )


if __name__ == "__main__":
    unittest.main()
