from pathlib import Path

import pytest

from aplicacao.llm import (
    CacheMemoriaTTL,
    ErroSegurancaLLM,
    Evidencia,
    GerenciadorContexto,
    PerfilLLM,
    PoliticaContexto,
    ProvedorCallable,
    ProvedorGemini,
    ProvedorGPT,
    ProvedorLocalOpenAI,
    RespostaLLM,
    SolicitacaoLLM,
    carregar_perfil,
    criar_gestor_padrao,
    criar_registro_provedores,
    hash_evidencia,
)


def test_deduplicacao_sha256():
    a = Evidencia(
        id="A",
        conteudo="linha 1\nlinha 2",
    )

    b = Evidencia(
        id="B",
        conteudo="linha 1\r\nlinha 2",
    )

    gestor = GerenciadorContexto(
        PoliticaContexto(
            max_tokens_entrada=1000,
            max_tokens_por_evidencia=500,
            max_evidencias=4,
        )
    )

    pacote = gestor.preparar(
        "s",
        "u",
        (a, b),
    )

    assert len(pacote.incluidas) == 1
    assert pacote.duplicadas_ids == ("B",)
    assert hash_evidencia(a) == hash_evidencia(b)


def test_evidencia_grande_nao_e_truncada():
    gestor = GerenciadorContexto(
        PoliticaContexto(
            max_tokens_entrada=1000,
            max_tokens_por_evidencia=100,
            max_evidencias=4,
        )
    )

    pacote = gestor.preparar(
        "s",
        "u",
        (
            Evidencia(
                id="BIG",
                conteudo="x" * 3000,
            ),
        ),
    )

    assert pacote.incluidas == ()
    assert pacote.omitidas_ids == ("BIG",)
    assert pacote.truncado is True


def test_local_rejeita_0_0_0_0():
    with pytest.raises(
        ErroSegurancaLLM
    ):
        ProvedorLocalOpenAI(
            modelo="m",
            base_url=(
                "http://0.0.0.0:1234/v1"
            ),
        )


def test_registro_tres_provedores():
    cb = lambda req: "ok"

    registro = criar_registro_provedores(
        local=ProvedorCallable(
            "local",
            "l",
            cb,
            escopo="local",
        ),
        gpt=ProvedorGPT(
            "g",
            cb,
        ),
        gemini=ProvedorGemini(
            "gm",
            cb,
        ),
    )

    assert registro.nomes() == (
        "gemini",
        "gpt",
        "local",
    )


def test_cache_hit():
    contador = {"n": 0}

    def callback(req):
        contador["n"] += 1
        return RespostaLLM(
            texto="ok",
            provedor="local",
            modelo="m",
        )

    gestor = criar_gestor_padrao(
        criar_registro_provedores(
            local=ProvedorCallable(
                "local",
                "m",
                callback,
                escopo="local",
            )
        )
    )

    req = SolicitacaoLLM(
        prompt_sistema="s",
        prompt_usuario="u",
        metadados={
            "execution_id": "E",
            "finding_id": "F",
        },
    )

    r1 = gestor.executar(
        "local",
        req,
    )

    r2 = gestor.executar(
        "local",
        req,
    )

    assert r1.cache_hit is False
    assert r2.cache_hit is True
    assert contador["n"] == 1


def test_cache_nao_cruza_finding():
    contador = {"n": 0}

    def callback(req):
        contador["n"] += 1
        return "ok"

    gestor = criar_gestor_padrao(
        criar_registro_provedores(
            local=ProvedorCallable(
                "local",
                "m",
                callback,
                escopo="local",
            )
        )
    )

    for finding in ("F1", "F2"):
        gestor.executar(
            "local",
            SolicitacaoLLM(
                prompt_sistema="s",
                prompt_usuario="u",
                metadados={
                    "execution_id": "E",
                    "finding_id": finding,
                },
            ),
        )

    assert contador["n"] == 2


def test_segredo_externo_bloqueado():
    contador = {"n": 0}

    def callback(req):
        contador["n"] += 1
        return "nao"

    gestor = criar_gestor_padrao(
        criar_registro_provedores(
            gpt=ProvedorGPT(
                "g",
                callback,
            )
        )
    )

    with pytest.raises(
        ErroSegurancaLLM
    ):
        gestor.executar(
            "gpt",
            SolicitacaoLLM(
                prompt_sistema="s",
                prompt_usuario=(
                    "sk-abcdefghijklmnopqrstuvwxyz123456"
                ),
            ),
        )

    assert contador["n"] == 0


def test_segredo_local_nao_cacheado():
    contador = {"n": 0}

    def callback(req):
        contador["n"] += 1
        return "ok"

    gestor = criar_gestor_padrao(
        criar_registro_provedores(
            local=ProvedorCallable(
                "local",
                "m",
                callback,
                escopo="local",
            )
        )
    )

    req = SolicitacaoLLM(
        prompt_sistema="s",
        prompt_usuario=(
            "sk-abcdefghijklmnopqrstuvwxyz123456"
        ),
    )

    r1 = gestor.executar("local", req)
    r2 = gestor.executar("local", req)

    assert r1.cache_habilitado is False
    assert r2.cache_habilitado is False
    assert contador["n"] == 2


def test_orcamento_por_agente():
    visto = {}

    def callback(req):
        visto["max"] = req.max_tokens_saida
        return "ok"

    gestor = criar_gestor_padrao(
        criar_registro_provedores(
            local=ProvedorCallable(
                "local",
                "m",
                callback,
                escopo="local",
            )
        ),
        PerfilLLM(
            max_output_tokens=512
        ),
        {
            "critico_adversarial": 96
        },
    )

    gestor.executar(
        "local",
        SolicitacaoLLM(
            prompt_sistema="s",
            prompt_usuario="u",
            max_tokens_saida=999,
            metadados={
                "agente":
                    "critico_adversarial"
            },
        ),
    )

    assert visto["max"] == 96


def test_cache_tem_salt_por_instancia():
    req = SolicitacaoLLM(
        prompt_sistema="s",
        prompt_usuario="u",
    )

    a = CacheMemoriaTTL()
    b = CacheMemoriaTTL()

    assert (
        a.chave("p", "m", req)
        !=
        b.chave("p", "m", req)
    )


def test_perfil_passo1(tmp_path: Path):
    arquivo = tmp_path / "perfil.env"

    arquivo.write_text(
        "VERITASSEC_LOCAL_CONTEXT_LENGTH=8192\n"
        "VERITASSEC_LOCAL_MAX_CONCURRENCY=1\n",
        encoding="utf-8",
    )

    perfil = carregar_perfil(
        arquivo
    )

    assert perfil.context_length == 8192
    assert perfil.max_concurrency_local == 1
