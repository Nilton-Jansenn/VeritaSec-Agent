import os
import unittest
from unittest.mock import patch

from aplicacao.runtime.capacidades import (
    obter_capacidades,
)


class TestCapacidadesM9(unittest.TestCase):

    def test_fail_closed(self):
        with patch.dict(
            os.environ,
            {},
            clear=True,
        ):
            c = obter_capacidades()

            self.assertFalse(
                c["llm"]["habilitada"]
            )

            self.assertFalse(
                c["rede"]["publica"]
            )

            self.assertFalse(
                c["rede"]["privada"]
            )

            self.assertTrue(
                c["rede"]["loopback"]
            )

            self.assertFalse(
                c["metodologia"][
                    "llm_sozinha_confirma"
                ]
            )

            self.assertFalse(
                c["metodologia"][
                    "ground_truth_inventado"
                ]
            )


if __name__ == "__main__":
    unittest.main()
