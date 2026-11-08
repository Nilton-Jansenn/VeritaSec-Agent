from __future__ import annotations

import json
import sys
from pathlib import Path

import httpx


BASE = "http://127.0.0.1:8083"

PROJ = Path(
    __file__
).resolve().parents[1]

SARIF = (
    PROJ
    / "input"
    / "sarif"
    / "juiceShop_code.sarif"
)

JUICE = (
    PROJ
    / "input"
    / "projects"
    / "juice-shop"
)


def fail(
    mensagem: str,
    *,
    detalhe=None,
) -> None:
    print(
        f"M16_REAL=FAIL:{mensagem}"
    )

    if detalhe is not None:
        print(
            json.dumps(
                detalhe,
                ensure_ascii=False,
                indent=2,
                default=str,
            )
        )

    raise SystemExit(1)


with httpx.Client(
    base_url=BASE,
    timeout=300.0,
) as client:

    # --------------------------------------------------------
    # Status seguro
    # --------------------------------------------------------

    r = client.get(
        "/api/interface/status-ia"
    )

    if r.status_code != 200:
        fail(
            "STATUS_IA_HTTP",
            detalhe={
                "status": r.status_code,
                "body": r.text[:1000],
            },
        )

    status = r.json()

    if (
        status.get(
            "segredo_exposto"
        )
        is not False
    ):
        fail(
            "CONTRATO_SEGREDO"
        )

    print(
        "PROVEDOR="
        + str(
            status.get(
                "provedor"
            )
        )
    )

    print(
        "MODELO="
        + str(
            status.get(
                "modelo"
            )
        )
    )

    print(
        "API_KEY_CONFIGURADA="
        + (
            "SIM"
            if status.get(
                "api_key_configurada"
            )
            else "NAO"
        )
    )

    if not status.get(
        "api_key_configurada"
    ):
        fail(
            "CONFIGURE_A_CHAVE_NA_INTERFACE"
        )

    # --------------------------------------------------------
    # Análise real
    # --------------------------------------------------------

    r = client.post(
        "/api/interface/analisar",
        json={
            "sarif_path": str(SARIF),
            "projeto_path": str(JUICE),
            "indice": 0,
        },
    )

    if r.status_code != 200:
        fail(
            "ANALISE_HTTP",
            detalhe={
                "status": r.status_code,
                "body": r.text[:2000],
            },
        )

    data = r.json()

    if data.get("modo") != "agent":
        fail(
            "MODO_NAO_AGENT",
            detalhe=data,
        )

    if (
        data.get(
            "arquitetura"
        )
        != "multiagente"
    ):
        fail(
            "ARQUITETURA_NAO_MULTIAGENTE"
        )

    if (
        data.get(
            "origem"
        )
        != "sarif"
    ):
        fail(
            "ORIGEM_NAO_SARIF"
        )

    if (
        data.get(
            "total_achados_sarif"
        )
        != 36
    ):
        fail(
            "TOTAL_SARIF_INESPERADO"
        )

    resultado = data.get(
        "resultado",
        {},
    )

    agentes = resultado.get(
        "agentes_executados",
        [],
    )

    trilha = resultado.get(
        "trilha",
        [],
    )

    raciocinio = resultado.get(
        "raciocinio",
        {},
    )

    if len(agentes) != 7:
        fail(
            "AGENTES_TOTAL",
            detalhe=agentes,
        )

    if len(set(agentes)) != 7:
        fail(
            "AGENTES_NAO_UNICOS",
            detalhe=agentes,
        )

    if len(trilha) != 7:
        fail(
            "TRILHA_TOTAL",
            detalhe=trilha,
        )

    if (
        raciocinio.get(
            "agentes_total"
        )
        != 7
    ):
        fail(
            "RACIOCINIO_TOTAL",
            detalhe=raciocinio,
        )

    chamadas = raciocinio.get(
        "chamadas_llm_reais"
    )

    fallbacks = raciocinio.get(
        "fallbacks_deterministicos"
    )

    modo = raciocinio.get(
        "modo"
    )

    print(
        "CHAMADAS_LLM_REAIS="
        + str(chamadas)
    )

    print(
        "FALLBACKS="
        + str(fallbacks)
    )

    print(
        "MODO_RACIOCINIO="
        + str(modo)
    )

    if chamadas != 7:
        erros = []

        for item in raciocinio.get(
            "agentes",
            [],
        ):
            if not item.get(
                "chamada_modelo_realizada"
            ):
                erros.append({
                    "agente": item.get(
                        "agente"
                    ),
                    "modo": item.get(
                        "modo"
                    ),
                    "erro": item.get(
                        "erro"
                    ),
                })

        fail(
            "NEM_TODOS_OS_AGENTES_CHAMARAM_LLM",
            detalhe=erros,
        )

    if fallbacks != 0:
        fail(
            "FALLBACK_PRESENTE",
            detalhe=raciocinio,
        )

    if modo != "LLM_REAL":
        fail(
            "MODO_NAO_LLM_REAL",
            detalhe=raciocinio,
        )

    for item in raciocinio.get(
        "agentes",
        [],
    ):
        if (
            item.get(
                "chamada_modelo_realizada"
            )
            is not True
        ):
            fail(
                "AGENTE_SEM_LLM_REAL",
                detalhe=item,
            )

        if (
            item.get(
                "fallback_deterministico"
            )
            is not False
        ):
            fail(
                "AGENTE_EM_FALLBACK",
                detalhe=item,
            )

        if (
            item.get(
                "modo"
            )
            != "LLM_REAL"
        ):
            fail(
                "MODO_AGENTE_INVALIDO",
                detalhe=item,
            )

    print(
        "ESTADO_FINAL="
        + str(
            resultado.get(
                "estado_final"
            )
        )
    )

    print(
        "MOTIVO_TERMINO="
        + str(
            resultado.get(
                "motivo_termino"
            )
        )
    )

    print(
        "ARTEFATOS_DIR="
        + str(
            data.get(
                "artefatos",
                {}
            ).get(
                "diretorio"
            )
        )
    )

    print("SARIF_REAL=PASS")
    print("JUICE_SHOP_REAL=PASS")
    print("SETE_AGENTES=PASS")
    print("SETE_LLM_REAIS=PASS")
    print("OUTPUT_TIPADO=PASS")
    print("TRILHA_AUDITAVEL=PASS")
    print("FALLBACK=0")
    print("SEGREDO_EXPOSTO=NAO")
    print("M16_REAL=PASS")
