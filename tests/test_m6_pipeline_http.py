import asyncio
import tempfile
import unittest
from pathlib import Path

import httpx

from aplicacao.dominio.modelos import (
    EscopoAutorizado,
    ReferenciaAchado,
)
from aplicacao.fixtures.alvo_http import (
    criar_fixture_segura,
    criar_fixture_vulneravel,
)
from aplicacao.integracao.motor import (
    MotorIntegracaoM6,
)
from aplicacao.integracao.modelos import (
    TipoValidacaoM6,
)


class TestPipelineHttpM6(unittest.TestCase):

    @staticmethod
    async def _marcador_recurso(app) -> str:

        transport = httpx.ASGITransport(
            app=app
        )

        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://127.0.0.1",
        ) as client:

            resposta = await client.get(
                "/recurso/42",
                headers={
                    "X-Identidade": (
                        "proprietario"
                    ),
                },
            )

        if resposta.status_code != 200:
            raise AssertionError(
                "fixture não disponibilizou "
                "o recurso ao proprietário"
            )

        marcador = resposta.text.strip()

        if not marcador:
            raise AssertionError(
                "representação protegida vazia"
            )

        return marcador

    def _executar(
        self,
        app,
        esperado: bool,
    ):

        async def fluxo():

            marcador = await (
                self._marcador_recurso(
                    app
                )
            )

            with tempfile.TemporaryDirectory() as td:

                raiz = Path(td)

                projeto = raiz / "projeto"
                estado_dir = raiz / "estado"

                projeto.mkdir()

                (
                    projeto / "auth.py"
                ).write_text(
                    "def recurso():\n"
                    "    return 42\n",
                    encoding="utf-8",
                )

                motor = MotorIntegracaoM6(
                    raiz_projeto=projeto,
                    diretorio_estado=estado_dir,
                )

                estado = await motor.iniciar(
                    achado=ReferenciaAchado(
                        projeto="fixture-http",
                        regra="BOLA",
                        arquivo="auth.py",
                        linha=1,
                        cwe="CWE-639",
                        mensagem=(
                            "possible authorization "
                            "bypass"
                        ),
                    ),
                    escopo=EscopoAutorizado(
                        projeto="fixture-http",
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

                violado = await (
                    motor.validar_autorizacao_http(
                        estado=estado,
                        app=app,
                        caminho="/recurso/42",
                        marcador=marcador,
                    )
                )

                resultado = (
                    motor.consolidar(
                        estado,
                        propriedade_violada=violado,
                        validacoes=[
                            TipoValidacaoM6
                            .AUTORIZACAO_HTTP
                        ],
                    )
                )

                self.assertEqual(
                    violado,
                    esperado,
                )

                self.assertTrue(
                    resultado
                    .evidencia_dinamica
                )

                self.assertTrue(
                    resultado
                    .evidencia_oraculo
                )

                self.assertEqual(
                    resultado
                    .confirmacao_permitida,
                    esperado,
                )

                recarregado = (
                    motor.repositorio
                    .carregar(
                        estado
                        .investigacao
                        .id
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

        asyncio.run(
            fluxo()
        )

    def test_fixture_vulneravel(self):

        self._executar(
            criar_fixture_vulneravel(),
            True,
        )

    def test_fixture_segura(self):

        self._executar(
            criar_fixture_segura(),
            False,
        )


if __name__ == "__main__":
    unittest.main()
