from fastapi.testclient import TestClient

from aplicacao.main import app
from aplicacao.multiagente import (
    REGISTRO_AGENTES,
)


cliente = TestClient(
    app
)


def test_botoes_estao_diretamente_no_html():

    resposta = cliente.get(
        "/interface"
    )

    assert resposta.status_code == 200

    html = resposta.text


    assert (
        "VERITASSEC_BOTOES_DIRETO_HTML_RENDER_20261019"
        in html
    )


    assert (
        'class="vs-html-seletor-botao"'
        in html
    )


    assert (
        'data-vs-acao="projeto"'
        in html
    )


    assert (
        'data-vs-acao="sarif"'
        in html
    )


    assert (
        "Selecionar Diretório"
        in html
    )


    assert (
        "Selecionar SARIF"
        in html
    )


def test_input_tem_largura_limitada():

    html = cliente.get(
        "/interface"
    ).text


    assert (
        "max-width:\n        720px !important"
        in html
    )


    assert (
        "165px !important"
        in html
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


def test_sete_agentes():

    assert (
        REGISTRO_AGENTES.quantidade()
        == 7
    )
