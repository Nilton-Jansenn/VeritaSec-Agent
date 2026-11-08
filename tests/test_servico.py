import unittest

from aplicacao.dominio.enums import (
    EstadoAcao,
    EstadoInvestigacao,
    TipoEvidencia,
)
from aplicacao.dominio.modelos import (
    AcaoInvestigacao,
    EscopoAutorizado,
    Evidencia,
    Investigacao,
    ReferenciaAchado,
)
from aplicacao.investigacao.servico import ServicoInvestigacao


def criar_investigacao():
    return Investigacao(
        achado=ReferenciaAchado(
            projeto="teste",
            regra="regra",
            arquivo="app.py",
            mensagem="teste",
        ),
        escopo=EscopoAutorizado(
            projeto="teste",
            ferramentas_permitidas={"sarif"},
        ),
    )


class TestServico(unittest.TestCase):

    def test_autorizacao_altera_estado(self):
        inv = criar_investigacao()

        acao = AcaoInvestigacao(
            ferramenta="sarif",
            objetivo="ler",
        )

        decisao = ServicoInvestigacao().autorizar_acao(
            inv,
            acao,
        )

        self.assertTrue(decisao.autorizada)
        self.assertEqual(
            acao.estado,
            EstadoAcao.AUTORIZADA,
        )

    def test_bloqueio_altera_estado(self):
        inv = criar_investigacao()

        acao = AcaoInvestigacao(
            ferramenta="shell",
            objetivo="executar",
        )

        decisao = ServicoInvestigacao().autorizar_acao(
            inv,
            acao,
        )

        self.assertFalse(decisao.autorizada)
        self.assertEqual(
            acao.estado,
            EstadoAcao.BLOQUEADA,
        )

    def test_registro_evidencia(self):
        inv = criar_investigacao()

        evidencia = Evidencia(
            hipotese_id="h1",
            tipo=TipoEvidencia.ESTATICA,
            origem="sarif",
            descricao="achado",
            observacao="teste",
        )

        ServicoInvestigacao().registrar_evidencia(
            inv,
            evidencia,
        )

        self.assertEqual(
            len(inv.evidencias),
            1,
        )

        self.assertEqual(
            inv.estado,
            EstadoInvestigacao.EVIDENCIA_EM_AQUISICAO,
        )


if __name__ == "__main__":
    unittest.main()
