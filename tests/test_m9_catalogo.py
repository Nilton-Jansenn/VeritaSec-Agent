import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from aplicacao.runtime.catalogo import (
    listar_vereditos,
)


class TestCatalogoM9(unittest.TestCase):

    def test_listagem(self):
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)

            pacotes = (
                raiz
                / "resultados"
                / "pacotes-veredito"
            )

            pacotes.mkdir(
                parents=True
            )

            (
                pacotes / "inv-1.json"
            ).write_text(
                json.dumps(
                    {
                        "projeto": "fixture",
                        "regra": "path",
                        "cwe": "CWE-22",
                        "estado": "confirmado",
                        "estrategia": (
                            "path_traversal"
                        ),
                        "fingerprint_achado": (
                            "fp"
                        ),
                        "evidencia_dinamica": True,
                        "evidencia_oraculo": True,
                    }
                ),
                encoding="utf-8",
            )

            with patch.dict(
                os.environ,
                {
                    "VERITASSEC_SAIDAS_DIR": td
                },
            ):
                itens = listar_vereditos()

            self.assertEqual(
                len(itens),
                1,
            )

            self.assertEqual(
                itens[0]["estado"],
                "confirmado",
            )


if __name__ == "__main__":
    unittest.main()
