from __future__ import annotations

import time
from typing import Any

import httpx

from .modelos import (
    AlvoHttpAutorizado,
    CasoHttp,
    ObservacaoHttp,
)
from .politica import validar_alvo


class ExecutorHttpControlado:

    def __init__(
        self,
        alvo: AlvoHttpAutorizado,
        transport: httpx.AsyncBaseTransport
        | None = None,
        timeout_segundos: float = 5.0,
    ) -> None:

        validar_alvo(alvo)

        self.alvo = alvo
        self.transport = transport
        self.timeout = timeout_segundos

    async def executar(
        self,
        caso: CasoHttp,
        identidade: str | None = None,
    ) -> ObservacaoHttp:

        inicio = time.perf_counter()

        async with httpx.AsyncClient(
            base_url=self.alvo.base_url,
            transport=self.transport,
            timeout=self.timeout,
            follow_redirects=False,
        ) as client:

            resposta = await client.request(
                method=caso.metodo.value,
                url=caso.caminho,
                headers=caso.headers,
                params=caso.parametros,
                json=caso.json_body,
            )

        duracao = (
            time.perf_counter()
            - inicio
        ) * 1000.0

        return ObservacaoHttp(
            status_code=resposta.status_code,
            headers={
                str(k): str(v)
                for k, v
                in resposta.headers.items()
            },
            corpo=resposta.text,
            duracao_ms=duracao,
            url=str(resposta.url),
            identidade=identidade,
        )
