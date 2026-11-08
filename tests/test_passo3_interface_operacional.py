from fastapi.testclient import (
    TestClient,
)

from aplicacao.main import app


def test_interface_operacional_presente():

    c = TestClient(app)

    r = c.get(
        "/interface"
    )

    assert r.status_code == 200

    html = r.text

    obrigatorios = [
        "VeritasSec-Agent",
        "Investiga",
        "agent-trace",

        'id="veritassec-passo3-root"',
        'id="vs3Projeto"',
        'id="vs3Sarif"',
        'id="vs3Executar"',
        'id="vs3Pausar"',
        'id="vs3Retomar"',
        'id="vs3Parar"',

        "Análise",
        "Resultados",
        "Evidências",
        "Gráficos",

        'id="vs3Estado"',
        'id="vs3Progresso"',
        'id="vs3Achado"',
        'id="vs3Agente"',
        'id="vs3Provedor"',
        'id="vs3Etapa"',

        "OWASP ZAP",
        "Security Oracle",

        "Local",
        "GPT",
        "Gemini",
    ]

    for item in obrigatorios:
        assert item in html, item


def test_interface_usa_backend_operacional():

    c = TestClient(app)

    html = c.get(
        "/interface"
    ).text

    assert (
        '"operacional"'
        not in html
        or "operacional" in html
    )

    assert (
        "/api/interface/analisar"
        in html
    )

    assert (
        "/api/interface/execucao/"
        in html
    )

    assert (
        "/resultados"
        in html
    )


def test_graficos_presentes():

    c = TestClient(app)

    html = c.get(
        "/interface"
    ).text

    for item in (
        "vs3GraficoVereditos",
        "vs3GraficoSeveridade",
        "vs3GraficoCwe",
        "vs3GraficoRegras",
        "vs3GraficoEvidencias",
        "vs3GraficoProvedores",
    ):
        assert item in html


def test_rota_resultados_presente():

    paths = app.openapi()[
        "paths"
    ]

    assert (
        "/api/interface/execucao/{job_id}/resultados"
        in paths
    )


def test_rota_analise_continua_unica():

    paths = app.openapi()[
        "paths"
    ]

    assert (
        "/api/interface/analisar"
        in paths
    )

    assert (
        "/api/interface/agent/analisar"
        not in paths
    )
