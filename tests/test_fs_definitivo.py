from pathlib import Path

from fastapi.testclient import (
    TestClient,
)

from aplicacao.main import app
from aplicacao.multiagente import (
    REGISTRO_AGENTES,
)


def test_seletor_definitivo_no_html():

    cliente = TestClient(
        app
    )

    resposta = cliente.get(
        "/interface"
    )

    assert resposta.status_code == 200

    html = resposta.text


    for marcador in (
        "VERITASSEC_FS_DEFINITIVO_20261019",
        'id="vsFsDefModal"',
        'id="vsFsDefLista"',
        'id="vsFsDefEscolherPasta"',
        "window.veritasSecAbrirSeletor",
        "cloneNode",
        "recriarInput",
        '"projetoPicker"',
        '"sarifPicker"',
        'window.veritasSecAbrirSeletor(\n                tipo',
    ):

        assert marcador in html


def test_backend_diretorio():

    cliente = TestClient(
        app
    )

    resposta = cliente.get(
        "/api/interface/fs",
        params={
            "tipo":
                "diretorio"
        },
    )

    assert resposta.status_code == 200

    dados = resposta.json()

    assert (
        Path(
            dados["atual"]
        ).resolve()
        == Path.home().resolve()
    )


def test_backend_sarif():

    cliente = TestClient(
        app
    )

    resposta = cliente.get(
        "/api/interface/fs",
        params={
            "tipo":
                "sarif"
        },
    )

    assert resposta.status_code == 200

    assert isinstance(
        resposta.json()[
            "itens"
        ],
        list,
    )


def test_sete_agentes():

    assert (
        REGISTRO_AGENTES.quantidade()
        == 7
    )
