from aplicacao.multiagente.modelos import (
    AchadoMultiagente,
)
from aplicacao.multiagente.pipeline_agent import (
    executar_pipeline_agent,
)


def test_pipeline_expoe_aquisicao():
    achado = AchadoMultiagente(
        id="m21",
        regra="m21",
        mensagem="canario",
        arquivo=__file__,
        linha=1,
        execucao_dinamica_permitida=False,
    )

    r = executar_pipeline_agent(
        achado
    )

    assert (
        "plano_aquisicao_evidencia"
        in r
    )

    assert (
        "aquisicao_evidencia"
        in r
    )

    aq = r[
        "aquisicao_evidencia"
    ]

    assert "orcamento" in aq

    assert (
        "criterio_parada"
        in aq
    )

    assert (
        "resultados"
        in aq
    )
