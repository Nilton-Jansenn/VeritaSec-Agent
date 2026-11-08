from __future__ import annotations

from typing import Any

from .orquestrador import (
    ExecutorFerramentas,
)


def obter_executor_ferramentas(
    *,
    achado: Any,
):
    """
    Usa exatamente o ExecutorFerramentas já utilizado
    pela arquitetura operacional.
    """

    # Contrato observado: ExecutorFerramentas()
    from .executor_estatico_seguro import ExecutorFerramentasComEstaticas
    return ExecutorFerramentasComEstaticas()
