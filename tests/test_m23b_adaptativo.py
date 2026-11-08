from pathlib import Path
import tempfile

from aplicacao.multiagente.ciclo_adaptativo import (
    CicloAdaptativoInvestigacao,
)
from aplicacao.multiagente.correlacao import (
    correlacionar_evidencias,
)
from aplicacao.multiagente.executor_adaptativo import (
    ExecutorAdaptativo,
)
from aplicacao.multiagente.oracle_adaptativo import (
    avaliar_resultado,
)


def test_feedback_adaptativo():
    chamadas = 0

    def planejar(ctx):
        nonlocal chamadas
        chamadas += 1

        if chamadas == 1:
            return {
                "hipoteses": ["h1"],
                "lacunas": ["reproducao"],
                "estrategia": "seed inicial",
                "sementes": ["x"],
                "capacidades": ["path_traversal"],
            }

        assert "evidencias_adquiridas" in ctx

        return {
            "hipoteses": ["h2"],
            "lacunas": [],
            "estrategia": "refinar",
            "sementes": ["../fora.txt"],
            "capacidades": ["path_traversal"],
        }

    def autorizar(_):
        return {
            "capacidades_autorizadas": [
                "path_traversal"
            ]
        }

    def executar(p):
        seed = p["sementes"][0]
        return {
            "entrada": seed,
            "confirmado": seed == "../fora.txt",
        }

    def oracle(p):
        return {
            "observavel": True,
            "violacao": bool(
                p["resultado"]["confirmado"]
            ),
            "hash_evidencia": "x",
        }

    r = CicloAdaptativoInvestigacao(
        planejar=planejar,
        autorizar=autorizar,
        executar=executar,
        avaliar_oraculo=oracle,
        max_rodadas=3,
        max_acoes=4,
    ).executar({})

    assert len(r.rodadas) == 2
    assert r.evidencia_confirmatoria
    assert (
        r.criterio_parada
        == "EVIDENCIA_SUFICIENTE_CONFIRMADA"
    )


def test_orcamento():
    r = CicloAdaptativoInvestigacao(
        planejar=lambda _: {
            "capacidades": ["path_traversal"]
        },
        autorizar=lambda _: {
            "capacidades_autorizadas": [
                "path_traversal"
            ]
        },
        executar=lambda _: {
            "confirmado": False
        },
        avaliar_oraculo=lambda _: {
            "observavel": True,
            "violacao": False,
        },
        max_rodadas=10,
        max_acoes=2,
    ).executar({})

    assert r.orcamento.acoes_executadas == 2
    assert r.criterio_parada == "ORCAMENTO_ESGOTADO"


def test_fail_closed():
    executou = False

    def executar(_):
        nonlocal executou
        executou = True
        return {}

    r = CicloAdaptativoInvestigacao(
        planejar=lambda _: {
            "capacidades": ["path_traversal"]
        },
        autorizar=lambda _: {
            "capacidades_autorizadas": [],
            "criterio": "ACAO_NAO_AUTORIZADA",
        },
        executar=executar,
        avaliar_oraculo=lambda _: {},
    ).executar({})

    assert executou is False
    assert r.criterio_parada == "ACAO_NAO_AUTORIZADA"


def test_llm_sem_dinamica_nao_confirma():
    r = correlacionar_evidencias(
        evidencia_estatica=True,
        plausibilidade_semantica=True,
        evidencia_dinamica=False,
        violacao_oraculo=False,
        reproduzivel=False,
    )

    assert r.estado == "PLAUSIVEL_SEMANTICAMENTE"


def test_oracle_dinamico_confirma():
    r = correlacionar_evidencias(
        evidencia_estatica=True,
        plausibilidade_semantica=True,
        evidencia_dinamica=True,
        violacao_oraculo=True,
        reproduzivel=True,
    )

    assert r.estado == "REPRODUZIDO_DINAMICAMENTE"


def test_shell_nao_executavel():
    r = ExecutorAdaptativo().executar(
        {
            "capacidade": "shell",
            "contexto": {},
            "sementes": [],
        }
    )

    assert r["executada"] is False
    assert r["motivo"] == "CAPACIDADE_NAO_IMPLEMENTADA"


def test_oracle_recursivo():
    r = avaliar_resultado(
        {
            "capacidade": "path_traversal",
            "resultado": {
                "oracle": {
                    "violacao_confirmada": True
                }
            },
        }
    )

    assert r["observavel"] is True
    assert r["violacao"] is True


def test_executor_real_controlado():
    with tempfile.TemporaryDirectory() as td:

        raiz = Path(td) / "sandbox"
        raiz.mkdir()

        fora = Path(td) / "fora.txt"
        fora.write_text(
            "M23B",
            encoding="utf-8",
        )

        r = ExecutorAdaptativo().executar(
            {
                "capacidade": "path_traversal",
                "sementes": ["../fora.txt"],
                "contexto": {
                    "raiz_sandbox": str(raiz),
                    "hipotese_id": "m23b",
                    "max_geracoes": 2,
                },
            }
        )

        assert isinstance(r, dict)

        o = avaliar_resultado(
            {
                "capacidade": "path_traversal",
                "resultado": r,
            }
        )

        assert o["observavel"] is True
        assert o["hash_evidencia"]
