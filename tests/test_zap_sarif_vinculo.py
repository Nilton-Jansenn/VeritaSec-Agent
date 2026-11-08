from pathlib import Path

from aplicacao.multiagente.executor import (
    ExecutorFerramentas,
)

from aplicacao.multiagente.aquisicao_evidencia import (
    ExecutorAquisicaoEvidencia,
)

from aplicacao.multiagente.politica_escopo import (
    calcular_capacidades_autorizadas,
)

from aplicacao.multiagente.sarif_agent import (
    carregar_achados_sarif,
)

from aplicacao.multiagente.zap_sarif_vinculo import (
    caminho_seguro,
    procedencia_sarif,
)


def achados_reais():
    raiz = Path(__file__).resolve().parents[1]

    return carregar_achados_sarif(
        str(
            raiz / "input/sarif/juiceShop_code.sarif"
        ),
        str(
            raiz / "input/projects/juice-shop"
        ),
    )


def test_sarif_carregado():
    assert len(achados_reais()) == 36


def test_sem_achado_nega():
    resultado = ExecutorFerramentas().executar_zap(
        achado=None
    )
    assert resultado["executada"] is False


def test_sarif_sem_endpoint_nega():
    achado = achados_reais()[0]
    assert achado["caminho_http"] is None

    resultado = ExecutorFerramentas().executar_zap(
        achado=achado
    )

    assert resultado["executada"] is False


def test_sem_procedencia_nega():
    assert procedencia_sarif({
        "id": "sarif:inventado",
        "metadados": {"origem": "sarif"},
    }) is False


def test_caminhos_inseguros():
    for caminho in (
        "https://example.com",
        "//example.com",
        "/../admin",
        "/%2e%2e/admin",
        "/api?url=externa",
        "/api#fragmento",
        "/\\admin",
    ):
        assert caminho_seguro(caminho) is False


def test_caminho_local():
    assert caminho_seguro("/api/status") is True


def test_despachante_resolve_zap():
    despachante = ExecutorAquisicaoEvidencia(
        ExecutorFerramentas()
    )

    assert callable(despachante._resolver("zap"))


def test_plano_negado():
    despachante = ExecutorAquisicaoEvidencia(
        ExecutorFerramentas()
    )

    resultado = despachante.executar_plano(
        achado=achados_reais()[0],
        plano={
            "decisoes_politica": [{
                "capacidade": "zap",
                "autorizada": False,
                "motivo": "POLITICA_NEGOU",
                "sementes": [],
            }]
        },
    )

    assert resultado["resultados"][0]["executada"] is False


def test_plano_sem_endpoint_falha_fechado():
    despachante = ExecutorAquisicaoEvidencia(
        ExecutorFerramentas()
    )

    resultado = despachante.executar_plano(
        achado=achados_reais()[0],
        plano={
            "decisoes_politica": [{
                "capacidade": "zap",
                "autorizada": True,
                "motivo": "TESTE_DE_SEGURANCA",
                "sementes": [],
            }]
        },
    )

    assert resultado["resultados"][0]["executada"] is False


def test_politica_sem_endpoint():
    achado = achados_reais()[0]

    resultado = calcular_capacidades_autorizadas(
        achado=achado,
        capacidades_registradas={"zap"},
    )

    if isinstance(resultado, dict):
        autorizadas = resultado.get(
            "capacidades_autorizadas", []
        )
    else:
        autorizadas = getattr(
            resultado,
            "capacidades_autorizadas",
            [],
        )

    assert "zap" not in autorizadas
