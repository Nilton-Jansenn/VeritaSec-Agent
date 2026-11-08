from fastapi.testclient import TestClient

from aplicacao.main import app


cliente = TestClient(
    app
)


def test_css_reserva_espaco_para_botoes():

    resposta = cliente.get(
        "/interface-assets/fs.css"
    )

    assert resposta.status_code == 200

    css = resposta.text

    assert (
        "VERITASSEC_LAYOUT_SELETORES_20261019"
        in css
    )

    assert (
        "calc(100% - 185px)"
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
        "width:\n        170px !important"
        in css
    )
