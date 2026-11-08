import json

from aplicacao.llm import (
    Evidencia,
    RespostaLLM,
    SolicitacaoLLM,
    criar_gestor_padrao,
    criar_registro_provedores,
)

from aplicacao.llm.multimodelo import (
    PainelMultimodelo,
    construir_evidencias_cegas,
)

from aplicacao.llm.provedores import (
    ProvedorCallable,
)


def _callback(
    nome,
    veredito,
):
    contador = {
        "n": 0
    }

    def fn(
        solicitacao:
            SolicitacaoLLM,
    ):
        contador["n"] += 1

        if contador["n"] == 1:
            data = {
                "veredito":
                    veredito,

                "confianca":
                    0.8,

                "justificativa":
                    "parecer",

                "lacunas":
                    [],
            }
        else:
            data = {
                "veredito":
                    veredito,

                "mantem":
                    True,

                "observacao":
                    "critica",
            }

        return RespostaLLM(
            texto=json.dumps(
                data
            ),
            provedor=nome,
            modelo="fake",
        )

    return fn


def _painel(
    local,
    gpt,
    gemini,
):

    registro = criar_registro_provedores(
        local=ProvedorCallable(
            "local",
            "fake",
            _callback(
                "local",
                local,
            ),
            escopo="local",
        ),

        gpt=ProvedorCallable(
            "gpt",
            "fake",
            _callback(
                "gpt",
                gpt,
            ),
            escopo="externo",
        ),

        gemini=ProvedorCallable(
            "gemini",
            "fake",
            _callback(
                "gemini",
                gemini,
            ),
            escopo="externo",
        ),
    )

    return PainelMultimodelo(
        criar_gestor_padrao(
            registro
        )
    )


def _evid():
    return (
        Evidencia(
            id="E1",
            conteudo="evidencia",
        ),
    )


def test_core_vp_preservado():
    r = _painel(
        "INCONCLUSIVO",
        "INCONCLUSIVO",
        "INCONCLUSIVO",
    ).executar(
        _evid(),
        "VERDADEIRO_POSITIVO",
        "F1",
    )

    assert (
        r.veredito_final
        == "VERDADEIRO_POSITIVO"
    )


def test_consenso_nao_promove_core():
    r = _painel(
        "VERDADEIRO_POSITIVO",
        "VERDADEIRO_POSITIVO",
        "VERDADEIRO_POSITIVO",
    ).executar(
        _evid(),
        "INCONCLUSIVO",
        "F2",
    )

    assert (
        r.veredito_final
        == "INCONCLUSIVO"
    )


def test_rotulo_nao_vaza():
    evidencias = construir_evidencias_cegas(
        {
            "message":
                "achado",
        },
        {
            "veredito_final":
                "VERDADEIRO_POSITIVO",

            "validacao_manual": {
                "rotulo":
                    "VERDADEIRO_POSITIVO",
            },

            "security_oracle": {
                "evidencia":
                    "prova objetiva",
            },
        },
    )

    texto = "\n".join(
        x.conteudo
        for x in evidencias
    )

    assert (
        "VERDADEIRO_POSITIVO"
        not in texto
    )

    assert (
        "prova objetiva"
        in texto
    )
