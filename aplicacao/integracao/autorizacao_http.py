from __future__ import annotations

import httpx

from aplicacao.dominio.modelos import Investigacao
from aplicacao.http_runtime.executor import (
    ExecutorHttpControlado,
)
from aplicacao.http_runtime.modelos import (
    AlvoHttpAutorizado,
)
from aplicacao.http_runtime.validador_autorizacao import (
    ValidadorAutorizacaoHttp,
)

from .evidencias_runtime import (
    RegistradorEvidenciaRuntime,
)


class IntegradorAutorizacaoHttp:

    def __init__(
        self,
        app,
        base_url: str = "http://127.0.0.1",
    ) -> None:

        self.app = app
        self.base_url = base_url
        self.registrador = (
            RegistradorEvidenciaRuntime()
        )

    async def executar(
        self,
        investigacao: Investigacao,
        caminho: str,
        marcador: str,
    ) -> bool:

        if (
            not investigacao.escopo
            .execucao_dinamica_permitida
        ):
            raise PermissionError(
                "execução dinâmica não autorizada"
            )

        alvo = AlvoHttpAutorizado(
            base_url=self.base_url,
            permitir_loopback=True,
            permitir_rede_privada=False,
            permitir_rede_publica=False,
        )

        transport = httpx.ASGITransport(
            app=self.app
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

        self.registrador.registrar_dinamica(
            investigacao=investigacao,
            origem="m6_runtime_http_controlado",
            descricao=(
                "comparação de acesso HTTP entre "
                "identidade autorizada e não autorizada"
            ),
            observacao=resultado.justificativa,
            metadados=resultado.evidencias,
        )

        self.registrador.registrar_oraculo(
            investigacao=investigacao,
            origem="m6_oraculo_autorizacao",
            propriedade=resultado.propriedade,
            observacao=resultado.justificativa,
            violado=resultado.violado,
            metadados=resultado.evidencias,
        )

        return resultado.violado
