from fastapi.testclient import TestClient

from aplicacao.main import app
from aplicacao.multiagente import (
    REGISTRO_AGENTES,
)


def test_sete_agentes():
    assert REGISTRO_AGENTES.quantidade() == 7


def test_rota_oficial():
    paths = app.openapi()["paths"]
    assert "/api/interface/analisar" in paths
    assert "/api/interface/agent/analisar" not in paths


def test_controles_e_exportacao():
    paths = app.openapi()["paths"]

    for rota in (
        "/api/interface/execucao/{job_id}/pausar",
        "/api/interface/execucao/{job_id}/retomar",
        "/api/interface/execucao/{job_id}/parar",
        "/api/interface/execucao/{job_id}/resultados",
        "/api/interface/execucao/{job_id}/exportar",
    ):
        assert rota in paths


def test_interface_exportacao():
    c = TestClient(app)
    r = c.get("/interface")
    assert r.status_code == 200
    assert 'id="vs4ExportarFinal"' in r.text
    assert "window.veritasSecJobId" in r.text


def test_modulo_exportacao():
    from aplicacao.relatorios.fechamento_veritassec import (
        gerar_exportacao_operacional,
    )
    assert callable(gerar_exportacao_operacional)
