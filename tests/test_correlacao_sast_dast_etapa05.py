from aplicacao.multiagente.correlacao_sast_dast import correlacionar

def _sarif(url='http://app.local/api/a', cwe='CWE-79', method='GET', param='q'):
    return {'runs':[{'tool':{'driver':{'rules':[{'id':'r1','properties':{'tags':[cwe]}}]}},
            'results':[{'ruleId':'r1','guid':'s1','properties':{'url':url,'method':method,'parameter':param}}]}]}

def test_confirmada():
    r=correlacionar(_sarif(),[{'id':'z1','url':'http://app.local/api/a','cweid':'79','method':'GET','param':'q'}])
    assert r['correspondencias_confirmadas']==1
    assert r['vinculos'][0]['nivel']=='CONFIRMADA'

def test_possivel_sem_metodo_ou_parametro():
    r=correlacionar(_sarif(method='',param=''),[{'id':'z1','url':'http://app.local/api/a','cweid':'79'}])
    assert r['correspondencias_possiveis']==1

def test_cwe_sem_endpoint_nao_correlaciona():
    r=correlacionar(_sarif(),[{'id':'z1','url':'http://app.local/outra','cweid':'79'}])
    assert not r['vinculos']

def test_contradicao_nao_confirma():
    r=correlacionar(_sarif(),[{'id':'z1','url':'http://app.local/api/a','cweid':'79','method':'POST','param':'q'}])
    assert r['correspondencias_confirmadas']==0
    assert r['correspondencias_possiveis']==1

def test_sarif_indisponivel_nao_inventa():
    r=correlacionar({'status':'ok'},[{'id':'z1','url':'http://app.local/api/a','cweid':'79'}])
    assert r['estado']=='SARIF_ESTRUTURADO_INDISPONIVEL'
    assert not r['vinculos']

def test_preserva_entrada():
    dados=_sarif(); original=repr(dados)
    correlacionar(dados,[])
    assert repr(dados)==original
