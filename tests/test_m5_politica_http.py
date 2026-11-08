import unittest

from aplicacao.http_runtime.modelos import (
    AlvoHttpAutorizado,
)
from aplicacao.http_runtime.politica import (
    AlvoNaoAutorizado,
    validar_alvo,
)


class TestPoliticaHttp(unittest.TestCase):

    def test_loopback_permitido(self):
        validar_alvo(
            AlvoHttpAutorizado(
                base_url="http://127.0.0.1:9000"
            )
        )

    def test_publico_bloqueado(self):
        with self.assertRaises(
            AlvoNaoAutorizado
        ):
            validar_alvo(
                AlvoHttpAutorizado(
                    base_url="http://8.8.8.8"
                )
            )

    def test_privado_bloqueado(self):
        with self.assertRaises(
            AlvoNaoAutorizado
        ):
            validar_alvo(
                AlvoHttpAutorizado(
                    base_url="http://10.0.0.10"
                )
            )

    def test_hostname_bloqueado(self):
        with self.assertRaises(
            AlvoNaoAutorizado
        ):
            validar_alvo(
                AlvoHttpAutorizado(
                    base_url="https://example.invalid"
                )
            )


if __name__ == "__main__":
    unittest.main()
