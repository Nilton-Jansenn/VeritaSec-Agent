from pathlib import Path

from fastapi.testclient import TestClient
from agno.agent import Agent

from aplicacao.main import app

from aplicacao.multiagente import (
    AchadoMultiagente,
    OrquestradorMultiagente,
    PapelAgente,
    REGISTRO_AGENTES,
)


PAPEIS = [
    PapelAgente.ORQUESTRADOR,
    PapelAgente.ANALISTA_CODIGO,
    PapelAgente.SUPERFICIE_ATAQUE,
    PapelAgente.HIPOTESES,
    PapelAgente.PLANEJADOR,
    PapelAgente.VALIDACAO,
    PapelAgente.CRITICO,
]


def test_existem_sete_agentes_agno_reais():

    agentes = REGISTRO_AGENTES.todos()

    assert len(agentes) == 7

    assert list(
        agentes.keys()
    ) == PAPEIS

    assert all(
        isinstance(a, Agent)
        for a in agentes.values()
    )


def test_agentes_tem_identidade_distinta():

    agentes = REGISTRO_AGENTES.todos()

    ids = [
        agente.id
        for agente in agentes.values()
    ]

    assert len(ids) == 7
    assert len(set(ids)) == 7


def test_arquitetura():

    arq = (
        OrquestradorMultiagente()
        .arquitetura()
    )

    assert arq.framework == "Agno"
    assert arq.quantidade_agentes == 7

    assert (
        "Conclusão de agente"
        in arq.regra_confirmacao
    )


def test_fluxo_real_sete_papeis(tmp_path):

    arquivo = tmp_path / "alvo.py"

    arquivo.write_text(
        """
def ler(caminho):
    return open(caminho).read()
""".strip(),
        encoding="utf-8",
    )

    achado = AchadoMultiagente(
        id="CANARIO-CWE22",
        regra="path traversal",
        cwe="CWE-22",
        arquivo=str(arquivo),
        linha=2,
    )

    resultado = (
        OrquestradorMultiagente()
        .investigar(achado)
    )

    assert (
        resultado.agentes_executados
        == PAPEIS
    )

    assert len(resultado.trilha) == 7

    assert (
        "path_traversal"
        in resultado.ferramentas_planejadas
    )

    assert (
        "busca_evolucionaria"
        in resultado.ferramentas_planejadas
    )

    assert (
        "oraculo_path_traversal"
        in resultado.ferramentas_planejadas
    )

    assert (
        "busca_codigo"
        in resultado.ferramentas_executadas
    )

    # Gate crítico:
    # não houve execução dinâmica real.
    assert resultado.evidencia_dinamica is False

    assert resultado.evidencia_oraculo is False

    assert (
        resultado.estado_final
        == "EVIDENCIA_INSUFICIENTE"
    )


def test_nao_confirma_sem_oraculo(tmp_path):

    arquivo = tmp_path / "x.py"

    arquivo.write_text(
        "print('x')",
        encoding="utf-8",
    )

    resultado = (
        OrquestradorMultiagente()
        .investigar(
            AchadoMultiagente(
                id="A1",
                regra="teste",
                arquivo=str(arquivo),
                linha=1,
            )
        )
    )

    assert (
        resultado.estado_final
        != "IMPACTO_CONFIRMADO"
    )

    assert (
        resultado.estado_final
        != "EXPLORABILIDADE_CONFIRMADA"
    )


def test_endpoint_arquitetura():

    client = TestClient(app)

    r = client.get(
        "/api/v1/multiagente/arquitetura"
    )

    assert r.status_code == 200

    dados = r.json()

    assert (
        dados["quantidade_agentes"]
        == 7
    )


def test_endpoint_investigacao(tmp_path):

    arquivo = tmp_path / "endpoint.py"

    arquivo.write_text(
        "x = input()\nprint(x)\n",
        encoding="utf-8",
    )

    client = TestClient(app)

    r = client.post(
        "/api/v1/multiagente/investigar",
        json={
            "id": "API-001",
            "regra": "path traversal",
            "cwe": "CWE-22",
            "arquivo": str(arquivo),
            "linha": 1,
        },
    )

    assert r.status_code == 200

    dados = r.json()

    assert len(
        dados["resultado"][
            "agentes_executados"
        ]
    ) == 7

    assert (
        dados["persistencia"][
            "sha256"
        ]
    )
