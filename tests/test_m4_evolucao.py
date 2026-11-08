import tempfile
import unittest

from aplicacao.evolucao.modelos import (
    ConfiguracaoEvolutiva,
)
from aplicacao.evolucao.path_traversal import (
    BuscaEvolutivaPathTraversal,
)


class TestEvolucao(
    unittest.TestCase
):

    def test_reproduzivel(
        self,
    ):
        with tempfile.TemporaryDirectory() as tmp:

            config = ConfiguracaoEvolutiva(
                max_geracoes=4,
                tamanho_populacao=8,
                semente_aleatoria=42,
            )

            a = BuscaEvolutivaPathTraversal(
                tmp,
                config,
            ).executar(
                ["arquivo.txt"]
            )

            b = BuscaEvolutivaPathTraversal(
                tmp,
                config,
            ).executar(
                ["arquivo.txt"]
            )

            self.assertEqual(
                a.model_dump(),
                b.model_dump(),
            )

    def test_limite_execucoes(
        self,
    ):
        with tempfile.TemporaryDirectory() as tmp:

            config = ConfiguracaoEvolutiva(
                max_geracoes=3,
                tamanho_populacao=6,
                semente_aleatoria=7,
            )

            resultado = (
                BuscaEvolutivaPathTraversal(
                    tmp,
                    config,
                ).executar(
                    ["arquivo.txt"]
                )
            )

            limite_teorico = (
                1
                + (
                    config.max_geracoes
                    * config.tamanho_populacao
                )
            )

            self.assertLessEqual(
                resultado.execucoes,
                limite_teorico,
            )

    def test_oraculo_confirma_escape(
        self,
    ):
        with tempfile.TemporaryDirectory() as tmp:

            resultado = (
                BuscaEvolutivaPathTraversal(
                    tmp,
                    ConfiguracaoEvolutiva(
                        max_geracoes=5,
                        tamanho_populacao=8,
                        semente_aleatoria=2026,
                    ),
                ).executar(
                    ["arquivo.txt"]
                )
            )

            self.assertTrue(
                resultado.confirmado
            )

            self.assertEqual(
                resultado.melhor.aptidao,
                1.0,
            )


if __name__ == "__main__":
    unittest.main()
