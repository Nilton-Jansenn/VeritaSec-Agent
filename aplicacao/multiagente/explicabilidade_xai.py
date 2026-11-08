from __future__ import annotations

import hashlib
import json
from typing import Any


def _dic(valor):
    return valor if isinstance(valor, dict) else {}


def _lista(valor):
    return valor if isinstance(valor, list) else []


def anexar_explicabilidade_xai(
    resultado: dict[str, Any],
) -> dict[str, Any]:
    """
    Explica a decisao registrada sem modificá-la.

    Nao infere provas novas e nao chama LLM.
    """

    if not isinstance(resultado, dict):
        raise TypeError("RESULTADO_INVALIDO")

    vm = _dic(
        resultado.get("veredito_multivariado")
    )

    plano = _dic(
        resultado.get("plano_aquisicao_evidencia")
    )

    aquisicao = _dic(
        resultado.get("aquisicao_evidencia")
    )

    orcamento = _dic(
        aquisicao.get("orcamento")
    )

    trilha = _lista(
        resultado.get("trilha")
    )

    contribuicoes = []

    for evento in trilha:
        evento = _dic(evento)
        saida = _dic(evento.get("saida"))
        registro = _dic(
            saida.get("raciocinio_agente")
        )

        decisao = _dic(
            registro.get("decisao")
        )

        texto = str(
            decisao.get("decisao") or ""
        )

        contribuicoes.append({
            "agente": evento.get("agente"),
            "modo": registro.get("modo"),
            "provedor": registro.get("provedor"),
            "llm_real": bool(
                registro.get(
                    "chamada_modelo_realizada"
                )
            ),
            "hash_decisao_sha256": (
                hashlib.sha256(
                    texto.encode("utf-8")
                ).hexdigest()
                if texto else None
            ),
            "decisao_registrada": bool(texto),
        })

    decisoes = [
        _dic(item)
        for item in _lista(
            plano.get("decisoes_politica")
        )
    ]

    resultados = [
        _dic(item)
        for item in _lista(
            aquisicao.get("resultados")
        )
    ]

    justificativa = str(
        resultado.get("justificativa_classificacao")
        or vm.get("justificativa_classificacao")
        or ""
    )

    classificacao = (
        resultado.get("classificacao_final")
        or vm.get("classificacao_final")
    )

    explicacao = {
        "versao": "1.0",
        "tipo": "RASTREABILIDADE_DA_DECISAO",
        "classificacao": classificacao,
        "regra_decisoria": (
            vm.get("fonte_veredito")
            or resultado.get("fonte_veredito")
            or "NAO_REGISTRADA"
        ),
        "justificativa_registrada": bool(
            justificativa
        ),
        "hash_justificativa_sha256": (
            hashlib.sha256(
                justificativa.encode("utf-8")
            ).hexdigest()
            if justificativa else None
        ),
        "evidencias_ausentes": _lista(
            resultado.get(
                "evidencias_ausentes_classificacao"
            )
        ),
        "agentes": contribuicoes,
        "aquisicao": {
            "solicitacoes": len(decisoes),
            "autorizadas": sum(
                item.get("autorizada") is True
                for item in decisoes
            ),
            "negadas": sum(
                item.get("autorizada") is False
                for item in decisoes
            ),
            "acoes_executadas": (
                orcamento.get("acoes_executadas", 0)
            ),
            "resultados_registrados": len(resultados),
            "resultados_executados": sum(
                item.get("executada") is True
                for item in resultados
            ),
            # VERITASSEC_PASSO02_XAI_FERRAMENTAS
            "resultados_nao_executados": sum(
                item.get("executada") is not True
                for item in resultados
            ),
            "falhas_de_execucao": [
                {
                    "capacidade": item.get("capacidade"),
                    "motivo": item.get("motivo"),
                    "tipo_erro": (
                        str(item.get("erro", "")).split(":", 1)[0]
                        if item.get("erro")
                        else None
                    ),
                }
                for item in resultados
                if item.get("motivo") == "ERRO_DE_EXECUCAO"
            ][:32],
            "operacoes_sem_execucao": [
                {
                    "capacidade": item.get("capacidade"),
                    "motivo": item.get("motivo"),
                }
                for item in resultados
                if (
                    item.get("autorizada") is True
                    and item.get("executada") is not True
                )
            ][:32],
            "bloqueios": [
                {
                    "capacidade": item.get(
                        "capacidade"
                    ),
                    "motivo": item.get("motivo"),
                }
                for item in decisoes
                if item.get("autorizada") is False
            ][:32],
        },
        "limites": [
            "A explicacao utiliza registros reais.",
            "Decisao textual de agente nao e prova.",
            "Ausencia de evidencia nao implica FP.",
            "A classificacao original foi preservada.",
        ],
    }

    resultado["explicabilidade_xai"] = explicacao

    return resultado
