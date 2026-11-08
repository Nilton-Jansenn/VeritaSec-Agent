from aplicacao.multiagente import painel_papeis
from aplicacao.api.interface_agent import (
    _resolver_llama_agno,
)


def test_painel_nao_duplica_inferencia(monkeypatch):
    monkeypatch.setenv(
        "VERITASSEC_PROVEDORES_PAPEIS",
        "local,gpt,gemini",
    )

    monkeypatch.setenv(
        "IA_HABILITADA",
        "true",
    )

    monkeypatch.setenv(
        "VERITASSEC_MULTIMODELO_PAPEIS",
        "true",
    )

    assert painel_papeis.habilitado() is False


def test_painel_legado_preservado(monkeypatch):
    monkeypatch.delenv(
        "VERITASSEC_PROVEDORES_PAPEIS",
        raising=False,
    )

    monkeypatch.setenv(
        "VERITASSEC_MULTIMODELO_PAPEIS",
        "true",
    )

    assert painel_papeis.habilitado() is True


def test_local_usa_credencial_configurada(monkeypatch):
    monkeypatch.setenv(
        "VERITASSEC_LLAMA_BASE_URL",
        "http://127.0.0.1:12345",
    )

    monkeypatch.setenv(
        "VERITASSEC_LLAMA_API_KEY",
        "credencial-ficticia-teste",
    )

    assert _resolver_llama_agno() is True


def test_local_rejeita_endpoint_remoto(monkeypatch):
    monkeypatch.setenv(
        "VERITASSEC_LLAMA_BASE_URL",
        "https://example.com/v1",
    )

    monkeypatch.setenv(
        "VERITASSEC_LLAMA_API_KEY",
        "credencial-ficticia-teste",
    )

    assert _resolver_llama_agno() is False
