import unittest

from pydantic import ValidationError

from aplicacao.dominio.enums import EstadoInvestigacao
from aplicacao.dominio.modelos import (
    EscopoAutorizado,
    HipoteseVulnerabilidade,
    Investigacao,
    ReferenciaAchado,
)


class TestDominio(unittest.TestCase):

    def test_estado_inicial(self):
        investigacao = Investigacao(
            achado=ReferenciaAchado(
                projeto="teste",
                regra="regra",
                arquivo="app.py",
                linha=1,
                mensagem="teste",
            ),
            escopo=EscopoAutorizado(
                projeto="teste",
                ferramentas_permitidas={"sarif"},
            ),
        )

        self.assertEqual(
            investigacao.estado,
            EstadoInvestigacao.CANDIDATO_ESTATICO,
        )

    def test_confianca_superior_a_um_falha(self):
        with self.assertRaises(ValidationError):
            HipoteseVulnerabilidade(
                achado_id="a",
                tipo="teste",
                descricao="teste",
                propriedade_seguranca="teste",
                confianca=1.1,
            )

    def test_confianca_negativa_falha(self):
        with self.assertRaises(ValidationError):
            HipoteseVulnerabilidade(
                achado_id="a",
                tipo="teste",
                descricao="teste",
                propriedade_seguranca="teste",
                confianca=-0.1,
            )

    def test_projeto_vazio_falha(self):
        with self.assertRaises(ValidationError):
            EscopoAutorizado(
                projeto="   ",
                ferramentas_permitidas={"sarif"},
            )


if __name__ == "__main__":
    unittest.main()
