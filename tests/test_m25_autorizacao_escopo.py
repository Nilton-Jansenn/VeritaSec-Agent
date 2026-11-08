from pathlib import Path
import tempfile

from aplicacao.multiagente.modelos import (
    AchadoMultiagente,
)

from aplicacao.multiagente.politica_escopo import (
    CAPACIDADES_REGISTRADAS_PADRAO,
    calcular_capacidades_autorizadas,
)


def _arquivo_temporario(td: str) -> str:
    alvo = Path(td) / "alvo.py"

    alvo.write_text(
        "print('ok')\n",
        encoding="utf-8",
    )

    return str(alvo)


def test_registrada_nao_significa_autorizada():
    with tempfile.TemporaryDirectory() as td:
        achado = AchadoMultiagente(
            id="M25-01",
            arquivo=_arquivo_temporario(td),
            linha=1,
            execucao_dinamica_permitida=False,
        )

        politica = calcular_capacidades_autorizadas(
            achado=achado,
            capacidades_registradas=set(
                CAPACIDADES_REGISTRADAS_PADRAO
            ),
        )

        assert (
            politica.capacidades_autorizadas
            != politica.capacidades_registradas
        )

        assert "busca_codigo" in (
            politica.capacidades_autorizadas
        )

        assert "path_traversal" not in (
            politica.capacidades_autorizadas
        )

        assert "autorizacao_http" not in (
            politica.capacidades_autorizadas
        )

        assert "zap" not in (
            politica.capacidades_autorizadas
        )


def test_path_traversal_exige_autorizacao_sandbox_seeds_budget():
    with tempfile.TemporaryDirectory() as td:
        sandbox = Path(td) / "sandbox"
        sandbox.mkdir()

        arquivo = _arquivo_temporario(td)

        achado = AchadoMultiagente(
            id="M25-02",
            arquivo=arquivo,
            linha=1,
            execucao_dinamica_permitida=True,
            raiz_sandbox=str(sandbox),
            sementes=[
                "../fora.txt",
            ],
            max_iteracoes=3,
        )

        politica = calcular_capacidades_autorizadas(
            achado=achado,
        )

        assert "path_traversal" in (
            politica.capacidades_autorizadas
        )

        assert "busca_evolucionaria" in (
            politica.capacidades_autorizadas
        )

        assert "oraculo_path_traversal" in (
            politica.capacidades_autorizadas
        )


def test_path_traversal_sem_seed_e_negado():
    with tempfile.TemporaryDirectory() as td:
        sandbox = Path(td) / "sandbox"
        sandbox.mkdir()

        achado = AchadoMultiagente(
            id="M25-03",
            arquivo=_arquivo_temporario(td),
            linha=1,
            execucao_dinamica_permitida=True,
            raiz_sandbox=str(sandbox),
            sementes=[],
            max_iteracoes=3,
        )

        politica = calcular_capacidades_autorizadas(
            achado=achado,
        )

        assert "path_traversal" not in (
            politica.capacidades_autorizadas
        )


def test_seed_com_nul_e_negada():
    with tempfile.TemporaryDirectory() as td:
        sandbox = Path(td) / "sandbox"
        sandbox.mkdir()

        achado = AchadoMultiagente(
            id="M25-04",
            arquivo=_arquivo_temporario(td),
            linha=1,
            execucao_dinamica_permitida=True,
            raiz_sandbox=str(sandbox),
            sementes=[
                "../fora\x00.txt",
            ],
            max_iteracoes=3,
        )

        politica = calcular_capacidades_autorizadas(
            achado=achado,
        )

        assert "path_traversal" not in (
            politica.capacidades_autorizadas
        )


def test_http_loopback_explicito_pode_ser_autorizado():
    with tempfile.TemporaryDirectory() as td:
        achado = AchadoMultiagente(
            id="M25-05",
            arquivo=_arquivo_temporario(td),
            linha=1,
            execucao_dinamica_permitida=True,
            base_url_http="http://127.0.0.1:8083",
            caminho_http="/recurso/1",
            marcador_recurso="M25",
            max_iteracoes=3,
        )

        politica = calcular_capacidades_autorizadas(
            achado=achado,
        )

        assert "runtime_http" in (
            politica.capacidades_autorizadas
        )

        assert "autorizacao_http" in (
            politica.capacidades_autorizadas
        )

        assert "oraculo_autorizacao" in (
            politica.capacidades_autorizadas
        )


def test_http_externo_e_fail_closed():
    with tempfile.TemporaryDirectory() as td:
        achado = AchadoMultiagente(
            id="M25-06",
            arquivo=_arquivo_temporario(td),
            linha=1,
            execucao_dinamica_permitida=True,
            base_url_http="https://example.com",
            caminho_http="/recurso/1",
            marcador_recurso="M25",
            max_iteracoes=3,
        )

        politica = calcular_capacidades_autorizadas(
            achado=achado,
        )

        assert "runtime_http" not in (
            politica.capacidades_autorizadas
        )

        assert "autorizacao_http" not in (
            politica.capacidades_autorizadas
        )

        assert "oraculo_autorizacao" not in (
            politica.capacidades_autorizadas
        )


def test_zap_nunca_autorizado_por_padrao():
    with tempfile.TemporaryDirectory() as td:
        achado = AchadoMultiagente(
            id="M25-07",
            arquivo=_arquivo_temporario(td),
            linha=1,
            execucao_dinamica_permitida=True,
            base_url_http="http://localhost:8083",
            caminho_http="/",
            marcador_recurso="x",
            max_iteracoes=3,
        )

        politica = calcular_capacidades_autorizadas(
            achado=achado,
        )

        assert "zap" not in (
            politica.capacidades_autorizadas
        )


def test_arquivo_sarif_fora_do_projeto_e_negado():
    with tempfile.TemporaryDirectory() as td:
        raiz = Path(td) / "projeto"
        raiz.mkdir()

        fora = Path(td) / "fora.py"
        fora.write_text(
            "print('fora')\n",
            encoding="utf-8",
        )

        achado = AchadoMultiagente(
            id="M25-08",
            arquivo=str(fora),
            linha=1,
            metadados={
                "projeto": str(raiz),
            },
        )

        politica = calcular_capacidades_autorizadas(
            achado=achado,
        )

        assert "busca_codigo" not in (
            politica.capacidades_autorizadas
        )

        assert "revisao_codigo_seguro" not in (
            politica.capacidades_autorizadas
        )

        assert "proveniencia" not in (
            politica.capacidades_autorizadas
        )
