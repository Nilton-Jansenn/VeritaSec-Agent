from pathlib import Path
from unittest.mock import patch

import pytest

from aplicacao.multiagente.pipeline_agent import (
    executar_pipeline_sarif_agent,
)
from aplicacao.multiagente.sarif_agent import (
    carregar_achados_sarif,
)


ROOT = Path(__file__).resolve().parents[1]

SARIF = (
    ROOT
    / "input"
    / "sarif"
    / "juiceShop_code.sarif"
)

PROJETO = (
    ROOT
    / "input"
    / "projects"
    / "juice-shop"
)


def fake(achado):
    return {
        "id": achado["id"],
        "estado_final": "INCONCLUSIVO",
    }


def test_sarif_real_36():
    achados = carregar_achados_sarif(
        str(SARIF),
        str(PROJETO),
    )

    assert len(achados) == 36


def test_limite_2():
    with patch(
        "aplicacao.multiagente.pipeline_agent."
        "executar_pipeline_agent",
        side_effect=fake,
    ) as executar:

        r = executar_pipeline_sarif_agent(
            sarif_path=str(SARIF),
            projeto_path=str(PROJETO),
            limite=2,
        )

    assert r["modo"] == "multiachado"
    assert r["total_achados_sarif"] == 36
    assert r["total_selecionado"] == 2
    assert r["total_processado"] == 2
    assert executar.call_count == 2


def test_todos_36():
    with patch(
        "aplicacao.multiagente.pipeline_agent."
        "executar_pipeline_agent",
        side_effect=fake,
    ) as executar:

        r = executar_pipeline_sarif_agent(
            sarif_path=str(SARIF),
            projeto_path=str(PROJETO),
        )

    assert r["total_processado"] == 36
    assert executar.call_count == 36


def test_individual():
    with patch(
        "aplicacao.multiagente.pipeline_agent."
        "executar_pipeline_agent",
        side_effect=fake,
    ) as executar:

        r = executar_pipeline_sarif_agent(
            sarif_path=str(SARIF),
            projeto_path=str(PROJETO),
            indice=3,
        )

    assert r["modo"] == "individual"
    assert r["achado"]["result_index"] == 3
    assert executar.call_count == 1


@pytest.mark.parametrize(
    "limite",
    [0, -1, True],
)
def test_limite_invalido(limite):
    with pytest.raises(ValueError):
        executar_pipeline_sarif_agent(
            sarif_path=str(SARIF),
            projeto_path=str(PROJETO),
            limite=limite,
        )
