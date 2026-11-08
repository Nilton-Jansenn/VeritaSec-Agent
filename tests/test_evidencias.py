import unittest

from aplicacao.dominio.enums import TipoEvidencia
from aplicacao.dominio.modelos import Evidencia
from aplicacao.investigacao.evidencias import (
    adicionar_evidencia,
    hash_evidencia,
)


class TestEvidencias(unittest.TestCase):

    def test_hash_deterministico(self):
        self.assertEqual(
            hash_evidencia({"b": 2, "a": 1}),
            hash_evidencia({"a": 1, "b": 2}),
        )

    def test_hash_muda_com_conteudo(self):
        self.assertNotEqual(
            hash_evidencia({"a": 1}),
            hash_evidencia({"a": 2}),
        )

    def test_evidencia_duplicada_falha(self):
        evidencia = Evidencia(
            id="e1",
            hipotese_id="h1",
            tipo=TipoEvidencia.ESTATICA,
            origem="sast",
            descricao="achado",
            observacao="teste",
        )

        with self.assertRaises(ValueError):
            adicionar_evidencia(
                [evidencia],
                evidencia,
            )


if __name__ == "__main__":
    unittest.main()
