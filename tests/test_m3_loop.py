import asyncio
import tempfile
import unittest
from pathlib import Path

from aplicacao.agentes.loop import LoopInvestigacao
from aplicacao.dominio.modelos import (
    EscopoAutorizado,
    ReferenciaAchado,
)
from aplicacao.investigacao.motor import MotorInvestigacao
from aplicacao.persistencia.investigacoes import (
    RepositorioInvestigacoesJson,
)


class TestLoop(unittest.TestCase):

    def test_loop_tem_parada(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)

            (raiz / "app.py").write_text(
                """
def download(path):
    return open(path).read()
""",
                encoding="utf-8",
            )

            motor = MotorInvestigacao(
                raiz,
                RepositorioInvestigacoesJson(
                    raiz / "estado"
                ),
            )

            estado = asyncio.run(
                motor.criar(
                    ReferenciaAchado(
                        projeto="teste",
                        regra="path-traversal",
                        arquivo="app.py",
                        cwe="CWE-22",
                        mensagem="teste",
                    ),
                    EscopoAutorizado(
                        projeto="teste",
                        ferramentas_permitidas={
                            "busca_codigo",
                            "revisao_codigo_seguro",
                        },
                    ),
                )
            )

            estado, loop = LoopInvestigacao(
                motor,
                max_iteracoes=5,
            ).executar(estado)

            self.assertTrue(loop.encerrado)

            self.assertLessEqual(
                loop.iteracao,
                5,
            )

            self.assertGreaterEqual(
                estado.investigacao
                .orcamento.acoes_consumidas,
                1,
            )


if __name__ == "__main__":
    unittest.main()
