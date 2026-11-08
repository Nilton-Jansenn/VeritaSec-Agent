from fastapi.testclient import (
    TestClient,
)

from aplicacao.main import app


def obter_html():
    r = TestClient(app).get(
        "/interface"
    )

    assert r.status_code == 200

    return r.text


def test_renderer():
    h = obter_html()

    for token in (
        "VS_AGENT_M22C_RENDERER",
        "renderizarResultadoAgent",
        "vsAgentOperationalResults",
        "response.clone()",
    ):
        assert token in h


def test_paineis():
    h = obter_html()

    for token in (
        "Sete agentes",
        "Plano de aquisição de evidência",
        "Política de capacidades",
        "Execução e evidências",
        "Critério de parada",
    ):
        assert token in h


def test_contratos():
    h = obter_html()

    for token in (
        "plano_aquisicao_evidencia",
        "aquisicao_evidencia",
        "decisoes_politica",
        "acoes_executadas",
        "acoes_negadas",
    ):
        assert token in h


def test_rota_unica():
    h = obter_html()

    assert (
        "/api/interface/analisar"
        in h
    )

    assert (
        "/api/interface/agent/analisar"
        not in h
    )


def test_maximo_achados_removido():
    h = obter_html()

    assert (
        "maximo_achados"
        not in h
    )

    assert (
        "maxAchados"
        not in h
    )

    assert (
        "Maximo de achados"
        not in h
    )



def test_linhas_contexto_removido():
    h = obter_html()

    assert (
        "linhas_contexto"
        not in h
    )

    assert (
        'id="linhas"'
        not in h
    )

    assert (
        "Linhas de contexto"
        not in h
    )
