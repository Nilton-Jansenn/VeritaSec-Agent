import unittest

from aplicacao.dominio.enums import (
    TipoEvidencia,
)
from aplicacao.dominio.modelos import (
    EscopoAutorizado,
    Evidencia,
    Investigacao,
    ReferenciaAchado,
)
from aplicacao.integracao.correlacao import (
    correlacionar,
)


class TestCorrelacaoM6(unittest.TestCase):

    def _investigacao(self):
        return Investigacao(
            achado=ReferenciaAchado(
                projeto="fixture",
                regra="teste",
                arquivo="x.py",
                linha=1,
                mensagem="teste",
            ),
            escopo=EscopoAutorizado(
                projeto="fixture"
            ),
        )

    def test_exige_dinamica_e_oraculo(self):
        i = self._investigacao()

        i.evidencias.extend([
            Evidencia(
                hipotese_id=i.achado.id,
                tipo=TipoEvidencia.EXECUCAO_DINAMICA,
                origem="teste",
                descricao="dinamica",
                observacao="ok",
            ),
            Evidencia(
                hipotese_id=i.achado.id,
                tipo=TipoEvidencia.ORACULO,
                origem="teste",
                descricao="oraculo",
                observacao="ok",
            ),
        ])

        c = correlacionar(i)

        self.assertTrue(
            c.possui_dinamica
        )
        self.assertTrue(
            c.possui_oraculo
        )

    def test_oraculo_sozinho_nao_tem_dinamica(self):
        i = self._investigacao()

        i.evidencias.append(
            Evidencia(
                hipotese_id=i.achado.id,
                tipo=TipoEvidencia.ORACULO,
                origem="teste",
                descricao="oraculo",
                observacao="ok",
            )
        )

        c = correlacionar(i)

        self.assertFalse(
            c.possui_dinamica
        )
        self.assertTrue(
            c.possui_oraculo
        )


if __name__ == "__main__":
    unittest.main()
