"""Executor determinístico e confinado para experimentos locais.

Não executa shell, subprocessos nem rede.
"""

from __future__ import annotations

from pathlib import Path


class ViolacaoEscopoDinamico(ValueError):
    pass


class ExecutorArquivoControlado:

    def __init__(
        self,
        raiz_sandbox: str | Path,
    ) -> None:

        self.raiz = Path(
            raiz_sandbox
        ).resolve()

        if not self.raiz.is_dir():
            raise ValueError(
                "sandbox inexistente"
            )

    def resolver_sem_bloqueio(
        self,
        entrada: str,
    ) -> Path:
        """Simula resolução vulnerável sem acessar o arquivo."""

        return (
            self.raiz / entrada
        ).resolve()

    def esta_fora_do_escopo(
        self,
        destino: Path,
    ) -> bool:

        try:
            destino.relative_to(self.raiz)
            return False
        except ValueError:
            return True

    def ler_seguro(
        self,
        entrada: str,
        limite_bytes: int = 64_000,
    ) -> str:

        destino = (
            self.raiz / entrada
        ).resolve()

        if self.esta_fora_do_escopo(destino):
            raise ViolacaoEscopoDinamico(
                "destino fora da sandbox"
            )

        if not destino.is_file():
            raise FileNotFoundError(destino)

        if destino.stat().st_size > limite_bytes:
            raise ValueError(
                "arquivo excede limite"
            )

        return destino.read_text(
            encoding="utf-8",
            errors="replace",
        )
