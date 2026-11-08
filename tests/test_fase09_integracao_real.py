import json
from copy import deepcopy
from unittest.mock import patch

from aplicacao.multiagente import integracao_dast_pipeline as modulo


def _sarif():
    return {
        "version": "2.1.0",
        "runs": [{
            "tool": {"driver": {"name": "Teste"}},
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


def test_preserva_resultado_sem_sarif():
    original = {
        "veredito": "INCONCLUSIVO",
        "total_achados_sarif": 36,
    }

    with patch.object(
        modulo,
        "_vs_etapa05_enriquecer_original",
        return_value={"integracao_dast": {}},
    ):
        saida = modulo.enriquecer_resultado_sarif(original)

    assert "correlacao_sast_dast" in saida
    assert "correlacao_semantica_http" not in saida
    assert original["veredito"] == "INCONCLUSIVO"


def test_integracao_semantica_com_sarif():
    sarif = _sarif()
    original = deepcopy(sarif)

    alertas = [{
        "url": "http://alvo.local/api/produtos/42",
        "method": "GET",
        "param": "id",
        "cweid": "639",
    }]

    class Resposta:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self, limite):
            return json.dumps({"alerts": alertas}).encode()

    with (
        patch.object(
            modulo,
            "_vs_etapa05_enriquecer_original",
            return_value={"integracao_dast": {}},
        ),
        patch.object(
            modulo,
            "_contexto_local",
            return_value=("http://alvo.local/", "chave-ficticia"),
        ),
        patch(
            "urllib.request.urlopen",
            return_value=Resposta(),
        ),
    ):
        saida = modulo.enriquecer_resultado_sarif(sarif)

    assert "correlacao_sast_dast" in saida
    assert "correlacao_semantica_http" in saida

    resultado = saida["correlacao_semantica_http"]

    assert resultado["total_sast"] == 1
    assert resultado["total_dast"] == 1
    assert resultado["confirmadas"] == 1
    assert resultado["vereditos_llm_modificados"] is False

    assert sarif == original
