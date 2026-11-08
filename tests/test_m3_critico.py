import unittest

from aplicacao.agentes.critico import CriticoAdversarial
from aplicacao.dominio.enums import TipoEvidencia
from aplicacao.dominio.modelos import (
    EscopoAutorizado,
    Evidencia,
    HipoteseVulnerabilidade,
    Investigacao,
    ReferenciaAchado,
)


class TestCritico(unittest.TestCase):

    def _inv(self):
        inv = Investigacao(
            achado=ReferenciaAchado(
                projeto="teste",
                regra="r",
                arquivo="app.py",
                mensagem="teste",
            ),
            escopo=EscopoAutorizado(
                projeto="teste"
            ),
        )

        inv.hipotese = HipoteseVulnerabilidade(
            achado_id=inv.achado.id,
            tipo="teste",
            descricao="teste",
            propriedade_seguranca="teste",
            confianca=0.5,
        )

        return inv

    def test_exige_contexto(self):
        decisao = CriticoAdversarial().revisar(
            self._inv()
        )

        self.assertFalse(
            decisao.evidencia_suficiente
        )

        self.assertIn(
            "contexto de código",
            decisao.evidencias_ausentes,
        )

    def test_detecta_dinamica_sem_oraculo(self):
        inv = self._inv()

        inv.evidencias.extend([
            Evidencia(
                hipotese_id=inv.hipotese.id,
                tipo=TipoEvidencia.CONTEXTO_CODIGO,
                origem="codigo",
                descricao="contexto",
                observacao="ok",
            ),
            Evidencia(
                hipotese_id=inv.hipotese.id,
                tipo=TipoEvidencia.EXECUCAO_DINAMICA,
                origem="executor",
                descricao="execução",
                observacao="ok",
            ),
        ])

        decisao = CriticoAdversarial().revisar(inv)

        self.assertTrue(decisao.conflitos)


if __name__ == "__main__":
    unittest.main()
