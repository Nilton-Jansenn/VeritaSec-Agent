from fastapi.testclient import TestClient

from aplicacao.main import app
from aplicacao.multiagente import (
    REGISTRO_AGENTES,
)


def test_status_ia_nao_expoe_segredo(
    monkeypatch,
):
    monkeypatch.setenv(
        "GEMINI_API_KEY",
        "segredo-que-nao-pode-aparecer",
    )

    c = TestClient(app)

    r = c.get(
        "/api/interface/status-ia"
    )

    assert r.status_code == 200

    d = r.json()

    serializado = str(d)

    assert (
        "segredo-que-nao-pode-aparecer"
        not in serializado
    )

    assert (
        d["segredo_exposto"]
        is False
    )

    assert (
        d["api_key_configurada"]
        is True
    )


def test_sete_agentes_sem_tools_diretas():
    agentes = (
        REGISTRO_AGENTES
        .todos()
    )

    assert len(agentes) == 7

    for agente in agentes.values():
        assert not agente.tools


def test_openapi_status_e_entrada_unica():
    paths = app.openapi()["paths"]

    assert (
        "/api/interface/status-ia"
        in paths
    )

    assert (
        "/api/interface/analisar"
        in paths
    )

    assert (
        "/api/interface/agent/analisar"
        not in paths
    )


def test_interface_exibe_prova_llm():
    c = TestClient(app)

    r = c.get("/interface")

    assert r.status_code == 200

    assert (
        "llm-proof-panel"
        in r.text
    )

    assert (
        "chamadas LLM reais"
        in r.text
    )
