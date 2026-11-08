from __future__ import annotations

import math
from typing import Protocol


class EstimadorTokens(Protocol):
    def estimar(self, texto: str) -> int:
        ...


class EstimadorTokensConservador:
    """
    Estimador usado apenas para orcamento preventivo.

    Nao substitui a contabilizacao real do provedor.
    """

    def __init__(
        self,
        bytes_por_token: float = 3.0,
        margem: float = 1.15,
    ) -> None:
        if bytes_por_token <= 0:
            raise ValueError(
                "bytes_por_token deve ser > 0"
            )

        if margem < 1.0:
            raise ValueError(
                "margem deve ser >= 1"
            )

        self.bytes_por_token = bytes_por_token
        self.margem = margem

    def estimar(self, texto: str) -> int:
        if not texto:
            return 0

        bruto = math.ceil(
            len(texto.encode("utf-8"))
            / self.bytes_por_token
        )

        return max(
            1,
            math.ceil(bruto * self.margem),
        )
