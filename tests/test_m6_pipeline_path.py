import asyncio
import tempfile
import unittest
from pathlib import Path

from aplicacao.dominio.modelos import (
    EscopoAutorizado,
    ReferenciaAchado,
)
from aplicacao.integracao.motor import (
    MotorIntegracaoM6,
)
from aplicacao.integracao.modelos import (
    TipoValidacaoM6,
)


class TestPipelinePathM6(unittest.TestCase):

    def test_pipeline_path_traversal(self):

        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)

            projeto = raiz / "projeto"
            estado_dir = raiz / "estado"
            harness = raiz / "harness"

            projeto.mkdir()
            harness.mkdir()

            (projeto / "alvo.py").write_text(
                "def ler(caminho):\n"
                "    return caminho\n",
                encoding="utf-8",
            )

            motor = MotorIntegracaoM6(
                raiz_projeto=projeto,
                diretorio_estado=estado_dir,
            )

            estado = asyncio.run(
                motor.iniciar(
                    achado=ReferenciaAchado(
                        projeto="fixture",
                        regra="path-traversal",
                        arquivo="alvo.py",
                        linha=1,
                        cwe="CWE-22",
                        mensagem=(
                            "possible path traversal"
                        ),
                    ),
                    escopo=EscopoAutorizado(
                        projeto="fixture",
                        caminhos_permitidos=[
                            str(projeto)
                        ],
                        ferramentas_permitidas={
                            "busca_codigo",
                            "revisao_codigo_seguro",
                            "execucao_dinamica",
                        },
                        execucao_dinamica_permitida=True,
                        rede_permitida=False,
                    ),
                )
            )

            estado = (
                motor.adquirir_evidencia_estatica(
                    estado
                )
            )

            violado = (
                motor.validar_path_traversal(
                    estado,
                    harness,
                )
            )

            resultado = motor.consolidar(
                estado,
                propriedade_violada=violado,
                validacoes=[
                    TipoValidacaoM6.ESTATICA,
                    TipoValidacaoM6.PATH_TRAVERSAL,
                ],
            )

            self.assertTrue(
                resultado.evidencia_dinamica
            )
            self.assertTrue(
                resultado.evidencia_oraculo
            )
            self.assertTrue(
                resultado.propriedade_violada
            )
            self.assertTrue(
                resultado.confirmacao_permitida
            )

            recarregado = (
                motor.repositorio.carregar(
                    estado.investigacao.id
                )
            )

            self.assertGreaterEqual(
                len(
                    recarregado
                    .investigacao
                    .evidencias
                ),
                2,
            )


if __name__ == "__main__":
    unittest.main()
