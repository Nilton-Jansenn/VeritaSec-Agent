from __future__ import annotations

import ast
from pathlib import Path
from types import SimpleNamespace

from aplicacao.multiagente import modelos_agno
from aplicacao.multiagente import raciocinio
from aplicacao.multiagente.modelos import (
    DecisaoAgenteLLM,
    PapelAgente,
)


def test_gemini_25_flash_desabilita_thinking(
    monkeypatch,
):
    import agno.models.google

    capturado = {}

    class GeminiFalso:
        def __init__(self, **kwargs):
            capturado.update(kwargs)

    monkeypatch.setattr(
        agno.models.google,
        "Gemini",
        GeminiFalso,
    )

    modelos_agno.construir_modelo_agno(
        provedor="gemini",
        modelo="gemini-2.5-flash",
        api_key="chave-ficticia",
        max_tokens=4096,
        timeout=10,
    )

    assert capturado["thinking_budget"] == 0
    assert capturado["max_output_tokens"] == 4096


def test_thinking_nao_aplicado_a_outros_modelos(
    monkeypatch,
):
    import agno.models.google

    capturado = {}

    class GeminiFalso:
        def __init__(self, **kwargs):
            capturado.update(kwargs)

    monkeypatch.setattr(
        agno.models.google,
        "Gemini",
        GeminiFalso,
    )

    modelos_agno.construir_modelo_agno(
        provedor="gemini",
        modelo="gemini-2.5-pro",
        api_key="chave-ficticia",
    )

    assert "thinking_budget" not in capturado


def test_motor_nao_modifica_agente_compartilhado(
    monkeypatch,
):
    agente_global = SimpleNamespace(
        model="modelo-original"
    )

    def executar(input, **kwargs):
        assert (
            kwargs["output_schema"]
            is DecisaoAgenteLLM
        )

        return SimpleNamespace(
            content=DecisaoAgenteLLM(
                decisao="Solicitar evidencias",
                observacoes=["Sem confirmacao"],
                confianca=0.5,
            )
        )

    agente_global.run = executar

    monkeypatch.setattr(
        raciocinio.REGISTRO_AGENTES,
        "obter",
        lambda papel: agente_global,
    )

    monkeypatch.setattr(
        raciocinio,
        "construir_modelo_agno",
        lambda **kwargs: "modelo-teste",
    )

    motor = raciocinio.MotorRaciocinioAgno(
        habilitada=True,
        provedor="gemini",
        modelo="gemini-2.5-flash",
        api_key="chave-ficticia",
    )

    resultado = motor.decidir(
        papel=PapelAgente.HIPOTESES,
        objetivo="Avaliar hipotese",
        contexto={},
        decisao_base="Sem evidencia",
    )

    assert resultado.modo == "LLM_REAL"

    # Modelo original do agente compartilhado
    # nao deve ser substituido.
    assert agente_global.model == "modelo-original"


def test_contrato_validacao_estruturada():
    arquivo = Path(raciocinio.__file__)
    codigo = arquivo.read_text(encoding="utf-8")

    ast.parse(codigo)

    assert "output_schema=DecisaoAgenteLLM" in codigo
    assert "agente = copy.copy(" in codigo
    assert '"formato_resposta"' in codigo
