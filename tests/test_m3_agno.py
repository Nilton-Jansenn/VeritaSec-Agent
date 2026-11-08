import asyncio
import unittest

from aplicacao.dominio.modelos import (
    DecisaoInvestigador,
    EscopoAutorizado,
    Investigacao,
    ReferenciaAchado,
)
from aplicacao.orquestracao.agno_adapter import (
    AdaptadorAgnoInvestigador,
    ErroSaidaAgente,
)


def investigacao():
    return Investigacao(
        achado=ReferenciaAchado(
            projeto="teste",
            regra="path-traversal",
            arquivo="app.py",
            linha=10,
            cwe="CWE-22",
            mensagem="possível path traversal",
        ),
        escopo=EscopoAutorizado(
            projeto="teste"
        ),
    )


class TestAgnoAdapter(unittest.TestCase):

    def test_saida_estruturada(self):
        def runner(_):
            return DecisaoInvestigador(
                tipo_hipotese="CWE-22",
                descricao_hipotese=(
                    "entrada pode escapar da raiz"
                ),
                propriedade_seguranca=(
                    "caminho deve permanecer na raiz"
                ),
                precondicoes=["entrada controlável"],
                evidencias_necessarias=[
                    "contexto",
                    "execução",
                ],
                lacunas_prioritarias=["contexto"],
                proxima_ferramenta_sugerida=(
                    "busca_codigo"
                ),
                justificativa_resumida=(
                    "requer aquisição de evidência"
                ),
                confianca=0.6,
            )

        adapter = AdaptadorAgnoInvestigador(
            runner=runner
        )

        hipotese = asyncio.run(
            adapter.formular_hipotese(
                investigacao()
            )
        )

        self.assertEqual(
            hipotese.tipo,
            "CWE-22",
        )

        self.assertEqual(
            hipotese.confianca,
            0.6,
        )

    def test_texto_livre_e_rejeitado(self):
        adapter = AdaptadorAgnoInvestigador(
            runner=lambda _: "texto livre"
        )

        with self.assertRaises(
            ErroSaidaAgente
        ):
            asyncio.run(
                adapter.formular_hipotese(
                    investigacao()
                )
            )


if __name__ == "__main__":
    unittest.main()
