from fastapi import HTTPException
from fastapi.testclient import TestClient

from aplicacao.main import app

from aplicacao.api.interface_agent import (
    ConfigInterface,
    MODELOS_SUPORTADOS,
    salvar_config,
)

from aplicacao.multiagente.modelos_agno import (
    construir_modelo_agno,
)

from aplicacao.multiagente.raciocinio import (
    MotorRaciocinioAgno,
)


def test_catalogo_modelos():

    assert MODELOS_SUPORTADOS[
        "openai"
    ] == (
        "gpt-4o-mini",
        "gpt-5.4",
    )

    assert MODELOS_SUPORTADOS[
        "gemini"
    ] == (
        "gemini-2.5-flash",
        "gemini-3.1-pro-preview",
    )

    assert MODELOS_SUPORTADOS[
        "ollama"
    ] == (
        "qwen2.5-coder:7b",
    )


def test_modelo_incompativel_rejeitado():

    req = ConfigInterface(
        provedor="openai",
        modelo="gemini-2.5-flash",
        timeout=120,
        max_tokens=2500,
        temperatura=0.1,
    )

    try:

        salvar_config(
            req
        )

    except HTTPException as exc:

        assert (
            exc.status_code
            == 400
        )

    else:

        raise AssertionError(
            "Modelo incompatível aceito"
        )


def test_gemini_modelo_agno():

    modelo = construir_modelo_agno(
        provedor="gemini",
        modelo="gemini-2.5-flash",
        api_key="teste",
    )

    assert (
        type(modelo).__name__
        == "Gemini"
    )


def test_openai_modelo_agno():

    modelo = construir_modelo_agno(
        provedor="openai",
        modelo="gpt-4o-mini",
        api_key="teste",
    )

    assert (
        type(modelo).__name__
        == "OpenAIResponses"
    )


def test_ollama_modelo_agno():

    modelo = construir_modelo_agno(
        provedor="ollama",
        modelo="qwen2.5-coder:7b",
    )

    assert (
        type(modelo).__name__
        == "Ollama"
    )


def test_disponibilidade_provedores():

    assert MotorRaciocinioAgno(
        habilitada=True,
        provedor="gemini",
        modelo="gemini-2.5-flash",
        api_key="x",
    ).disponivel

    assert MotorRaciocinioAgno(
        habilitada=True,
        provedor="openai",
        modelo="gpt-4o-mini",
        api_key="x",
    ).disponivel

    assert MotorRaciocinioAgno(
        habilitada=True,
        provedor="ollama",
        modelo="qwen2.5-coder:7b",
    ).disponivel


def test_frontend_modelo_select():

    html = TestClient(
        app
    ).get(
        "/interface"
    ).text

    assert (
        '<select id="modelo">'
        in html
    )

    assert (
        "atualizarModelos"
        in html
    )

    assert (
        "MODELOS_DISPONIVEIS"
        in html
    )
