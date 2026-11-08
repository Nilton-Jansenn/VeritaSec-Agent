from __future__ import annotations

import itertools

import pytest

from aplicacao.multiagente.modelos import PapelAgente
from aplicacao.multiagente.raciocinio import (
    MotorRaciocinioAgno,
)


@pytest.mark.parametrize(
    "selecionados",
    [
        combinacao
        for tamanho in (1, 2, 3)
        for combinacao in itertools.combinations(
            ("local", "gpt", "gemini"),
            tamanho,
        )
    ],
)
def test_sete_combinacoes_sem_provedores_extras(
    monkeypatch,
    selecionados,
):
    monkeypatch.setenv(
        "VERITASSEC_PROVEDORES_PAPEIS",
        ",".join(selecionados),
    )

    monkeypatch.setenv(
        "VERITASSEC_LOCAL_MODEL",
        "qwen2.5-coder:7b",
    )

    monkeypatch.setenv(
        "VERITASSEC_OPENAI_MODEL",
        "gpt-4o-mini",
    )

    monkeypatch.setenv(
        "VERITASSEC_GEMINI_MODEL",
        "gemini-2.5-flash",
    )

    monkeypatch.setenv(
        "OPENAI_API_KEY",
        "chave-ficticia",
    )

    monkeypatch.setenv(
        "GEMINI_API_KEY",
        "chave-ficticia",
    )

    monkeypatch.setenv(
        "VERITASSEC_LLAMA_BASE_URL",
        "http://127.0.0.1:8091/v1",
    )

    monkeypatch.setenv(
        "VERITASSEC_LLAMA_API_KEY",
        "chave-ficticia",
    )

    motor = MotorRaciocinioAgno(
        habilitada=True,
        provedor="gemini",
        modelo="gemini-2.5-flash",
        api_key="chave-ficticia",
    )

    equivalencia = {
        "local": "llama_cpp",
        "gpt": "openai",
        "gemini": "gemini",
    }

    permitidos = {
        equivalencia[nome]
        for nome in selecionados
    }

    for papel in PapelAgente:
        candidatos = motor._candidatos_selecionados(
            papel
        )

        obtidos = {
            provedor
            for provedor, _, _ in candidatos
        }

        assert obtidos == permitidos
        assert len(candidatos) == len(selecionados)


def test_sete_papeis_preservados():
    assert len(list(PapelAgente)) == 7


def test_contrato_local_nao_utiliza_ollama():
    from pathlib import Path

    texto = Path(
        "aplicacao/multiagente/modelos_agno.py"
    ).read_text(encoding="utf-8")

    assert 'if provedor == "llama_cpp":' in texto
    assert "OpenAIChat" in texto


def test_roteamento_nao_modifica_classificacao():
    from pathlib import Path

    texto = Path(
        "aplicacao/multiagente/raciocinio.py"
    ).read_text(encoding="utf-8")

    assert "output_schema=DecisaoAgenteLLM" in texto
    assert "agente = copy.copy(" in texto
