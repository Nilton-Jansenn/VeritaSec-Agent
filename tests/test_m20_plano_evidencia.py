from aplicacao.multiagente.plano_evidencia import (
    construir_plano_aquisicao,
)


def test_plano_causal_tipado():
    decisoes = [
        (
            "hipoteses",
            {
                "hipotese_causal":
                    "entrada alcança sink de arquivo",
                "lacunas_evidencia": [
                    "confirmar acesso fora da raiz",
                ],
            },
        ),
        (
            "planejador",
            {
                "estrategia_validacao":
                    "usar sandbox controlado",
                "ferramentas_sugeridas": [
                    "busca_evolucionaria",
                    "path_traversal",
                ],
                "sementes": [
                    "../fora.txt",
                ],
            },
        ),
    ]

    plano = construir_plano_aquisicao(
        decisoes_por_agente=decisoes,
        capacidades_registradas={
            "busca_evolucionaria",
            "path_traversal",
        },
        capacidades_autorizadas={
            "busca_evolucionaria",
            "path_traversal",
        },
        execucao_dinamica_permitida=True,
    )

    dados = plano.model_dump()

    assert dados["hipoteses"]
    assert dados["lacunas"]
    assert dados["estrategia"]

    assert len(
        dados["decisoes_politica"]
    ) == 2

    assert all(
        x["autorizada"]
        for x in
        dados["decisoes_politica"]
    )
