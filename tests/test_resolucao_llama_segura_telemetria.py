from pathlib import Path

import pytest

from aplicacao.api.interface_agent import (
    _resolver_llama_agno,
)

from aplicacao.multiagente.modelos import (
    PapelAgente,
)


@pytest.mark.parametrize(
    "url",
    [
        "https://example.com/v1",
        "http://example.com:8000/v1",
        "http://8.8.8.8:8000/v1",
        "http://169.254.1.1:8000/v1",
        "http://127.0.0.1:8000/administracao",
        "http://usuario:senha@127.0.0.1:8000/v1",
    ],
)
def test_rejeita_endpoint_nao_autorizado(
    monkeypatch,
    url,
):
    monkeypatch.setenv(
        "VERITASSEC_LLAMA_BASE_URL",
        url,
    )

    monkeypatch.setenv(
        "VERITASSEC_LLAMA_API_KEY",
        "credencial-ficticia",
    )

    assert _resolver_llama_agno() is False


def test_sete_agentes_preservados():
    assert len(list(PapelAgente)) == 7


def test_telemetria_por_provedor():
    codigo = Path(
        "aplicacao/multiagente/raciocinio.py"
    ).read_text(encoding="utf-8")

    assert (
        "VERITASSEC_TELEMETRIA_CANDIDATO_V1"
        in codigo
    )

    assert "provedor=provedor" in codigo
