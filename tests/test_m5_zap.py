import asyncio
import json
import unittest

import httpx

from aplicacao.http_runtime.modelos import (
    AlvoHttpAutorizado,
)
from aplicacao.integracoes.zap.cliente import (
    ClienteZap,
)


class TestZap(unittest.TestCase):

    def test_versao(self):

        async def handler(request):
            return httpx.Response(
                200,
                json={
                    "version": "fixture"
                },
            )

        async def rotina():
            cliente = ClienteZap(
                transport=httpx.MockTransport(
                    handler
                )
            )

            return await cliente.versao()

        self.assertEqual(
            asyncio.run(rotina()),
            "fixture",
        )

    def test_url_fora_escopo(self):

        async def rotina():
            cliente = ClienteZap()

            await cliente.acessar_url_autorizada(
                AlvoHttpAutorizado(
                    base_url=(
                        "http://127.0.0.1:9000"
                    )
                ),
                "http://127.0.0.1:9999/outro",
            )

        with self.assertRaises(
            PermissionError
        ):
            asyncio.run(
                rotina()
            )


if __name__ == "__main__":
    unittest.main()
