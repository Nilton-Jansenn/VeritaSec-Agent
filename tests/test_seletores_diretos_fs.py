from pathlib import Path

from fastapi.testclient import (
    TestClient,
)

from aplicacao.main import app
from aplicacao.multiagente import (
    REGISTRO_AGENTES,
)


def test_html_contem_seletor_direto():

    cliente = TestClient(
        app
    )

    resposta = cliente.get(
        "/interface"
    )

    assert resposta.status_code == 200

    html = resposta.text

    for marcador in (
        "VERITASSEC_SELETOR_FS_DIRETO_20261019",
        'id="vsFsDiretoModal"',
        'id="vsFsDiretoLista"',
        'id="vsFsDiretoSelecionarPasta"',
        "vsAbrirFs",
        "vsCarregarPasta",
        "vsDefinirValor",
        'vsAbrirFs(\n                "projeto"',
        'vsAbrirFs(\n                "sarif"',
    ):

        assert marcador in html


def test_backend_fs_real():

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

    assert isinstance(
        dados["itens"],
        list,
    )


def test_backend_fs_sarif():

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

    dados = resposta.json()

    assert isinstance(
        dados["itens"],
        list,
    )


def test_sete_agentes():

    assert (
        REGISTRO_AGENTES.quantidade()
        == 7
    )
