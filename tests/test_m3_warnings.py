import asyncio
import tempfile
import unittest
from pathlib import Path

from aplicacao.dominio.enums import EstadoAcao
from aplicacao.dominio.modelos import (
    EscopoAutorizado,
    ReferenciaAchado,
)
from aplicacao.investigacao.motor import MotorInvestigacao
from aplicacao.persistencia.investigacoes import (
    RepositorioInvestigacoesJson,
)


class TestWarningsM3(unittest.TestCase):

    def test_estado_acao_permanece_enum(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)

            (raiz / "app.py").write_text(
                "print('ok')\n",
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
                        regra="teste",
                        arquivo="app.py",
                        mensagem="teste",
                    ),
                    EscopoAutorizado(
                        projeto="teste",
                        ferramentas_permitidas={
                            "busca_codigo"
                        },
                    ),
                )
            )

            estado = motor.executar_proxima_acao(
                estado
            )

            acao = (
                estado.investigacao
                .plano.acoes[0]
            )

            self.assertIsInstance(
                acao.estado,
                EstadoAcao,
            )

            serializado = (
                estado.model_dump_json()
            )

            self.assertIn(
                '"executada"',
                serializado,
            )


if __name__ == "__main__":
    unittest.main()
