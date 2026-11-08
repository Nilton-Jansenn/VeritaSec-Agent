import unittest

from aplicacao.dominio.enums import (
    MotivoTerminacao,
    TipoEvidencia,
    TipoVeredito,
)
from aplicacao.dominio.modelos import (
    EscopoAutorizado,
    Evidencia,
    Investigacao,
    ReferenciaAchado,
)
from aplicacao.investigacao.vereditos import (
    confirmar_explorabilidade,
    emitir_evidencia_insuficiente,
    refutar_sob_teste,
)


def investigacao_base():
    return Investigacao(
        achado=ReferenciaAchado(
            projeto="teste",
            regra="regra",
            arquivo="app.py",
            mensagem="teste",
        ),
        escopo=EscopoAutorizado(
            projeto="teste",
            ferramentas_permitidas={"sarif"},
        ),
    )


class TestVereditos(unittest.TestCase):

    def test_nao_confirma_sem_oraculo(self):
        inv = investigacao_base()

        inv.evidencias.append(
            Evidencia(
                hipotese_id="h",
                tipo=TipoEvidencia.EXECUCAO_DINAMICA,
                origem="executor",
                descricao="execução",
                observacao="teste",
            )
        )

        with self.assertRaises(ValueError):
            confirmar_explorabilidade(
                inv,
                "teste",
            )

    def test_nao_confirma_so_com_oraculo(self):
        inv = investigacao_base()

        inv.evidencias.append(
            Evidencia(
                hipotese_id="h",
                tipo=TipoEvidencia.ORACULO,
                origem="oraculo",
                descricao="oráculo",
                observacao="teste",
            )
        )

        with self.assertRaises(ValueError):
            confirmar_explorabilidade(
                inv,
                "teste",
            )

    def test_confirma_com_dinamica_e_oraculo(self):
        inv = investigacao_base()

        inv.evidencias.extend([
            Evidencia(
                hipotese_id="h",
                tipo=TipoEvidencia.EXECUCAO_DINAMICA,
                origem="executor",
                descricao="execução",
                observacao="condição alcançada",
            ),
            Evidencia(
                hipotese_id="h",
                tipo=TipoEvidencia.ORACULO,
                origem="oraculo",
                descricao="violação",
                observacao="confirmada",
            ),
        ])

        resultado = confirmar_explorabilidade(
            inv,
            "evidência reproduzível",
        )

        self.assertEqual(
            resultado.tipo,
            TipoVeredito.CONFIRMADO_EXPLORAVEL,
        )

    def test_evidencia_insuficiente(self):
        resultado = emitir_evidencia_insuficiente(
            investigacao_base(),
            MotivoTerminacao.ORCAMENTO_ESGOTADO,
            "não há evidência suficiente",
        )

        self.assertEqual(
            resultado.tipo,
            TipoVeredito.EVIDENCIA_INSUFICIENTE,
        )

        self.assertTrue(
            resultado.requer_revisao_humana
        )

    def test_refutacao_exige_condicao_testada(self):
        with self.assertRaises(ValueError):
            refutar_sob_teste(
                investigacao_base(),
                "teste",
                [],
            )

    def test_refutado_sob_teste_preserva_limite(self):
        resultado = refutar_sob_teste(
            investigacao_base(),
            "hipótese não reproduzida nas condições avaliadas",
            ["entrada A", "entrada B"],
            ["autenticação alternativa"],
        )

        self.assertEqual(
            resultado.tipo,
            TipoVeredito.REFUTADO_SOB_TESTE,
        )

        self.assertEqual(
            resultado.condicoes_nao_testadas,
            ["autenticação alternativa"],
        )


if __name__ == "__main__":
    unittest.main()
