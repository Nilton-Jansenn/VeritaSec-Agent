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
from aplicacao.investigacao.vereditos import (
    pode_confirmar_explorabilidade,
)


class TestMetodologiaM6(unittest.TestCase):

    def _base(self):
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

    def test_dinamica_sem_oraculo_nao_confirma(self):
        i = self._base()

        i.evidencias.append(
            Evidencia(
                hipotese_id=i.achado.id,
                tipo=TipoEvidencia.EXECUCAO_DINAMICA,
                origem="teste",
                descricao="execucao",
                observacao="observada",
            )
        )

        self.assertFalse(
            pode_confirmar_explorabilidade(i)
        )

    def test_oraculo_sem_dinamica_nao_confirma(self):
        i = self._base()

        i.evidencias.append(
            Evidencia(
                hipotese_id=i.achado.id,
                tipo=TipoEvidencia.ORACULO,
                origem="teste",
                descricao="oraculo",
                observacao="violado",
            )
        )

        self.assertFalse(
            pode_confirmar_explorabilidade(i)
        )

    def test_dinamica_e_oraculo_permitem(self):
        i = self._base()

        for tipo in (
            TipoEvidencia.EXECUCAO_DINAMICA,
            TipoEvidencia.ORACULO,
        ):
            i.evidencias.append(
                Evidencia(
                    hipotese_id=i.achado.id,
                    tipo=tipo,
                    origem="teste",
                    descricao="evidencia",
                    observacao="observada",
                )
            )

        self.assertTrue(
            pode_confirmar_explorabilidade(i)
        )


if __name__ == "__main__":
    unittest.main()
