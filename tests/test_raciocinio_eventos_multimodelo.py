import ast
from pathlib import Path


ARQ = Path(
    "aplicacao/multiagente/orquestrador.py"
)


def _texto():
    return ARQ.read_text(encoding="utf-8")


def test_orquestrador_nao_suprime_agentes():
    texto = _texto()

    assert (
        "RACIOCINIO_MULTIMODELO_CONSOLIDADO"
        not in texto
    )

    assert (
        "VERITASSEC_ETAPA1_AGENTES_ESPECIALIZADOS"
        in texto
    )


def test_agente_recebe_inferencia_especializada():
    texto = _texto()

    inicio = texto.index(
        "VERITASSEC_ETAPA1_AGENTES_ESPECIALIZADOS"
    )

    fim = texto.index(
        "saida_evento = dict(",
        inicio,
    )

    trecho = texto[inicio:fim]

    assert "self.raciocinio.decidir(" in trecho
    assert "papel=papel" in trecho
    assert "objetivo=funcao" in trecho
    assert "contexto=contexto_cognitivo" in trecho


def test_critico_adversarial_fase1_preservado():
    texto = _texto()

    assert (
        "registro_critico_fase1"
        in texto
    )

    assert (
        "registro_precomputado=registro_critico_fase1"
        in texto
    )

    assert "consolidar_fase1(" in texto
    assert "aplicar_fase1_na_hipotese(" in texto


def test_painel_multimodelo_preservado():
    texto = _texto()

    assert "painel_pre_planejamento(" in texto
    assert "consultar_painel_papel(" in texto


def test_estrutura_sintaticamente_valida():
    ast.parse(_texto())
