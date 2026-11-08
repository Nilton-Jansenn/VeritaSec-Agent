import tempfile
import unittest
from pathlib import Path

from aplicacao.ferramentas.catalogo import CatalogoFerramentas
from aplicacao.ferramentas.codigo import (
    ErroEscopoCodigo,
    FerramentaCodigo,
)


class TestFerramentas(unittest.TestCase):

    def test_catalogo(self):
        catalogo = CatalogoFerramentas()

        self.assertIn(
            "revisao_codigo_seguro",
            catalogo.nomes(),
        )

    def test_confinamento(self):
        with tempfile.TemporaryDirectory() as tmp:
            ferramenta = FerramentaCodigo(tmp)

            with self.assertRaises(ErroEscopoCodigo):
                ferramenta.resolver(
                    "../../etc/passwd"
                )

    def test_leitura_local(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)

            (raiz / "app.py").write_text(
                "print('ok')\n",
                encoding="utf-8",
            )

            ferramenta = FerramentaCodigo(raiz)

            self.assertIn(
                "print",
                ferramenta.ler("app.py"),
            )


if __name__ == "__main__":
    unittest.main()
