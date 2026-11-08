import unittest

from aplicacao.dominio.modelos import (
    AcaoInvestigacao,
    EscopoAutorizado,
    OrcamentoInvestigacao,
)
from aplicacao.investigacao.politica import PoliticaExecucao


class TestPolitica(unittest.TestCase):

    def setUp(self):
        self.politica = PoliticaExecucao()

    def test_ferramenta_permitida(self):
        decisao = self.politica.avaliar(
            AcaoInvestigacao(
                ferramenta="sarif",
                objetivo="ler achado",
            ),
            EscopoAutorizado(
                projeto="teste",
                ferramentas_permitidas={"sarif"},
            ),
            OrcamentoInvestigacao(),
        )

        self.assertTrue(decisao.autorizada)

    def test_ferramenta_nao_permitida(self):
        decisao = self.politica.avaliar(
            AcaoInvestigacao(
                ferramenta="shell",
                objetivo="executar comando",
            ),
            EscopoAutorizado(
                projeto="teste",
                ferramentas_permitidas={"sarif"},
            ),
            OrcamentoInvestigacao(),
        )

        self.assertFalse(decisao.autorizada)

    def test_execucao_dinamica_exige_permissao(self):
        decisao = self.politica.avaliar(
            AcaoInvestigacao(
                ferramenta="execucao_dinamica",
                objetivo="validar hipótese",
            ),
            EscopoAutorizado(
                projeto="teste",
                ferramentas_permitidas={
                    "execucao_dinamica"
                },
                execucao_dinamica_permitida=False,
            ),
            OrcamentoInvestigacao(),
        )

        self.assertFalse(decisao.autorizada)

    def test_orcamento_esgotado_bloqueia(self):
        orcamento = OrcamentoInvestigacao(
            max_acoes=1,
            max_chamadas_llm=1,
            max_execucoes_dinamicas=1,
            acoes_consumidas=1,
        )

        decisao = self.politica.avaliar(
            AcaoInvestigacao(
                ferramenta="sarif",
                objetivo="ler",
            ),
            EscopoAutorizado(
                projeto="teste",
                ferramentas_permitidas={"sarif"},
            ),
            orcamento,
        )

        self.assertFalse(decisao.autorizada)


if __name__ == "__main__":
    unittest.main()
