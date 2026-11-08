"""Oráculos determinísticos de segurança."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ResultadoOraculoPathTraversal:
    violacao_confirmada: bool
    entrada: str
    raiz_autorizada: str
    destino_resolvido: str
    propriedade: str


class OraculoPathTraversal:

    PROPRIEDADE = (
        "A entrada controlável não pode resolver "
        "um recurso fora da raiz autorizada."
    )

    def avaliar(
        self,
        entrada: str,
        raiz_autorizada: str | Path,
        destino_resolvido: str | Path,
    ) -> ResultadoOraculoPathTraversal:

        raiz = Path(
            raiz_autorizada
        ).resolve()

        destino = Path(
            destino_resolvido
        ).resolve()

        try:
            destino.relative_to(raiz)
            violacao = False
        except ValueError:
            violacao = True

        return ResultadoOraculoPathTraversal(
            violacao_confirmada=violacao,
            entrada=entrada,
            raiz_autorizada=str(raiz),
            destino_resolvido=str(destino),
            propriedade=self.PROPRIEDADE,
        )
