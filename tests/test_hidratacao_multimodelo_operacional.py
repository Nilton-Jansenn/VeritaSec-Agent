import os

import pytest

import aplicacao.api.interface_agent as api


VARIAVEIS = (
    "VERITASSEC_MULTIMODELO_PAPEIS",
    "VERITASSEC_PROVEDORES_PAPEIS",
    "VERITASSEC_LOCAL_MODEL",
    "VERITASSEC_GPT_MODEL",
    "VERITASSEC_OPENAI_MODEL",
    "MODELO_OPENAI",
    "VERITASSEC_GEMINI_MODEL",
    "MODELO_GEMINI",
)


@pytest.fixture
def ambiente():

    anterior = {
        nome:
            os.environ.get(
                nome
            )
        for nome
        in VARIAVEIS
    }

    yield

    for nome, valor in anterior.items():

        if valor is None:
            os.environ.pop(
                nome,
                None,
            )
        else:
            os.environ[
                nome
            ] = valor


def test_hidratacao_tres_provedores(
    monkeypatch,
    ambiente,
):

    monkeypatch.setattr(
        api,
        "obter_config_multimodelo",
        lambda: {
            "usar_local":
                True,

            "modelo_local":
                "qwen2.5-coder:7b",

            "usar_gpt":
                True,

            "modelo_gpt":
                "gpt-4o-mini",

            "usar_gemini":
                True,

            "modelo_gemini":
                "gemini-2.5-flash",
        },
    )

    resultado = (
        api._hidratar_multimodelo_operacional()
    )

    assert (
        resultado[
            "provedores_ativos"
        ]
        == (
            "local",
            "gpt",
            "gemini",
        )
    )

    assert (
        resultado[
            "multimodelo_ativo"
        ]
        is True
    )

    assert (
        os.environ[
            "VERITASSEC_MULTIMODELO_PAPEIS"
        ]
        == "true"
    )

    assert (
        os.environ[
            "VERITASSEC_PROVEDORES_PAPEIS"
        ]
        == "local,gpt,gemini"
    )

    assert (
        os.environ[
            "VERITASSEC_LOCAL_MODEL"
        ]
        == "qwen2.5-coder:7b"
    )

    assert (
        os.environ[
            "VERITASSEC_GPT_MODEL"
        ]
        == "gpt-4o-mini"
    )

    assert (
        os.environ[
            "VERITASSEC_GEMINI_MODEL"
        ]
        == "gemini-2.5-flash"
    )


def test_caminho_nao_operacional_nao_hidrata(
    monkeypatch,
):

    chamado = {
        "hidratar":
            False,

        "historico":
            False,
    }

    def hidratar():
        chamado[
            "hidratar"
        ] = True

    def historico(payload):
        chamado[
            "historico"
        ] = True

        return {
            "ok": True
        }

    monkeypatch.setattr(
        api,
        "_hidratar_multimodelo_operacional",
        hidratar,
    )

    monkeypatch.setattr(
        api,
        "_executar_analise_sincrono_compat_passo2",
        historico,
    )

    resultado = api.executar_analise(
        {
            "operacional":
                False
        }
    )

    assert resultado == {
        "ok": True
    }

    assert (
        chamado[
            "historico"
        ]
        is True
    )

    assert (
        chamado[
            "hidratar"
        ]
        is False
    )


def test_caminho_operacional_hidrata(
    monkeypatch,
):

    chamado = {
        "hidratar":
            0,

        "iniciar":
            0,
    }

    def hidratar():

        chamado[
            "hidratar"
        ] += 1

        return {
            "provedores_ativos":
                (
                    "local",
                    "gpt",
                    "gemini",
                ),

            "multimodelo_ativo":
                True,
        }

    monkeypatch.setattr(
        api,
        "_hidratar_multimodelo_operacional",
        hidratar,
    )

    import aplicacao.multiagente.controle_execucao as controle

    def iniciar(payload):

        chamado[
            "iniciar"
        ] += 1

        return {
            "job_id":
                "TESTE",

            "estado":
                "CRIADO",
        }

    monkeypatch.setattr(
        controle,
        "iniciar_execucao",
        iniciar,
    )

    resultado = api.executar_analise(
        {
            "operacional":
                True,

            "sarif_path":
                "/tmp/teste.sarif",

            "projeto_path":
                "/tmp/projeto",
        }
    )

    assert (
        chamado[
            "hidratar"
        ]
        == 1
    )

    assert (
        chamado[
            "iniciar"
        ]
        == 1
    )

    assert isinstance(
        resultado,
        dict,
    )
