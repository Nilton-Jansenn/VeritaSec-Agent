import httpx

from aplicacao.fixtures.alvo_http import (
    criar_fixture_segura,
    criar_fixture_vulneravel,
)
from aplicacao.multiagente.executor import (
    ExecutorFerramentas,
)
from aplicacao.multiagente.http_controlado import (
    executar_validacao_autorizacao_http,
)


def executar(app):
    transport = httpx.ASGITransport(
        app=app
    )

    return executar_validacao_autorizacao_http(
        base_url="http://127.0.0.1",
        caminho="/recurso/42",
        marcador="RECURSO_PROTEGIDO_42",
        transport=transport,
    )


def test_http_fixture_vulneravel():
    r = executar(
        criar_fixture_vulneravel()
    )

    assert r["executada"] is True
    assert r["violacao_confirmada"] is True
    assert r["resultado_oraculo"]["violado"] is True


def test_http_fixture_segura():
    r = executar(
        criar_fixture_segura()
    )

    assert r["executada"] is True
    assert r["violacao_confirmada"] is False
    assert r["resultado_oraculo"]["violado"] is False


def test_executor_possui_http():
    assert callable(
        ExecutorFerramentas()
        .executar_autorizacao_http
    )
