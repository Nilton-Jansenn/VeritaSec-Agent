from aplicacao.multiagente.controle_cognitivo import (
    aplicar_politica_cognitiva,
    extrair_solicitacoes_cognitivas,
)


def test_llm_nao_pode_inventar_shell():
    decisao = {
        "ferramentas_sugeridas": [
            "shell",
            "busca_codigo",
        ],
        "sementes": [
            "abc",
        ],
    }

    solicitacoes = (
        extrair_solicitacoes_cognitivas(
            agente="planejador",
            decisao=decisao,
        )
    )

    resultado = (
        aplicar_politica_cognitiva(
            solicitacoes,
            capacidades_registradas={
                "busca_codigo",
            },
            capacidades_autorizadas={
                "busca_codigo",
            },
            execucao_dinamica_permitida=False,
        )
    )

    por_capacidade = {
        x.capacidade: x
        for x in resultado
    }

    assert (
        por_capacidade[
            "shell"
        ].autorizada
        is False
    )

    assert (
        por_capacidade[
            "shell"
        ].motivo
        == "CAPACIDADE_FORA_DA_ALLOWLIST"
    )

    assert (
        por_capacidade[
            "busca_codigo"
        ].autorizada
        is True
    )


def test_dinamica_negada_sem_scope():
    decisao = {
        "ferramentas_sugeridas": [
            "path_traversal",
            "busca_evolucionaria",
        ],
        "sementes": [
            "../fora.txt",
        ],
    }

    solicitacoes = (
        extrair_solicitacoes_cognitivas(
            agente="planejador",
            decisao=decisao,
        )
    )

    resultado = (
        aplicar_politica_cognitiva(
            solicitacoes,
            capacidades_registradas={
                "path_traversal",
                "busca_evolucionaria",
            },
            capacidades_autorizadas={
                "path_traversal",
                "busca_evolucionaria",
            },
            execucao_dinamica_permitida=False,
        )
    )

    assert all(
        x.autorizada is False
        for x in resultado
    )

    assert all(
        x.motivo
        == "EXECUCAO_DINAMICA_NAO_AUTORIZADA"
        for x in resultado
    )


def test_dinamica_autorizada_com_scope():
    decisao = {
        "ferramentas_sugeridas": [
            "path_traversal",
            "busca_evolucionaria",
        ],
        "sementes": [
            "../fora.txt",
            "..%2ffora.txt",
        ],
    }

    solicitacoes = (
        extrair_solicitacoes_cognitivas(
            agente="planejador",
            decisao=decisao,
        )
    )

    resultado = (
        aplicar_politica_cognitiva(
            solicitacoes,
            capacidades_registradas={
                "path_traversal",
                "busca_evolucionaria",
            },
            capacidades_autorizadas={
                "path_traversal",
                "busca_evolucionaria",
            },
            execucao_dinamica_permitida=True,
        )
    )

    assert all(
        x.autorizada
        for x in resultado
    )

    assert (
        resultado[0].sementes
    )


def test_capacidade_nao_registrada_falha_fechado():
    decisao = {
        "ferramentas_sugeridas": [
            "runtime_http",
        ]
    }

    solicitacoes = (
        extrair_solicitacoes_cognitivas(
            agente="validacao",
            decisao=decisao,
        )
    )

    resultado = (
        aplicar_politica_cognitiva(
            solicitacoes,
            capacidades_registradas=set(),
            capacidades_autorizadas={
                "runtime_http",
            },
            execucao_dinamica_permitida=True,
        )
    )

    assert (
        resultado[0].autorizada
        is False
    )

    assert (
        resultado[0].motivo
        == "CAPACIDADE_NAO_REGISTRADA"
    )
