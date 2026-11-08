import tempfile
import unittest
from pathlib import Path

from aplicacao.dinamica.executor import (
    ExecutorArquivoControlado,
    ViolacaoEscopoDinamico,
)
from aplicacao.dinamica.servico import (
    ValidadorPathTraversal,
)


class TestPathTraversal(unittest.TestCase):

    def test_oraculo_detecta_escape(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            sandbox = base / "sandbox"
            sandbox.mkdir()

            executor = ExecutorArquivoControlado(
                sandbox
            )

            validador = ValidadorPathTraversal(
                executor
            )

            dinamica, oraculo = validador.validar(
                "h1",
                "../fora.txt",
            )

            self.assertTrue(
                oraculo.metadados[
                    "violacao_confirmada"
                ]
            )

            self.assertTrue(
                dinamica.reproduzivel
            )

    def test_oraculo_nao_detecta_caminho_interno(self):
        with tempfile.TemporaryDirectory() as tmp:
            sandbox = Path(tmp)
            executor = ExecutorArquivoControlado(
                sandbox
            )

            _, oraculo = (
                ValidadorPathTraversal(
                    executor
                ).validar(
                    "h1",
                    "interno.txt",
                )
            )

            self.assertFalse(
                oraculo.metadados[
                    "violacao_confirmada"
                ]
            )

    def test_leitura_bloqueia_escape(self):
        with tempfile.TemporaryDirectory() as tmp:
            sandbox = Path(tmp)

            executor = ExecutorArquivoControlado(
                sandbox
            )

            with self.assertRaises(
                ViolacaoEscopoDinamico
            ):
                executor.ler_seguro(
                    "../fora.txt"
                )


if __name__ == "__main__":
    unittest.main()
