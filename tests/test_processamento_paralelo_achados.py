from pathlib import Path
import ast


ARQUIVOS = (
    Path(
        "aplicacao/multiagente/"
        "controle_execucao.py"
    ),
    Path(
        "aplicacao/multiagente/"
        "pipeline_agent.py"
    ),
)


def test_paralelizacao_presente():

    for arquivo in ARQUIVOS:

        texto = arquivo.read_text(
            encoding="utf-8"
        )

        assert (
            "VERITASSEC_ACHADOS_PARALELOS_20261019"
            in texto
        )

        assert (
            "ThreadPoolExecutor"
            in texto
        )

        assert (
            "_workers_achados = min("
            in texto
        )

        assert (
            "_timeout_achado = 60.0"
            in texto
        )


def test_codigo_permanece_valido():

    for arquivo in ARQUIVOS:

        ast.parse(
            arquivo.read_text(
                encoding="utf-8"
            )
        )


def test_teto_concorrencia_dois():

    for arquivo in ARQUIVOS:

        texto = arquivo.read_text(
            encoding="utf-8"
        )

        marcador = texto.index(
            "VERITASSEC_ACHADOS_PARALELOS_20261019"
        )

        trecho = texto[
            marcador:
            marcador + 2500
        ]

        assert "min(" in trecho
        assert "2," in trecho


def test_ordem_de_saida_preservada():

    for arquivo in ARQUIVOS:

        texto = arquivo.read_text(
            encoding="utf-8"
        )

        assert (
            "_futuros[posicao].result("
            in texto
        )


def test_sete_agentes_preservados():

    texto = Path(
        "aplicacao/multiagente/"
        "orquestrador.py"
    ).read_text(
        encoding="utf-8"
    )

    papeis = (
        "PapelAgente.ORQUESTRADOR",
        "PapelAgente.ANALISTA_CODIGO",
        "PapelAgente.SUPERFICIE_ATAQUE",
        "PapelAgente.HIPOTESES",
        "PapelAgente.PLANEJADOR",
        "PapelAgente.VALIDACAO",
        "PapelAgente.CRITICO",
    )

    for papel in papeis:
        assert papel in texto
