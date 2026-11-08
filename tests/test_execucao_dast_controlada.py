import unittest
from unittest.mock import patch

from aplicacao.multiagente.execucao_dast_controlada import (
    ExecucaoDASTInvalida,
    executar,
    validar_alvo,
    validar_zap,
)


class TesteExecucaoDASTControlada(unittest.TestCase):

    def test_alvo_privado(self):
        self.assertEqual(
            validar_alvo("http://172.17.0.3:3000/"),
            "http://172.17.0.3:3000/",
        )

    def test_alvo_publico_bloqueado(self):
        with self.assertRaises(ExecucaoDASTInvalida):
            validar_alvo("http://8.8.8.8:3000/")

    def test_zap_loopback(self):
        self.assertEqual(
            validar_zap("http://127.0.0.1:8090"),
            "http://127.0.0.1:8090",
        )

    def test_autorizacao_obrigatoria(self):
        with self.assertRaises(ExecucaoDASTInvalida):
            executar(
                zap_url="http://127.0.0.1:8090",
                alvo_url="http://172.17.0.3:3000/",
                chave_api="teste",
                autorizado=False,
            )

    @patch(
        "aplicacao.multiagente."
        "execucao_dast_controlada.chamar_api"
    )
    def test_execucao_controlada(self, chamada):
        chamada.side_effect = [
            {"version": "2.17.0"},
            {"accessUrl": ["http://172.17.0.3:3000/"]},
            {
                "alerts": [
                    {
                        "url": "http://172.17.0.3:3000/a",
                        "pluginId": "1",
                    },
                    {
                        "url": "http://outro:3000/a",
                        "pluginId": "2",
                    },
                ]
            },
        ]

        resultado = executar(
            zap_url="http://127.0.0.1:8090",
            alvo_url="http://172.17.0.3:3000/",
            chave_api="teste",
            autorizado=True,
        )

        self.assertTrue(resultado["acesso_confirmado"])
        self.assertEqual(resultado["alertas_origem"], 1)
        self.assertEqual(chamada.call_count, 3)
