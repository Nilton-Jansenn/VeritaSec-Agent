from copy import deepcopy

from aplicacao.multiagente.correlacao_semantica_http import (
    comparar,
    correlacionar,
    normalizar_cwe,
    normalizar_endpoint,
)


def caso():
    return {
        "endpoint": "/api/produtos/42",
        "metodo": "GET",
        "parametro": "id",
        "cwe": "CWE-639",
    }


def test_confirmada():
    assert comparar(caso(), {
        "endpoint": "http://localhost/api/produtos/42",
        "metodo": "get",
        "parametro": "ID",
        "cwe": 639,
    })["classificacao"] == "CONFIRMADA"


def test_possivel():
    assert comparar(caso(), {
        "endpoint": "/api/produtos/42",
        "metodo": "GET",
    })["classificacao"] == "POSSIVEL"


def test_divergencia():
    assert comparar(caso(), {
        "endpoint": "/api/produtos/43",
        "metodo": "GET",
        "parametro": "id",
        "cwe": 639,
    })["classificacao"] == "NAO_DETERMINADA"


def test_sem_endpoint():
    assert comparar(
        {"cwe": 639},
        {"cwe": 639},
    )["classificacao"] == "NAO_DETERMINADA"


def test_arquivo_nao_e_endpoint():
    assert normalizar_endpoint(
        "src/controllers/produtos.js"
    ) is None


def test_cwe():
    assert normalizar_cwe("CWE-639") == "639"


def test_nao_altera_entradas():
    achados = [caso()]
    alertas = [caso()]

    original = deepcopy((achados, alertas))

    correlacionar(achados, alertas)

    assert (achados, alertas) == original


def test_contagem():
    saida = correlacionar(
        [caso(), {"cwe": 79}],
        [caso()],
    )

    assert len(saida) == 2
    assert saida[0]["classificacao"] == "CONFIRMADA"
    assert saida[1]["classificacao"] == "NAO_DETERMINADA"
