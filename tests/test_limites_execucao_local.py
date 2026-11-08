import ast
from pathlib import Path

from aplicacao.multiagente.controle_execucao import (
    _vs_limites_execucao_local,
)


def test_somente_local(monkeypatch):

    monkeypatch.setenv(
        "VERITASSEC_PROVEDORES_PAPEIS",
        "local",
    )

    monkeypatch.setenv(
        "VERITASSEC_TIMEOUT_LOCAL",
        "180",
    )

    workers, timeout = (
        _vs_limites_execucao_local(
            total=36,
            workers_originais=2,
            timeout_original=60.0,
        )
    )

    assert workers == 1
    assert timeout >= 7 * 180


def test_multimodelo_com_local(monkeypatch):

    monkeypatch.setenv(
        "VERITASSEC_PROVEDORES_PAPEIS",
        "local,gpt,gemini",
    )

    workers, timeout = (
        _vs_limites_execucao_local(
            total=36,
            workers_originais=2,
            timeout_original=60.0,
        )
    )

    assert workers == 1
    assert timeout > 60.0


def test_gpt_gemini_preservados(monkeypatch):

    monkeypatch.setenv(
        "VERITASSEC_PROVEDORES_PAPEIS",
        "gpt,gemini",
    )

    resultado = _vs_limites_execucao_local(
        total=36,
        workers_originais=2,
        timeout_original=60.0,
    )

    assert resultado == (
        2,
        60.0,
    )


def test_local_um_achado(monkeypatch):

    monkeypatch.setenv(
        "VERITASSEC_PROVEDORES_PAPEIS",
        "local",
    )

    workers, timeout = (
        _vs_limites_execucao_local(
            total=1,
            workers_originais=1,
            timeout_original=60.0,
        )
    )

    assert workers == 1
    assert timeout >= 900.0


def test_timeout_local_invalido(monkeypatch):

    monkeypatch.setenv(
        "VERITASSEC_PROVEDORES_PAPEIS",
        "local",
    )

    monkeypatch.setenv(
        "VERITASSEC_TIMEOUT_LOCAL",
        "nan",
    )

    workers, timeout = (
        _vs_limites_execucao_local(
            total=1,
            workers_originais=1,
            timeout_original=60.0,
        )
    )

    assert workers == 1
    assert timeout >= 900.0


def test_contrato_paralelizacao_preservado():

    arquivo = Path(
        "aplicacao/multiagente/controle_execucao.py"
    )

    codigo = arquivo.read_text(
        encoding="utf-8"
    )

    ast.parse(codigo)

    assert "_workers_achados = min(" in codigo

    assert "_timeout_achado = 60.0" in codigo

    assert "ThreadPoolExecutor" in codigo

    assert (
        "VERITASSEC_LIMITES_LOCAL_COMPATIVEIS_V2"
        in codigo
    )
