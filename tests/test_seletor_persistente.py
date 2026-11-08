from fastapi.testclient import TestClient

from aplicacao.main import app
from aplicacao.multiagente import (
    REGISTRO_AGENTES,
)


cliente = TestClient(
    app
)


def test_javascript_persistente():

    resposta = cliente.get(
        "/interface-assets/fs.js"
    )

    assert resposta.status_code == 200

    js = resposta.text


    for marcador in (
        "__veritasSecSeletorPersistente",
        "MutationObserver",
        "vsPersistSelecionarDiretorio",
        "vsPersistSelecionarSarif",
        "Selecionar Diretório",
        "Selecionar SARIF",
        "insertAdjacentElement",
        "/api/interface/fs",
        "veritasSecAbrirProjeto",
        "veritasSecAbrirSarif",
    ):

        assert marcador in js


def test_css_persistente():

    resposta = cliente.get(
        "/interface-assets/fs.css"
    )

    assert resposta.status_code == 200

    css = resposta.text


    assert (
        "#projetoPicker"
        in css
    )

    assert (
        "#sarifPicker"
        in css
    )

    assert (
        "#vsPersistSelecionarDiretorio"
        in css
    )

    assert (
        "#vsPersistSelecionarSarif"
        in css
    )

    assert (
        "visible !important"
        in css
    )


def test_backend_fs():

    resposta = cliente.get(
        "/api/interface/fs",
        params={
            "tipo":
                "diretorio"
        },
    )

    assert resposta.status_code == 200

    dados = resposta.json()

    assert "atual" in dados
    assert "itens" in dados


def test_interface_referencia_asset():

    resposta = cliente.get(
        "/interface"
    )

    assert resposta.status_code == 200

    html = resposta.text

    assert (
        'id="vsFsInlineScript"'
        in html
    )

    assert (
        'id="vsFsInlineCss"'
        in html
    )

    assert (
        "/interface-assets/fs.js"
        not in html
    )

    assert (
        "/interface-assets/fs.css"
        not in html
    )


def test_sete_agentes():

    assert (
        REGISTRO_AGENTES.quantidade()
        == 7
    )
