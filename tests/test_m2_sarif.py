import json
import tempfile
import unittest
from pathlib import Path

from aplicacao.entrada.sarif import carregar_sarif


class TestSarif(unittest.TestCase):

    def test_carregamento(self):
        documento = {
            "version": "2.1.0",
            "runs": [{
                "results": [{
                    "ruleId": "python.path-traversal",
                    "message": {
                        "text": "Possível CWE-22"
                    },
                    "locations": [{
                        "physicalLocation": {
                            "artifactLocation": {
                                "uri": "app.py"
                            },
                            "region": {
                                "startLine": 10
                            },
                        }
                    }],
                    "properties": {
                        "tags": ["security", "CWE-22"]
                    },
                }]
            }],
        }

        with tempfile.TemporaryDirectory() as tmp:
            arquivo = Path(tmp) / "teste.sarif"

            arquivo.write_text(
                json.dumps(documento),
                encoding="utf-8",
            )

            achados = carregar_sarif(
                arquivo,
                "projeto",
            )

        self.assertEqual(len(achados), 1)
        self.assertEqual(
            achados[0].arquivo,
            "app.py",
        )
        self.assertEqual(
            achados[0].linha,
            10,
        )
        self.assertEqual(
            achados[0].cwe,
            "CWE-22",
        )
        self.assertTrue(
            achados[0].fingerprint
        )


if __name__ == "__main__":
    unittest.main()
