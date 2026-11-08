from __future__ import annotations

import pytest

from aplicacao.multiagente.executor_estatico_seguro import (
    ExecutorFerramentasComEstaticas,
)
from aplicacao.multiagente.aquisicao_evidencia import (
    ExecutorAquisicaoEvidencia,
)
from aplicacao.multiagente.explicabilidade_xai import (
    anexar_explicabilidade_xai,
)


def achado(raiz, arquivo):
    return {
        "id": "teste",
        "arquivo": str(arquivo),
        "linha": 1,
        "metadados": {
            "projeto": str(raiz),
        },
    }


@pytest.mark.parametrize(
    "extensao",
    [".html", ".yaml", ".yml", ".json", ".xml", ".sh"],
)
def test_extensoes_sast_autorizadas(tmp_path, extensao):
    arquivo = tmp_path / ("fonte" + extensao)
    arquivo.write_text(
        "conteudo de teste\n",
        encoding="utf-8",
    )

    executor = ExecutorFerramentasComEstaticas()

    resultado = executor.busca_codigo(
        achado=achado(tmp_path, arquivo)
    )

    assert resultado["executada"] is True
    assert resultado["confirmacao_vulnerabilidade"] is False


def test_arquivo_ausente_nao_conta_como_evidencia(tmp_path):
    executor = ExecutorFerramentasComEstaticas()

    resultado = executor.busca_codigo(
        achado=achado(
            tmp_path,
            tmp_path / "ausente.js",
        )
    )

    assert resultado["executada"] is False
    assert resultado["motivo"] == "ARQUIVO_NAO_ENCONTRADO"


def test_fora_do_projeto_continua_bloqueado(tmp_path):
    raiz = tmp_path / "projeto"
    raiz.mkdir()

    externo = tmp_path / "externo.py"
    externo.write_text("x = 1\n")

    executor = ExecutorFerramentasComEstaticas()

    with pytest.raises(ValueError):
        executor.busca_codigo(
            achado=achado(raiz, externo)
        )


def test_aquisicao_nao_contabiliza_execucao_falsa(tmp_path):
    class ExecutorNegativo:
        def busca_codigo(self, *, achado, sementes=None):
            return {
                "executada": False,
                "motivo": "ARQUIVO_NAO_ENCONTRADO",
            }

    aquisitor = ExecutorAquisicaoEvidencia(
        ExecutorNegativo()
    )

    resultado = aquisitor.executar_plano(
        achado={"id": "teste"},
        plano={
            "decisoes_politica": [{
                "capacidade": "busca_codigo",
                "autorizada": True,
                "motivo": "AUTORIZADA",
                "sementes": [],
            }]
        },
    )

    assert resultado["orcamento"]["acoes_executadas"] == 0
    assert resultado["resultados"][0]["executada"] is False


def test_xai_registra_falha_sem_reclassificar():
    resultado = {
        "classificacao_final": "INCONCLUSIVO",
        "veredito_multivariado": {
            "fonte_veredito": "EVIDENCIA_INSUFICIENTE",
        },
        "plano_aquisicao_evidencia": {
            "decisoes_politica": [],
        },
        "aquisicao_evidencia": {
            "orcamento": {
                "acoes_executadas": 0,
            },
            "resultados": [{
                "capacidade": "busca_codigo",
                "autorizada": True,
                "executada": False,
                "motivo": "ERRO_DE_EXECUCAO",
                "erro": "ValueError: exemplo",
            }],
        },
        "trilha": [],
    }

    retorno = anexar_explicabilidade_xai(resultado)

    xai = retorno["explicabilidade_xai"]

    assert retorno["classificacao_final"] == "INCONCLUSIVO"
    assert xai["aquisicao"]["resultados_nao_executados"] == 1
    assert len(xai["aquisicao"]["falhas_de_execucao"]) == 1
    assert (
        xai["aquisicao"]["falhas_de_execucao"][0]["tipo_erro"]
        == "ValueError"
    )
