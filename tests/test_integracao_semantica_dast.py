from copy import deepcopy

import pytest

from aplicacao.multiagente.integracao_semantica_dast import (
    integrar,
)


def sarif(resultado):
    return {
        "version": "2.1.0",
        "runs": [{
            "results": [resultado],
        }],
    }


def achado():
    return {
        "ruleId": "CWE-639",
        "properties": {
            "endpoint": "/api/produtos/42",
            "httpMethod": "GET",
            "parameter": "id",
            "cwe": "CWE-639",
        },
    }


def alerta():
    return {
        "url": "http://localhost/api/produtos/42",
        "method": "GET",
        "param": "id",
        "cweid": "639",
    }


def test_correspondencia_confirmada():
    r = integrar(sarif(achado()), [alerta()])
    assert r["confirmadas"] == 1


def test_correspondencia_possivel():
    a = alerta()
    a.pop("param")
    a.pop("cweid")

    r = integrar(sarif(achado()), [a])
    assert r["possiveis"] == 1


def test_endpoint_divergente():
    a = alerta()
    a["url"] = "http://localhost/api/outra-rota"

    r = integrar(sarif(achado()), [a])
    assert r["nao_determinadas"] == 1


def test_sem_atributos_http():
    r = integrar(
        sarif({"ruleId": "regra-1"}),
        [alerta()],
    )

    assert r["confirmadas"] == 0
    assert r["possiveis"] == 0


def test_preservacao_dados():
    s = sarif(achado())
    a = [alerta()]

    antes = deepcopy((s, a))

    integrar(s, a)

    assert (s, a) == antes


def test_entrada_invalida():
    with pytest.raises(TypeError):
        integrar(None, [])


def test_sem_alertas():
    r = integrar(sarif(achado()), [])

    assert r["total_sast"] == 1
    assert r["total_dast"] == 0
    assert r["nao_determinadas"] == 1
