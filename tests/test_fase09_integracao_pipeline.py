from copy import deepcopy

from aplicacao.multiagente.pipeline_agent import (
    executar_correlacao_semantica,
)


def test_integracao_confirmada():
    sarif = {
        "version": "2.1.0",
        "runs": [{
            "results": [{
                "ruleId": "CWE-639",
                "properties": {
                    "endpoint": "/api/produtos/42",
                    "httpMethod": "GET",
                    "parameter": "id",
                    "cwe": "CWE-639",
                },
            }],
        }],
    }

    alertas = [{
        "url": "http://localhost/api/produtos/42",
        "method": "GET",
        "param": "id",
        "cweid": "639",
    }]

    original = deepcopy((sarif, alertas))

    resultado = executar_correlacao_semantica(
        sarif,
        alertas,
    )

    assert resultado["confirmadas"] == 1
    assert resultado["total_sast"] == 1
    assert resultado["total_dast"] == 1
    assert (sarif, alertas) == original


def test_sem_correspondencia():
    sarif = {
        "version": "2.1.0",
        "runs": [{
            "results": [{
                "ruleId": "regra-1",
            }],
        }],
    }

    alertas = [{
        "url": "http://localhost/api/teste",
        "method": "GET",
        "cweid": "79",
    }]

    resultado = executar_correlacao_semantica(
        sarif,
        alertas,
    )

    assert resultado["confirmadas"] == 0
    assert resultado["possiveis"] == 0
    assert resultado["nao_determinadas"] == 1
