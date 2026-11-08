import ast
from pathlib import Path

from aplicacao.multiagente.raciocinio import (
    MotorRaciocinioAgno,
)
from aplicacao.multiagente.modelos import (
    PapelAgente,
)


RAC = Path(
    "aplicacao/multiagente/raciocinio.py"
)

ORQ = Path(
    "aplicacao/multiagente/orquestrador.py"
)


def test_motor_sem_supressao_multimodelo():
    texto = RAC.read_text(encoding="utf-8")

    assert (
        "AGNO_INDIVIDUAL_SUPRIMIDO_POR_MULTIMODELO"
        not in texto
    )

    assert (
        "VERITASSEC_ETAPA1_RACIOCINIO_ESPECIALIZADO"
        in texto
    )


def test_modo_multimodelo_nao_bloqueia_motor(
    monkeypatch,
):
    monkeypatch.setenv(
        "VERITASSEC_MULTIMODELO_PAPEIS",
        "true",
    )

    motor = MotorRaciocinioAgno(
        habilitada=False,
    )

    registro = motor.decidir(
        papel=PapelAgente.ANALISTA_CODIGO,
        objetivo="revisar achado",
        contexto={},
        decisao_base="Sem evidencias suficientes.",
    )

    assert registro.fallback_deterministico is True
    assert registro.chamada_modelo_realizada is False

    # A causa correta e a IA desabilitada,
    # nao uma supressao decorrente do multimodelo.
    assert registro.erro == "IA_DESABILITADA"


def test_contrato_agno_preservado():
    texto = RAC.read_text(encoding="utf-8")

    assert "agente.run(" in texto
    assert "PROVEDORES_SUPORTADOS" in texto
    assert "API_KEY_AUSENTE:" in texto

    ast.parse(texto)


def test_sete_agentes_preservados():
    texto = ORQ.read_text(encoding="utf-8")

    papeis = (
        "PapelAgente.ORQUESTRADOR",
        "PapelAgente.ANALISTA_CODIGO",
        "PapelAgente.SUPERFICIE_ATAQUE",
        "PapelAgente.HIPOTESES",
        "PapelAgente.PLANEJADOR",
        "PapelAgente.VALIDACAO",
        "PapelAgente.CRITICO",
    )

    for papel in papeis:
        assert papel in texto
