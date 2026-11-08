import os
import unittest
from unittest.mock import patch

from aplicacao.runtime.configuracao import (
    carregar_configuracao_runtime,
)


class TestRuntimeM9(unittest.TestCase):

    def test_offline_por_padrao(self):
        with patch.dict(
            os.environ,
            {},
            clear=True,
        ):
            cfg = (
                carregar_configuracao_runtime()
            )

            self.assertFalse(
                cfg.ia_habilitada
            )

            self.assertFalse(
                cfg.zap_habilitado
            )

            self.assertFalse(
                cfg.permitir_rede_publica
            )

            self.assertFalse(
                cfg.permitir_rede_privada
            )

    def test_ia_exige_modelo(self):
        with patch.dict(
            os.environ,
            {
                "IA_HABILITADA": "true",
            },
            clear=True,
        ):
            with self.assertRaises(
                ValueError
            ):
                carregar_configuracao_runtime()

    def test_ia_configurada(self):
        with patch.dict(
            os.environ,
            {
                "IA_HABILITADA": "true",
                "VERITASSEC_LLM_PROVIDER": (
                    "openai"
                ),
                "VERITASSEC_LLM_MODEL": (
                    "modelo-teste"
                ),
            },
            clear=True,
        ):
            cfg = (
                carregar_configuracao_runtime()
            )

            self.assertTrue(
                cfg.ia_habilitada
            )

            self.assertEqual(
                cfg.provedor_llm,
                "openai",
            )

            self.assertEqual(
                cfg.modelo_llm,
                "modelo-teste",
            )


if __name__ == "__main__":
    unittest.main()
