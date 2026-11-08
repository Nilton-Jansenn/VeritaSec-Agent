from pathlib import Path

from aplicacao.multiagente.capacidades_canonicas import (
    canonicalizar_capacidade,
)

from aplicacao.multiagente.contexto_expandido import (
    adquirir_contexto_expandido,
)

from aplicacao.multiagente.perfil_runtime_local import (
    obter_perfil_runtime_local,
)


ROOT = Path(
    __file__
).resolve().parents[1]

JUICE = (
    ROOT
    / "input"
    / "projects"
    / "juice-shop"
)


def test_alias_codigo():

    assert (
        canonicalizar_capacidade(
            "Análise de fluxo de dados "
            "(Data Flow Analysis)"
        )
        == "revisao_codigo_seguro"
    )

    assert (
        canonicalizar_capacidade(
            "Analisador de código-fonte"
        )
        == "revisao_codigo_seguro"
    )

    assert (
        canonicalizar_capacidade(
            "leitor_de_conteudo_de_arquivo"
        )
        == "busca_codigo"
    )


def test_alias_dinamico():

    assert (
        canonicalizar_capacidade(
            "Análise dinâmica (DAST)"
        )
        == "runtime_http"
    )

    assert (
        canonicalizar_capacidade(
            "Path Traversal"
        )
        == "path_traversal"
    )


def test_alias_perigoso_nao_mapeado():

    assert (
        canonicalizar_capacidade(
            "executar shell arbitrario"
        )
        is None
    )


def test_perfil_juice_shop(
    monkeypatch,
):

    monkeypatch.setenv(
        "VERITASSEC_RUNTIME_LOCAL",
        "true",
    )

    monkeypatch.setenv(
        "VERITASSEC_RUNTIME_BASE_URL",
        "http://127.0.0.1:3000",
    )

    perfil = (
        obter_perfil_runtime_local(
            str(JUICE)
        )
    )

    assert (
        perfil.habilitado
        is True
    )

    assert (
        perfil.projeto_autorizado
        is True
    )

    assert (
        perfil.loopback
        is True
    )

    assert (
        perfil.base_url
        == "http://127.0.0.1:3000"
    )

    assert (
        perfil.motivo
        == "RUNTIME_LOCAL_AUTORIZADO"
    )


def test_perfil_desabilitado(
    monkeypatch,
):

    monkeypatch.setenv(
        "VERITASSEC_RUNTIME_LOCAL",
        "false",
    )

    perfil = (
        obter_perfil_runtime_local(
            str(JUICE)
        )
    )

    assert (
        perfil.habilitado
        is False
    )

    assert (
        perfil.base_url
        is None
    )

    assert (
        perfil.motivo
        == "RUNTIME_LOCAL_DESABILITADO"
    )


def test_perfil_externo_fail_closed(
    monkeypatch,
):

    monkeypatch.setenv(
        "VERITASSEC_RUNTIME_LOCAL",
        "true",
    )

    monkeypatch.setenv(
        "VERITASSEC_RUNTIME_BASE_URL",
        "https://example.com",
    )

    perfil = (
        obter_perfil_runtime_local(
            str(JUICE)
        )
    )

    assert (
        perfil.habilitado
        is False
    )

    assert (
        perfil.base_url
        is None
    )

    assert (
        perfil.loopback
        is False
    )

    assert (
        perfil.motivo
        == "BASE_URL_NAO_LOOPBACK"
    )


def test_contexto_expandido():

    arquivo = next(
        p
        for p in JUICE.rglob(
            "*.ts"
        )
        if p.is_file()
    )

    r = adquirir_contexto_expandido(
        arquivo=str(arquivo),
        linha=1,
        projeto=str(JUICE),
    )

    assert (
        r["executada"]
        is True
    )

    assert (
        "arquivo_completo"
        in r
    )

    assert (
        "referencias"
        in r
    )
