import asyncio,unittest,tempfile,pathlib,json,httpx
from aplicacao.multiagente.coleta_incremental_dast import coletar_alertas_existentes,correlacionar_e_registrar,ColetaDASTInvalida
class FakeZap:
 def __init__(self,transport):self.transport=transport;self.zap_url='http://127.0.0.1:8081'
 def _params(self,extras):return dict(extras,apikey='teste')
class TesteColetaIncrementalDAST(unittest.TestCase):
 def test_bloqueio_sem_autorizacao(self):
  with self.assertRaises(ColetaDASTInvalida):asyncio.run(coletar_alertas_existentes(FakeZap(None),'http://localhost:3000',False))
 def test_sem_acao_ativa_e_filtro_de_origem(self):
  chamadas=[]
  def responder(req):
   chamadas.append(str(req.url))
   self.assertEqual(req.url.path,'/JSON/alert/view/alerts/')
   return httpx.Response(200,json={'alerts':[{'url':'http://localhost:3000/a','pluginId':'1','method':'GET','cweid':'89'},{'url':'http://outro:3000/a','pluginId':'2'}]})
  encontrados=asyncio.run(coletar_alertas_existentes(FakeZap(httpx.MockTransport(responder)),'http://localhost:3000',True,pagina=100))
  self.assertEqual(len(encontrados),1);self.assertEqual(len(chamadas),1)
  self.assertEqual(encontrados[0]['classificacao'],'inconclusivo')
 def test_persistencia_e_correlacao(self):
  with tempfile.TemporaryDirectory() as d:
   a={'url':'http://localhost:3000/a','metodo':'GET','cwe':'89','regra':'1'}
   r=correlacionar_e_registrar(pathlib.Path(d)/'dast.json',[{'id':'x','caminho_http':'/a','metodo_http':'GET','cwe':'CWE-89'}],[a])
   self.assertEqual(r['correlacoes'],1)
   self.assertEqual(json.loads((pathlib.Path(d)/'dast.json').read_text())['correlacoes'][0]['classificacao'],'inconclusivo')
 def test_url_com_credenciais_bloqueada(self):
  with self.assertRaises(ColetaDASTInvalida):asyncio.run(coletar_alertas_existentes(FakeZap(None),'http://a:b@localhost:3000',True))
