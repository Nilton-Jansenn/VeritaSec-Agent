from fastapi.testclient import TestClient

from aplicacao.main import app
from aplicacao.multiagente import (
    REGISTRO_AGENTES,
)


cliente = TestClient(
    app
)


def test_seletor_inline_presente():

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
        "__veritasSecSeletorPersistente"
        in html
    )

    assert (
        "MutationObserver"
        in html
    )

    assert (
        "vsPersistSelecionarDiretorio"
        in html
    )

    assert (
        "vsPersistSelecionarSarif"
        in html
    )


def test_assets_externos_nao_sao_referenciados():

    html = cliente.get(
        "/interface"
    ).text

    assert (
        '<script src="/interface-assets/fs.js'
        not in html
    )

    assert (
        'href="/interface-assets/fs.css'
        not in html
    )


def test_inline_esta_antes_do_fechamento_body():

    html = cliente.get(
        "/interface"
    ).text

    pos_script = html.rfind(
        'id="vsFsInlineScript"'
    )

    pos_body = html.rfind(
        "</body>"
    )

    assert pos_script > 0
    assert pos_body > pos_script


def test_probe_embutido():

    html = cliente.get(
        "/interface"
    ).text

    assert (
        "VERITASSEC_BROWSER_PROBE_JS_20261019"
        in html
    )

    assert (
        "01_CARREGADO"
        in html
    )


def test_sete_agentes():

    assert (
        REGISTRO_AGENTES.quantidade()
        == 7
    )
