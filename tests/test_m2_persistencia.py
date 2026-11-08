import tempfile
import unittest

from aplicacao.dominio.modelos import (
    EscopoAutorizado,
    EstadoInvestigacaoPersistido,
    Investigacao,
    ReferenciaAchado,
)
from aplicacao.persistencia.investigacoes import (
    RepositorioInvestigacoesJson,
)


class TestPersistencia(unittest.TestCase):

    def test_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = RepositorioInvestigacoesJson(
                tmp
            )

            inv = Investigacao(
                achado=ReferenciaAchado(
                    projeto="teste",
                    regra="regra",
                    arquivo="app.py",
                    mensagem="teste",
                ),
                escopo=EscopoAutorizado(
                    projeto="teste"
                ),
            )

            estado = EstadoInvestigacaoPersistido(
                investigacao=inv
            )

            repo.salvar(estado)

            carregado = repo.carregar(
                inv.id
            )

            self.assertEqual(
                carregado.investigacao.id,
                inv.id,
            )


if __name__ == "__main__":
    unittest.main()
