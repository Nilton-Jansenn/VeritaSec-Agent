import unittest
from aplicacao.multiagente.contrato_dast import validar_configuracao_dast, ConfiguracaoDASTInvalida

class TesteContratoDAST(unittest.TestCase):
    def test_desabilitado_nao_requer_runtime(self):
        x=validar_configuracao_dast(False,None,False)
        self.assertFalse(x.habilitado)
        self.assertIsNone(x.url_base)
    def test_url_valida_autorizada(self):
        x=validar_configuracao_dast(True,'http://127.0.0.1:3000/',True)
        self.assertEqual(x.url_base,'http://127.0.0.1:3000')
    def test_autorizacao_obrigatoria(self):
        with self.assertRaises(ConfiguracaoDASTInvalida):
            validar_configuracao_dast(True,'http://127.0.0.1:3000',False)
    def test_credenciais_na_url_bloqueadas(self):
        with self.assertRaises(ConfiguracaoDASTInvalida):
            validar_configuracao_dast(True,'http://user:pass@127.0.0.1:3000',True)
    def test_esquema_nao_http_bloqueado(self):
        with self.assertRaises(ConfiguracaoDASTInvalida):
            validar_configuracao_dast(True,'file:///etc/passwd',True)
    def test_caminho_na_url_base_bloqueado(self):
        with self.assertRaises(ConfiguracaoDASTInvalida):
            validar_configuracao_dast(True,'http://127.0.0.1:3000/admin',True)

if __name__ == '__main__':
    unittest.main()
