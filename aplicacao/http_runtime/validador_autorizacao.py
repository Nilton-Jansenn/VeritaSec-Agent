from __future__ import annotations

from aplicacao.oraculos.autorizacao import (
    OraculoAutorizacao,
)

from .executor import ExecutorHttpControlado
from .modelos import (
    CasoHttp,
    MetodoHttp,
    ResultadoOraculoHttp,
)


class ValidadorAutorizacaoHttp:

    def __init__(
        self,
        executor: ExecutorHttpControlado,
    ) -> None:
        self.executor = executor
        self.oraculo = OraculoAutorizacao()

    async def validar(
        self,
        caminho: str,
        marcador: str,
    ) -> ResultadoOraculoHttp:

        autorizado = await self.executor.executar(
            CasoHttp(
                metodo=MetodoHttp.GET,
                caminho=caminho,
                headers={
                    "X-Identidade": "proprietario",
                },
            ),
            identidade="proprietario",
        )

        nao_autorizado = (
            await self.executor.executar(
                CasoHttp(
                    metodo=MetodoHttp.GET,
                    caminho=caminho,
                    headers={
                        "X-Identidade": "outro",
                    },
                ),
                identidade="outro",
            )
        )

        return self.oraculo.avaliar(
            autorizado=autorizado,
            nao_autorizado=nao_autorizado,
            marcador_recurso=marcador,
        )
