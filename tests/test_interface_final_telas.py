from fastapi.testclient import TestClient

from aplicacao.main import app
from aplicacao.multiagente import (
    REGISTRO_AGENTES,
)


def html_interface():

    cliente = TestClient(
        app
    )

    resposta = cliente.get(
        "/interface"
    )

    assert resposta.status_code == 200

    return resposta.text


def test_interface_tem_telas_reais():

    html = html_interface()

    assert (
        "<!-- VERITASSEC_INTERFACE_TELAS_REAIS_20261019 -->"
        in html
    )

    assert (
        'id="vsTelasReaisScript"'
        in html
    )

    assert (
        '"Configuração"'
        in html
    )

    assert (
        '"Análise"'
        in html
    )

    assert (
        '"Resultados"'
        in html
    )

    assert (
        '"Evidências"'
        in html
    )

    assert (
        '"Gráficos"'
        in html
    )

    assert (
        '"VeritasSec-Agent"'
        in html
    )

    assert (
        "vsTelaEvidencias"
        in html
    )

    assert (
        "vsTelaGraficos"
        in html
    )

    assert (
        "vs-tab-principal"
        in html
    )

    assert (
        "vs-tela-principal"
        in html
    )


def test_botoes_internos_deixam_de_ser_navegacao():

    html = html_interface()

    assert (
        "vs-nav-interna-legada"
        in html
    )

    assert (
        "ocultarNavegacaoInterna"
        in html
    )

    assert (
        "tela.appendChild("
        in html
    )

    assert (
        "clicarModoInterno"
        in html
    )


def test_seletor_projeto_e_sarif():

    html = html_interface()

    assert (
        'id="projetoPicker"'
        in html
    )

    assert (
        'id="sarifPicker"'
        in html
    )

    assert (
        'id="btnSelecionarProjeto"'
        in html
    )

    assert (
        'id="btnSelecionarSarif"'
        in html
    )

    assert (
        "btnProjeto.click()"
        in html
    )

    assert (
        "btnSarif.click()"
        in html
    )


def test_multimodelo_unico():

    html = html_interface()

    assert (
        "vsMmConfig"
        in html
    )

    assert (
        "mmLocal"
        in html
    )

    assert (
        "mmGpt"
        in html
    )

    assert (
        "mmGemini"
        in html
    )

    assert (
        "#config > .grid"
        in html
    )


def test_sete_agentes_preservados():

    assert (
        REGISTRO_AGENTES.quantidade()
        == 7
    )


def test_rotas_preservadas():

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

    assert (
        "/api/interface/fs"
        in paths
    )

    assert (
        "/api/interface/config-multimodelo"
        in paths
    )
