import copy
import json

from aplicacao.multiagente.sarif_agent import (
    carregar_achados_sarif,
)

from aplicacao.multiagente.zap_sarif_vinculo import (
    autorizado,
)

from aplicacao.multiagente.politica_escopo import (
    calcular_capacidades_autorizadas,
)


def test_vinculo_get_exato_e_negacoes(
    tmp_path,
    monkeypatch,
):
    projeto = tmp_path / "projeto"
    projeto.mkdir()

    (projeto / "rotas.js").write_text(
        "app.get('/estado', (req,res) => { "
        "res.send('ok'); });\n"
        "app.post('/alterar', (req,res) => { "
        "res.send('ok'); });\n",
        encoding="utf-8",
    )

    sarif = tmp_path / "fixture.sarif"

    sarif.write_text(
        json.dumps({
            "version": "2.1.0",
            "runs": [{
                "tool": {
                    "driver": {
                        "name": "fixture-testes"
                    }
                },
                "results": [
                    {
                        "ruleId": "fixture-get",
                        "message": {
                            "text": "teste"
                        },
                        "locations": [{
                            "physicalLocation": {
                                "artifactLocation": {
                                    "uri": "rotas.js"
                                },
                                "region": {
                                    "startLine": 1
                                },
                            }
                        }],
                    },
                    {
                        "ruleId": "fixture-post",
                        "message": {
                            "text": "teste"
                        },
                        "locations": [{
                            "physicalLocation": {
                                "artifactLocation": {
                                    "uri": "rotas.js"
                                },
                                "region": {
                                    "startLine": 2
                                },
                            }
                        }],
                    },
                ],
            }],
        }),
        encoding="utf-8",
    )

    for nome, valor in {
        "VERITASSEC_RUNTIME_LOCAL": "true",
        "VERITASSEC_ZAP_HABILITADO": "true",
        "VERITASSEC_ZAP_URL":
            "http://127.0.0.1:8090",
        "VERITASSEC_RUNTIME_LOCAL_BASE_URL":
            "http://127.0.0.1:3001",
    }.items():
        monkeypatch.setenv(nome, valor)

    get, post = carregar_achados_sarif(
        str(sarif),
        str(projeto),
    )

    assert get["metodo_http"] == "GET"
    assert get["caminho_http"] == "/estado"

    # GET comprovado pelo codigo original.
    assert autorizado(get) is True

    # POST nao pode ser executado pelo accessUrl GET.
    assert autorizado(post) is False

    # Nao aceitar substituicao artificial do endpoint.
    get_caminho_falso = copy.deepcopy(get)
    get_caminho_falso["caminho_http"] = "/admin"

    assert autorizado(get_caminho_falso) is False

    # Nao aceitar substituicao artificial do metodo.
    get_metodo_falso = copy.deepcopy(get)
    get_metodo_falso["metodo_http"] = "POST"

    assert autorizado(get_metodo_falso) is False

    politica = calcular_capacidades_autorizadas(
        achado=get,
        capacidades_registradas={
            "zap",
            "runtime_http",
        },
    )

    assert "zap" in politica.capacidades_autorizadas

    monkeypatch.setenv(
        "VERITASSEC_ZAP_HABILITADO",
        "false",
    )

    assert autorizado(get) is False
