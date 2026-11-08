from pathlib import Path
import tempfile

from aplicacao.multiagente.scr import executar_scr

from aplicacao.multiagente.oracle_adaptativo import (
    avaliar_resultado,
)


def test_scr_conservador():
    with tempfile.TemporaryDirectory() as td:
        arquivo = Path(td) / "x.js"

        arquivo.write_text(
            (
                "function x(req){"
                "const n=req.query.n;"
                "return fs.readFile(n,()=>{});"
                "}"
            ),
            encoding="utf-8",
        )

        resultado = executar_scr(
            arquivo=str(arquivo),
            linha=1,
            regra="path traversal",
            cwe="CWE-22",
        ).dump()

        assert resultado["executado"]

        assert resultado[
            "entradas_identificadas"
        ]

        assert resultado[
            "sinks_identificados"
        ]

        assert (
            "violacao_confirmada"
            not in resultado
        )


def test_oracle_sem_evidencia_fail_closed():
    resultado = avaliar_resultado(
        {
            "capacidade": "path_traversal",
            "resultado": {
                "confirmado": True
            },
        }
    )

    assert resultado["observavel"] is False
    assert resultado["violacao"] is False


def test_oracle_explicito():
    resultado = avaliar_resultado(
        {
            "capacidade": "path_traversal",
            "resultado": {
                "executada": True,
                "evidencia_dinamica": {
                    "id": "din"
                },
                "evidencia_oraculo": {
                    "id": "ora"
                },
                "violacao_confirmada": True,
            },
        }
    )

    assert resultado["observavel"] is True
    assert resultado["violacao"] is True

    assert (
        resultado["fonte_oracle"]
        == "evidencia_oraculo"
    )


def test_oracle_recursivo():
    resultado = avaliar_resultado(
        {
            "capacidade": "path_traversal",
            "resultado": {
                "oracle": {
                    "violacao_confirmada": True
                }
            },
        }
    )

    assert resultado["observavel"] is True
    assert resultado["violacao"] is True

    assert (
        resultado["fonte_oracle"]
        == "oracle_recursivo"
    )


def test_oracle_recursivo_refutado():
    resultado = avaliar_resultado(
        {
            "capacidade": "path_traversal",
            "resultado": {
                "oracle": {
                    "violacao_confirmada": False
                }
            },
        }
    )

    assert resultado["observavel"] is True
    assert resultado["violacao"] is False


def test_executada_false_tem_precedencia():
    resultado = avaliar_resultado(
        {
            "capacidade": "path_traversal",
            "resultado": {
                "executada": False,
                "oracle": {
                    "violacao_confirmada": True
                },
            },
        }
    )

    assert resultado["observavel"] is False
    assert resultado["violacao"] is False
