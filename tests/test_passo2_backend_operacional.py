from pathlib import Path
import json
import time

import pytest

from fastapi.testclient import (
    TestClient,
)

from aplicacao.main import app

from aplicacao.multiagente import (
    controle_execucao as controle,
)


def aguardar(
    job_id,
    estados,
    timeout=5.0,
):

    limite = (
        time.monotonic()
        + timeout
    )

    while (
        time.monotonic()
        < limite
    ):

        estado = controle.obter_execucao(
            job_id
        )

        if estado["estado"] in estados:
            return estado

        time.sleep(
            0.02
        )

    raise AssertionError(
        "Timeout aguardando estado: "
        + str(estados)
    )


def criar_sarif(
    tmp_path,
):

    projeto = (
        tmp_path
        / "projeto"
    )

    projeto.mkdir()

    alvo = (
        projeto
        / "a.py"
    )

    alvo.write_text(
        "print('x')\n",
        encoding="utf-8",
    )

    sarif = (
        tmp_path
        / "entrada.sarif"
    )

    documento = {
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "teste"
                    }
                },
                "results": [
                    {
                        "ruleId": "TESTE",
                        "message": {
                            "text": "teste"
                        },
                        "locations": [
                            {
                                "physicalLocation": {
                                    "artifactLocation": {
                                        "uri": "a.py"
                                    },
                                    "region": {
                                        "startLine": 1
                                    },
                                }
                            }
                        ],
                    }
                ],
            }
        ],
    }

    sarif.write_text(
        json.dumps(
            documento
        ),
        encoding="utf-8",
    )

    return (
        projeto,
        sarif,
    )


def test_validacao_exige_sarif(
    tmp_path,
):

    projeto = (
        tmp_path
        / "p"
    )

    projeto.mkdir()

    txt = (
        tmp_path
        / "x.txt"
    )

    txt.write_text(
        "{}",
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError
    ):
        controle.validar_entrada_operacional(
            {
                "projeto_path":
                    str(projeto),

                "sarif_path":
                    str(txt),
            }
        )


def test_rota_analise_unica():

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


def test_rotas_controle():

    paths = app.openapi()[
        "paths"
    ]

    assert (
        "/api/interface/execucao/{job_id}/pausar"
        in paths
    )

    assert (
        "/api/interface/execucao/{job_id}/retomar"
        in paths
    )

    assert (
        "/api/interface/execucao/{job_id}/parar"
        in paths
    )


def test_execucao_operacional_conclui(
    tmp_path,
    monkeypatch,
):

    projeto, sarif = (
        criar_sarif(
            tmp_path
        )
    )

    monkeypatch.setenv(
        "VERITASSEC_SAIDAS_DIR",
        str(
            tmp_path
            / "saidas"
        ),
    )

    def fake_pipeline(
        achado,
    ):
        return {
            "estado_final":
                "INCONCLUSIVO",

            "achado_id":
                (
                    achado.get("id")
                    if isinstance(
                        achado,
                        dict,
                    )
                    else getattr(
                        achado,
                        "id",
                        "X",
                    )
                ),
        }

    monkeypatch.setattr(
        controle,
        "executar_pipeline_agent",
        fake_pipeline,
    )

    criado = (
        controle.iniciar_execucao(
            {
                "projeto_path":
                    str(projeto),

                "sarif_path":
                    str(sarif),
            }
        )
    )

    estado = aguardar(
        criado["job_id"],
        {
            "CONCLUIDO",
            "ERRO",
        },
    )

    assert (
        estado["estado"]
        == "CONCLUIDO"
    )

    assert (
        estado[
            "total_processado"
        ]
        == 1
    )

    assert (
        estado[
            "progresso"
        ]["percentual"]
        == 100.0
    )

    assert Path(
        estado[
            "diretorio_execucao"
        ]
    ).is_dir()


def test_pausa_retomada_parada(
    tmp_path,
    monkeypatch,
):

    projeto, sarif = (
        criar_sarif(
            tmp_path
        )
    )

    monkeypatch.setenv(
        "VERITASSEC_SAIDAS_DIR",
        str(
            tmp_path
            / "saidas2"
        ),
    )

    def fake_carregar(
        sarif_path,
        projeto_path,
    ):
        return [
            {
                "id": f"A-{i}",
                "regra": "teste",
                "arquivo":
                    str(
                        projeto
                        / "a.py"
                    ),
                "linha": 1,
            }
            for i in range(6)
        ]

    def fake_pipeline(
        achado,
    ):
        time.sleep(
            0.08
        )

        return {
            "estado_final":
                "INCONCLUSIVO",

            "id":
                achado["id"],
        }

    monkeypatch.setattr(
        controle,
        "carregar_achados_sarif",
        fake_carregar,
    )

    monkeypatch.setattr(
        controle,
        "executar_pipeline_agent",
        fake_pipeline,
    )

    criado = (
        controle.iniciar_execucao(
            {
                "projeto_path":
                    str(projeto),

                "sarif_path":
                    str(sarif),
            }
        )
    )

    job_id = criado[
        "job_id"
    ]

    aguardar(
        job_id,
        {
            "EXECUTANDO",
        },
    )

    controle.pausar_execucao(
        job_id
    )

    estado = aguardar(
        job_id,
        {
            "PAUSADO",
        },
    )

    processado_pausa = (
        estado[
            "total_processado"
        ]
    )

    assert (
        estado[
            "pausa_solicitada"
        ]
        is True
    )

    controle.retomar_execucao(
        job_id
    )

    aguardar(
        job_id,
        {
            "EXECUTANDO",
            "CONCLUIDO",
        },
    )

    controle.parar_execucao(
        job_id
    )

    estado = aguardar(
        job_id,
        {
            "INTERROMPIDO",
            "CONCLUIDO",
        },
    )

    if (
        estado["estado"]
        == "INTERROMPIDO"
    ):
        assert (
            estado[
                "motivo_termino"
            ]
            == "INTERROMPIDO_PELO_USUARIO"
        )

    assert (
        estado[
            "total_processado"
        ]
        >= processado_pausa
    )


def test_endpoint_operacional(
    tmp_path,
    monkeypatch,
):

    projeto, sarif = (
        criar_sarif(
            tmp_path
        )
    )

    monkeypatch.setenv(
        "VERITASSEC_SAIDAS_DIR",
        str(
            tmp_path
            / "saida-api"
        ),
    )

    monkeypatch.setattr(
        controle,
        "executar_pipeline_agent",
        lambda achado: {
            "estado_final":
                "INCONCLUSIVO"
        },
    )

    c = TestClient(app)

    r = c.post(
        "/api/interface/analisar",
        json={
            "operacional": True,
            "projeto_path":
                str(projeto),
            "sarif_path":
                str(sarif),
        },
    )

    assert r.status_code == 200

    dados = r.json()

    assert (
        dados["operacional"]
        is True
    )

    assert dados["job_id"]

    s = c.get(
        "/api/interface/analisar/status/"
        + dados["job_id"]
    )

    assert s.status_code == 200
