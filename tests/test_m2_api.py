import unittest

from fastapi import FastAPI
from fastapi.testclient import TestClient

from aplicacao.api.investigacoes import router


class TestApiM2(unittest.TestCase):

    def test_health(self):
        app = FastAPI()
        app.include_router(router)

        cliente = TestClient(app)

        resposta = cliente.get(
            "/api/v1/investigacoes/health"
        )

        self.assertEqual(
            resposta.status_code,
            200,
        )

        self.assertEqual(
            resposta.json()["status"],
            "ok",
        )


if __name__ == "__main__":
    unittest.main()
