from types import SimpleNamespace

from aplicacao.multiagente import (
    AchadoMultiagente,
    OrquestradorMultiagente,
    REGISTRO_AGENTES,
)
from aplicacao.multiagente.modelos import (
    DecisaoAgenteLLM,
)


def test_sete_agents_executam_run(
    tmp_path,
    monkeypatch,
):
    chamadas = []

    for papel, agente in (
        REGISTRO_AGENTES
        .todos()
        .items()
    ):
        def make_fake(p):
            def fake_run(
                input,
                **kwargs,
            ):
                chamadas.append(
                    p.value
                )

                return SimpleNamespace(
                    content=DecisaoAgenteLLM(
                        decisao=(
                            "Decisão estruturada "
                            f"de {p.value}"
                        ),
                        observacoes=[],
                        ferramentas_sugeridas=[],
                        requer_evidencia_adicional=True,
                        confianca=0.5,
                    )
                )

            return fake_run

        monkeypatch.setattr(
            agente,
            "run",
            make_fake(papel),
        )

    monkeypatch.setenv(
        "IA_HABILITADA",
        "true",
    )

    monkeypatch.setenv(
        "PROVEDOR_IA",
        "gemini",
    )

    monkeypatch.setenv(
        "MODELO_IA",
        "gemini-2.5-flash",
    )

    monkeypatch.setenv(
        "GEMINI_API_KEY",
        "teste",
    )

    codigo = tmp_path / "alvo.py"

    codigo.write_text(
        "valor = input()\nprint(valor)\n",
        encoding="utf-8",
    )

    r = (
        OrquestradorMultiagente()
        .investigar(
            AchadoMultiagente(
                id="M15-7-AGENTES",
                regra="teste",
                arquivo=str(codigo),
                linha=1,
            )
        )
    )

    assert len(r.trilha) == 7
    assert len(chamadas) == 7
    assert len(set(chamadas)) == 7

    for evento in r.trilha:
        meta = (
            evento
            .saida[
                "raciocinio_agente"
            ]
        )

        assert (
            meta[
                "chamada_modelo_realizada"
            ]
            is True
        )

        assert (
            meta[
                "modo"
            ]
            == "LLM_REAL"
        )
