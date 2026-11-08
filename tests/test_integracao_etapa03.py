from __future__ import annotations

from pathlib import Path

from aplicacao.multiagente.controle_cognitivo import (
    SolicitacaoCognitiva,
    aplicar_politica_cognitiva,
)

from aplicacao.multiagente.descoberta_autonoma import (
    descobrir_candidatos,
)

from aplicacao.multiagente.executor_estatico_seguro import (
    ExecutorFerramentasComEstaticas,
)

from aplicacao.multiagente.explicabilidade_xai import (
    anexar_explicabilidade_xai,
)


def test_alias_nao_concede_autorizacao():
    decisoes = aplicar_politica_cognitiva(
        [
            SolicitacaoCognitiva(
                agente="analista_codigo",
                capacidade="SAST",
                justificativa="teste",
            )
        ],
        capacidades_registradas={
            "busca_codigo",
            "revisao_codigo_seguro",
        },
        capacidades_autorizadas=set(),
        execucao_dinamica_permitida=False,
    )

    assert len(decisoes) == 1
    assert decisoes[0].autorizada is False


def test_capacidade_inexistente_continua_negada():
    decisoes = aplicar_politica_cognitiva(
        [
            SolicitacaoCognitiva(
                agente="planejador",
                capacidade="comando_arbitrario",
                justificativa="teste",
            )
        ],
        capacidades_registradas={"busca_codigo"},
        capacidades_autorizadas={"busca_codigo"},
        execucao_dinamica_permitida=False,
    )

    assert decisoes[0].autorizada is False


def test_executor_estatico_restringe_escopo(tmp_path):
    raiz = tmp_path / "projeto"
    raiz.mkdir()

    dentro = raiz / "exemplo.py"
    dentro.write_text(
        "print('teste')\n",
        encoding="utf-8",
    )

    fora = tmp_path / "fora.py"
    fora.write_text(
        "print('fora')\n",
        encoding="utf-8",
    )

    executor = ExecutorFerramentasComEstaticas()

    permitido = {
        "arquivo": str(dentro),
        "linha": 1,
        "metadados": {
            "projeto": str(raiz),
        },
    }

    resultado = executor.busca_codigo(
        achado=permitido,
    )

    assert resultado["executada"] is True

    proibido = {
        "arquivo": str(fora),
        "linha": 1,
        "metadados": {
            "projeto": str(raiz),
        },
    }

    try:
        executor.busca_codigo(achado=proibido)
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Leitura fora do escopo foi permitida"
        )


def test_descoberta_independente_do_sarif(tmp_path):
    fonte = tmp_path / "app.js"

    fonte.write_text(
        "const x = eval(entrada);\n",
        encoding="utf-8",
    )

    candidatos = descobrir_candidatos(
        str(tmp_path)
    )

    assert candidatos
    assert candidatos[0].id.startswith("desc-")
    assert candidatos[0].metadados[
        "confirmacao"
    ] == "NAO_CONFIRMADA"
    assert (
        candidatos[0].execucao_dinamica_permitida
        is False
    )


def test_xai_preserva_classificacao():
    original = {
        "classificacao_final": "INCONCLUSIVO",
        "veredito_multivariado": {
            "fonte_veredito": "EVIDENCIA_INSUFICIENTE"
        },
        "plano_aquisicao_evidencia": {
            "decisoes_politica": []
        },
        "aquisicao_evidencia": {
            "orcamento": {
                "acoes_executadas": 0
            },
            "resultados": [],
        },
        "trilha": [],
    }

    retorno = anexar_explicabilidade_xai(
        original
    )

    assert retorno[
        "classificacao_final"
    ] == "INCONCLUSIVO"

    assert retorno[
        "explicabilidade_xai"
    ]["regra_decisoria"] == (
        "EVIDENCIA_INSUFICIENTE"
    )
