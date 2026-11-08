from unittest.mock import patch

from aplicacao.multiagente.modelos import (
    AchadoMultiagente,
)
from aplicacao.multiagente.pipeline_agent import (
    executar_pipeline_agent,
)


def test_pipeline_expoe_plano_cognitivo():
    achado = AchadoMultiagente(
        id="m20",
        regra="teste",
        mensagem="teste",
        arquivo=__file__,
        linha=1,
        execucao_dinamica_permitida=False,
    )

    resultado = executar_pipeline_agent(
        achado
    )

    assert (
        "plano_aquisicao_evidencia"
        in resultado
    )

    plano = resultado[
        "plano_aquisicao_evidencia"
    ]

    assert "hipoteses" in plano
    assert "lacunas" in plano
    assert "estrategia" in plano
    assert "decisoes_politica" in plano
