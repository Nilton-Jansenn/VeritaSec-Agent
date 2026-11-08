from aplicacao.multiagente.integracao_dast_pipeline import enriquecer_resultado_sarif
import pytest

def test_rejeita_resultado_invalido():
    with pytest.raises(TypeError): enriquecer_resultado_sarif(None)

def test_retorno_preserva_veredito(monkeypatch):
    import aplicacao.multiagente.execucao_dast_controlada as executor
    import aplicacao.multiagente.integracao_dast_pipeline as integracao
    monkeypatch.setattr(integracao, "_contexto_local", lambda: ("http://172.17.0.3:3000/", "chave-teste"))
    monkeypatch.setattr(executor, "executar", lambda **kw: {"acesso_confirmado": True, "zap_version": "2.17.0", "alertas_origem": 3})
    original={"veredito": "INCONCLUSIVO", "total_achados_sarif": 36}
    saida=enriquecer_resultado_sarif(original)
    assert saida["veredito"] == "INCONCLUSIVO"
    assert saida["integracao_dast"]["correlacao_sast_dast"] == "NAO_DETERMINADA"
    assert original.get("integracao_dast") is None

def test_acesso_nao_confirmado(monkeypatch):
    import aplicacao.multiagente.execucao_dast_controlada as executor
    import aplicacao.multiagente.integracao_dast_pipeline as integracao
    monkeypatch.setattr(integracao, "_contexto_local", lambda: ("http://172.17.0.3:3000/", "chave-teste"))
    monkeypatch.setattr(executor, "executar", lambda **kw: {"acesso_confirmado": False})
    with pytest.raises(RuntimeError, match="ACESSO_DAST_NAO_CONFIRMADO"):
        enriquecer_resultado_sarif({})
