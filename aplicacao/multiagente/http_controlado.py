from __future__ import annotations

import asyncio
from typing import Any

from aplicacao.http_runtime.executor import (
    ExecutorHttpControlado,
)
from aplicacao.http_runtime.modelos import (
    AlvoHttpAutorizado,
)
from aplicacao.http_runtime.validador_autorizacao import (
    ValidadorAutorizacaoHttp,
)


def executar_validacao_autorizacao_http(
    *,
    base_url: str,
    caminho: str,
    marcador: str,
    transport=None,
) -> dict[str, Any]:
    """
    Executa exatamente o validador HTTP existente.

    Política deste adaptador:
    - loopback permitido;
    - rede privada bloqueada;
    - rede pública bloqueada;
    - sem descoberta de alvo;
    - sem redirecionamento de escopo;
    - sem shell.
    """

    if not base_url:
        raise ValueError("base_url HTTP não informada")

    if not caminho or not caminho.startswith("/"):
        raise ValueError(
            "caminho HTTP precisa iniciar com /"
        )

    if not marcador:
        raise ValueError(
            "marcador de recurso não informado"
        )

    async def fluxo():
        alvo = AlvoHttpAutorizado(
            base_url=base_url,
            permitir_loopback=True,
            permitir_rede_privada=False,
            permitir_rede_publica=False,
        )

        executor = ExecutorHttpControlado(
            alvo=alvo,
            transport=transport,
        )

        resultado = await (
            ValidadorAutorizacaoHttp(
                executor
            ).validar(
                caminho=caminho,
                marcador=marcador,
            )
        )

        return resultado

    resultado = asyncio.run(fluxo())

    return {
        "executada": True,
        "tipo": "autorizacao_http",
        "base_url": base_url,
        "caminho": caminho,
        "violacao_confirmada": bool(
            resultado.violado
        ),
        "propriedade": resultado.propriedade,
        "justificativa": resultado.justificativa,
        "evidencias": resultado.evidencias,
        "resultado_oraculo": resultado.model_dump(
            mode="json"
        ),
    }
