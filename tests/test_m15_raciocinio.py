from types import SimpleNamespace

from aplicacao.multiagente.modelos import (
    DecisaoAgenteLLM,
    PapelAgente,
)
from aplicacao.multiagente.raciocinio import (
    MotorRaciocinioAgno,
)
from aplicacao.multiagente import (
    REGISTRO_AGENTES,
)


def test_fallback_explicito_sem_ia():
    motor = MotorRaciocinioAgno(
        habilitada=False,
    )

    r = motor.decidir(
        papel=PapelAgente.HIPOTESES,
        objetivo="formular hipótese",
        contexto={},
        decisao_base="fallback",
    )

    assert (
        r.modo
        == "FALLBACK_DETERMINISTICO"
    )

    assert (
        r.chamada_modelo_realizada
        is False
    )

    assert (
        r.fallback_deterministico
        is True
    )


def test_llm_real_estruturada_mock(
    monkeypatch,
):
    agente = REGISTRO_AGENTES.obter(
        PapelAgente.HIPOTESES
    )

    def fake_run(
        input,
        **kwargs,
    ):
        assert (
            kwargs["output_schema"]
            is DecisaoAgenteLLM
        )

        return SimpleNamespace(
            content=DecisaoAgenteLLM(
                decisao=(
                    "Hipótese requer "
                    "evidência dinâmica."
                ),
                observacoes=[
                    "contexto analisado"
                ],
                ferramentas_sugeridas=[
                    "busca_codigo"
                ],
                requer_evidencia_adicional=True,
                confianca=0.75,
            )
        )

    monkeypatch.setattr(
        agente,
        "run",
        fake_run,
    )

    motor = MotorRaciocinioAgno(
        habilitada=True,
        provedor="gemini",
        modelo="gemini-2.5-flash",
        api_key="chave-de-teste",
    )

    r = motor.decidir(
        papel=PapelAgente.HIPOTESES,
        objetivo="formular hipótese",
        contexto={
            "teste": True,
        },
        decisao_base="fallback",
    )

    assert r.modo == "LLM_REAL"

    assert (
        r.chamada_modelo_realizada
        is True
    )

    assert (
        r.fallback_deterministico
        is False
    )

    assert (
        r.decisao.confianca
        == 0.75
    )


def test_llm_nao_recebe_tools():
    for agente in (
        REGISTRO_AGENTES
        .todos()
        .values()
    ):
        assert not agente.tools
