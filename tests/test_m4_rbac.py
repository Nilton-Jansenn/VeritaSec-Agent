import unittest

from aplicacao.autorizacao.rbac import (
    Papel,
    Permissao,
    autorizado,
    exigir,
)


class TestRbac(
    unittest.TestCase
):

    def test_admin_configura(
        self,
    ):
        self.assertTrue(
            autorizado(
                Papel.ADMINISTRADOR,
                Permissao.CONFIGURAR_SISTEMA,
            )
        )

    def test_avaliador_nao_configura(
        self,
    ):
        self.assertFalse(
            autorizado(
                Papel.AVALIADOR,
                Permissao.CONFIGURAR_SISTEMA,
            )
        )

    def test_avaliador_executa_validacao(
        self,
    ):
        self.assertTrue(
            autorizado(
                Papel.AVALIADOR,
                Permissao.EXECUTAR_VALIDACAO,
            )
        )

    def test_exigir_bloqueia(
        self,
    ):
        with self.assertRaises(
            PermissionError
        ):
            exigir(
                Papel.AVALIADOR,
                Permissao.GERENCIAR_USUARIOS,
            )


if __name__ == "__main__":
    unittest.main()
