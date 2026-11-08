from pathlib import Path

from aplicacao.multiagente import (
    AchadoMultiagente,
    OrquestradorMultiagente,
    PapelAgente,
    REGISTRO_AGENTES,
)

from aplicacao.multiagente.painel_papeis import (
    sanitizar,
)

from aplicacao.integracoes.zap.evidencia import (
    normalizar_alerta_zap,
)

from aplicacao.multiagente.fundamentacao import (
    construir_fundamentacao_tecnica,
)


ROOT = Path(__file__).resolve().parents[1]


PAPEIS = [
    PapelAgente.ORQUESTRADOR,
    PapelAgente.ANALISTA_CODIGO,
    PapelAgente.SUPERFICIE_ATAQUE,
    PapelAgente.HIPOTESES,
    PapelAgente.PLANEJADOR,
    PapelAgente.VALIDACAO,
    PapelAgente.CRITICO,
]


def test_exatamente_sete_agentes():

    assert (
        REGISTRO_AGENTES.quantidade()
        == 7
    )

    assert (
        list(
            REGISTRO_AGENTES
            .todos()
            .keys()
        )
        == PAPEIS
    )


def test_exatamente_um_evento_por_papel(
    tmp_path,
    monkeypatch,
):

    monkeypatch.setenv(
        "IA_HABILITADA",
        "false",
    )

    alvo = tmp_path / "alvo.py"

    alvo.write_text(
        "x = input()\nprint(x)\n",
        encoding="utf-8",
    )

    resultado = (
        OrquestradorMultiagente()
        .investigar(
            AchadoMultiagente(
                id="PASSO1-SETE",
                regra="teste",
                arquivo=str(alvo),
                linha=1,
            )
        )
    )

    assert (
        resultado.agentes_executados
        == PAPEIS
    )

    assert len(
        resultado.trilha
    ) == 7

    assert len(
        set(
            resultado.agentes_executados
        )
    ) == 7


def test_fase1_nao_cria_evento_extra():

    fonte = (
        ROOT
        / "aplicacao"
        / "multiagente"
        / "orquestrador.py"
    ).read_text(
        encoding="utf-8"
    )

    assert (
        fonte.count(
            "evento(\n"
            "            PapelAgente.CRITICO"
        )
        == 1
    )

    assert (
        fonte.index(
            "VERITASSEC_PASSO1_FASE1_INTERNA"
        )
        <
        fonte.index(
            "# 5. PLANEJADOR"
        )
        <
        fonte.index(
            "FASE 2 (PÓS-EVIDÊNCIA)"
        )
    )

    assert (
        "registro_precomputado="
        "registro_critico_fase1"
        in fonte
    )


def test_ground_truth_nao_vaza():

    limpo = sanitizar(
        {
            "ground_truth":
                "VERDADEIRO_POSITIVO",

            "validacao_manual":
                "confirmado",

            "veredito_final":
                "VERDADEIRO_POSITIVO",

            "evidencia":
                "source -> sink",
        }
    )

    texto = str(limpo)

    assert "ground_truth" not in texto
    assert "validacao_manual" not in texto
    assert "veredito_final" not in texto

    assert (
        "source -> sink"
        in texto
    )


def test_zap_e_evidencia():

    e = normalizar_alerta_zap(
        {
            "pluginId": "40018",
            "alert": "SQL Injection",
            "risk": "High",
            "url":
                "http://127.0.0.1/api",
        }
    )

    assert (
        e["tipo"]
        == "EVIDENCIA_DAST_ZAP"
    )

    assert (
        e["autoridade_decisoria"]
        is False
    )

    assert (
        len(e["hash_sha256"])
        == 64
    )


def test_fundamentacao_vp():

    f = construir_fundamentacao_tecnica(
        {
            "veredito_final":
                "VERDADEIRO_POSITIVO",

            "evidencia_oraculo":
                True,
        }
    )

    assert (
        f["veredito"]
        == "VERDADEIRO_POSITIVO"
    )


def test_fundamentacao_fp():

    f = construir_fundamentacao_tecnica(
        {
            "veredito_final":
                "FALSO_POSITIVO",

            "refutacao":
                "fluxo refutado",
        }
    )

    assert (
        f["veredito"]
        == "FALSO_POSITIVO"
    )

    assert (
        f["evidencias_refutacao"]
    )


def test_fundamentacao_inconclusivo():

    f = construir_fundamentacao_tecnica(
        {
            "veredito_final":
                "INCONCLUSIVO",

            "evidencias_ausentes": [
                "runtime",
                "oracle",
            ],
        }
    )

    assert (
        f["veredito"]
        == "INCONCLUSIVO"
    )

    assert (
        f["evidencias_ausentes"]
    )


def test_dast_nao_e_ground_truth():

    fonte = (
        ROOT
        / "aplicacao"
        / "servicos"
        / "montador_prompt.py"
    ).read_text(
        encoding="utf-8"
    )

    assert (
        "DAST deve ser usado apenas "
        "como ground truth experimental externo"
        not in fonte
    )
