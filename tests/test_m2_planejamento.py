import unittest

from aplicacao.dominio.modelos import (
    EscopoAutorizado,
    Investigacao,
    LacunaEvidencia,
    ReferenciaAchado,
)
from aplicacao.investigacao.planejador import (
    PlanejadorAdaptativo,
)


class TestPlanejador(unittest.TestCase):

    def test_prioridade(self):
        inv = Investigacao(
            achado=ReferenciaAchado(
                projeto="teste",
                regra="regra",
                arquivo="app.py",
                mensagem="teste",
            ),
            escopo=EscopoAutorizado(
                projeto="teste"
            ),
        )

        plano = PlanejadorAdaptativo().planejar(
            inv,
            [
                LacunaEvidencia(
                    tipo="fluxo_dados",
                    descricao="fluxo",
                    prioridade=10,
                ),
                LacunaEvidencia(
                    tipo="contexto_codigo",
                    descricao="contexto",
                    prioridade=100,
                ),
            ],
        )

        self.assertEqual(
            plano.acoes[0].ferramenta,
            "busca_codigo",
        )

        self.assertEqual(
            plano.acoes[0].parametros["lacuna"],
            "contexto_codigo",
        )


if __name__ == "__main__":
    unittest.main()
