from aplicacao.multiagente import (
    AchadoMultiagente,
    OrquestradorMultiagente,
    PapelAgente,
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


def _codigo(tmp_path):
    p = tmp_path / "alvo.py"

    p.write_text(
        """
from pathlib import Path

def ler(nome):
    return Path(nome).read_text()
""".strip(),
        encoding="utf-8",
    )

    return p


def test_path_traversal_real_com_oraculo(
    tmp_path,
):
    sandbox = tmp_path / "sandbox"
    sandbox.mkdir()

    (sandbox / "seguro.txt").write_text(
        "seguro",
        encoding="utf-8",
    )

    resultado = (
        OrquestradorMultiagente()
        .investigar(
            AchadoMultiagente(
                id="DYN-CWE22",
                regra="path traversal",
                cwe="CWE-22",
                arquivo=str(
                    _codigo(tmp_path)
                ),
                linha=4,
                execucao_dinamica_permitida=True,
                raiz_sandbox=str(sandbox),
                sementes=[
                    "seguro.txt",
                    "../fora.txt",
                ],
            )
        )
    )

    assert resultado.agentes_executados == PAPEIS
    assert len(resultado.trilha) == 7

    assert (
        len(set(resultado.agentes_executados))
        == 7
    )

    assert (
        "busca_evolucionaria"
        in resultado.ferramentas_executadas
    )

    assert (
        "path_traversal"
        in resultado.ferramentas_executadas
    )

    assert (
        "oraculo_path_traversal"
        in resultado.ferramentas_executadas
    )

    assert resultado.evidencia_dinamica
    assert resultado.evidencia_oraculo

    assert resultado.estado_final == (
        "REPRODUZIDO_DINAMICAMENTE"
    )

    assert resultado.motivo_termino == (
        "EVIDENCIA_SUFICIENTE_CONFIRMADA"
    )

    assert resultado.estado_final != (
        "EXPLORABILIDADE_CONFIRMADA"
    )


def test_sem_autorizacao_fail_closed(
    tmp_path,
):
    sandbox = tmp_path / "sandbox"
    sandbox.mkdir()

    resultado = (
        OrquestradorMultiagente()
        .investigar(
            AchadoMultiagente(
                id="BLOCK",
                regra="path traversal",
                cwe="CWE-22",
                arquivo=str(
                    _codigo(tmp_path)
                ),
                linha=4,
                execucao_dinamica_permitida=False,
                raiz_sandbox=str(sandbox),
            )
        )
    )

    assert resultado.agentes_executados == PAPEIS
    assert len(resultado.trilha) == 7

    assert not resultado.evidencia_dinamica
    assert not resultado.evidencia_oraculo

    assert (
        "path_traversal"
        not in resultado.ferramentas_executadas
    )

    assert resultado.estado_final == (
        "EVIDENCIA_INSUFICIENTE"
    )


def test_sem_sandbox_fail_closed(
    tmp_path,
):
    resultado = (
        OrquestradorMultiagente()
        .investigar(
            AchadoMultiagente(
                id="NO-SANDBOX",
                regra="path traversal",
                cwe="CWE-22",
                arquivo=str(
                    _codigo(tmp_path)
                ),
                linha=4,
                execucao_dinamica_permitida=True,
            )
        )
    )

    assert resultado.agentes_executados == PAPEIS
    assert len(resultado.trilha) == 7

    assert not resultado.evidencia_dinamica
    assert not resultado.evidencia_oraculo


def test_replanejamento_nao_cria_oitavo_agente(
    tmp_path,
):
    resultado = (
        OrquestradorMultiagente()
        .investigar(
            AchadoMultiagente(
                id="REPLAN",
                regra="path traversal",
                cwe="CWE-22",
                arquivo=str(
                    _codigo(tmp_path)
                ),
                linha=4,
                max_iteracoes=3,
            )
        )
    )

    assert resultado.agentes_executados == PAPEIS
    assert len(resultado.trilha) == 7

    planejador = next(
        e
        for e in resultado.trilha
        if e.agente == PapelAgente.PLANEJADOR
    )

    assert (
        planejador.saida[
            "replanejamento"
        ]["realizado"]
        is True
    )

    assert resultado.iteracoes == 2
