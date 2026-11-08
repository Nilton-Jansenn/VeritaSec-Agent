import asyncio
import unittest

import httpx

from aplicacao.fixtures.alvo_http import (
    criar_fixture_segura,
    criar_fixture_vulneravel,
)
from aplicacao.http_runtime.executor import (
    ExecutorHttpControlado,
)
from aplicacao.http_runtime.modelos import (
    AlvoHttpAutorizado,
)
from aplicacao.http_runtime.validador_autorizacao import (
    ValidadorAutorizacaoHttp,
)


class TestAutorizacaoHttp(unittest.TestCase):

    def _executar(
        self,
        app,
    ):
        async def rotina():

            transport = httpx.ASGITransport(
                app=app
            )

            executor = ExecutorHttpControlado(
                alvo=AlvoHttpAutorizado(
                    base_url="http://127.0.0.1"
                ),
                transport=transport,
            )

            return await (
                ValidadorAutorizacaoHttp(
                    executor
                ).validar(
                    caminho="/recurso/42",
                    marcador=(
                        "RECURSO_PROTEGIDO_42"
                    ),
                )
            )

        return asyncio.run(
            rotina()
        )

    def test_fixture_segura(self):
        resultado = self._executar(
            criar_fixture_segura()
        )

        self.assertFalse(
            resultado.violado
        )

    def test_fixture_vulneravel(self):
        resultado = self._executar(
            criar_fixture_vulneravel()
        )

        self.assertTrue(
            resultado.violado
        )


if __name__ == "__main__":
    unittest.main()
