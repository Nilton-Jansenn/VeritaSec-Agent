import unittest,tempfile,pathlib,json
from aplicacao.multiagente.correlacao_dast import normalizar_alerta_zap,correlacionar,registrar_resultados
class TesteCorrelacaoDAST(unittest.TestCase):
 def test_alerta_nao_e_prova(self):
  self.assertEqual(normalizar_alerta_zap({'risk':'High'})['classificacao'],'inconclusivo')
 def test_correlacao_nao_e_prova(self):
  a=normalizar_alerta_zap({'url':'http://localhost/a','method':'GET','cweid':'89'})
  c=correlacionar({'id':'x','caminho_http':'/a','metodo_http':'GET','cwe':'CWE-89'},a)
  self.assertTrue(c['correspondencia']);self.assertEqual(c['classificacao'],'inconclusivo')
 def test_sem_correlacao_nao_e_falso_positivo(self):
  c=correlacionar({'id':'x'},normalizar_alerta_zap({}))
  self.assertEqual(c['classificacao'],'inconclusivo')
 def test_artefato(self):
  with tempfile.TemporaryDirectory() as d:
   f=registrar_resultados(pathlib.Path(d)/'resultado.json',[],[])
   self.assertEqual(json.loads(f.read_text())['esquema'],'veritassec.dast.v1')
