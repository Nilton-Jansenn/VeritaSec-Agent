from __future__ import annotations

from aplicacao.dinamica.executor import (
    ExecutorArquivoControlado,
)
from aplicacao.dinamica.oraculos import (
    OraculoPathTraversal,
)
from aplicacao.dominio.enums import TipoEvidencia
from aplicacao.dominio.modelos import Evidencia
from aplicacao.investigacao.evidencias import hash_evidencia


class ValidadorPathTraversal:

    def __init__(
        self,
        executor: ExecutorArquivoControlado,
    ) -> None:
        self.executor = executor
        self.oraculo = OraculoPathTraversal()

    def validar(
        self,
        hipotese_id: str,
        entrada: str,
    ) -> tuple[Evidencia, Evidencia]:

        destino = (
            self.executor
            .resolver_sem_bloqueio(entrada)
        )

        dinamica = Evidencia(
            hipotese_id=hipotese_id,
            tipo=TipoEvidencia.EXECUCAO_DINAMICA,
            origem="executor_arquivo_controlado",
            descricao=(
                "resolução controlada de caminho "
                "em sandbox"
            ),
            observacao=(
                f"entrada={entrada};"
                f"destino={destino}"
            ),
            hash_sha256=hash_evidencia({
                "entrada": entrada,
                "destino": str(destino),
            }),
            reproduzivel=True,
        )

        resultado = self.oraculo.avaliar(
            entrada,
            self.executor.raiz,
            destino,
        )

        oraculo = Evidencia(
            hipotese_id=hipotese_id,
            tipo=TipoEvidencia.ORACULO,
            origem="oraculo_path_traversal",
            descricao=resultado.propriedade,
            observacao=(
                "violacao_confirmada="
                f"{resultado.violacao_confirmada};"
                "destino="
                f"{resultado.destino_resolvido}"
            ),
            hash_sha256=hash_evidencia(
                resultado.__dict__
            ),
            reproduzivel=True,
            metadados={
                "violacao_confirmada": (
                    resultado.violacao_confirmada
                ),
                "entrada": entrada,
                "destino": (
                    resultado.destino_resolvido
                ),
            },
        )

        return dinamica, oraculo
