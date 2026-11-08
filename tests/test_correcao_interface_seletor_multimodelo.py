from pathlib import Path

from fastapi.testclient import TestClient

from aplicacao.main import app
from aplicacao.api.interface_agent import (
    listar_sistema_arquivos,
)


def test_rotas_novas():

    paths = app.openapi()["paths"]

    assert "/api/interface/fs" in paths
    assert "/api/interface/config-multimodelo" in paths


def test_navegacao_home():

    dados = listar_sistema_arquivos(
        path=str(Path.home()),
        tipo="diretorio",
    )

    assert dados["atual"] == str(
        Path.home().resolve()
    )

    assert isinstance(
        dados["itens"],
        list,
    )


def test_interface_tem_seletores():

    c = TestClient(app)
    r = c.get("/interface")

    assert r.status_code == 200

    for marcador in (
        'id="btnSelecionarProjeto"',
        'id="btnSelecionarSarif"',
        'id="projetoPicker"',
        'id="sarifPicker"',
        'id="mmLocal"',
        'id="mmGpt"',
        'id="mmGemini"',
        'id="mmModeloLocal"',
        'id="mmModeloGpt"',
        'id="mmModeloGemini"',
        'id="mmSalvar"',
    ):
        assert marcador in r.text


def test_sete_agentes_preservados():

    from aplicacao.multiagente import (
        REGISTRO_AGENTES,
    )

    assert REGISTRO_AGENTES.quantidade() == 7
