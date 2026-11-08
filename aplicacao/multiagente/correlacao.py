from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class ResultadoCorrelacao:
    estatica: bool
    semantica: bool
    dinamica: bool
    oracle: bool
    reproduzivel: bool
    estado: str
    justificativa: str

    def dump(self) -> dict[str, Any]:
        return {
            "estatica": self.estatica,
            "semantica": self.semantica,
            "dinamica": self.dinamica,
            "oracle": self.oracle,
            "reproduzivel": self.reproduzivel,
            "estado": self.estado,
            "justificativa": self.justificativa,
        }


def correlacionar_evidencias(
    *,
    evidencia_estatica: bool,
    plausibilidade_semantica: bool,
    evidencia_dinamica: bool,
    violacao_oraculo: bool,
    reproduzivel: bool,
) -> ResultadoCorrelacao:

    if (
        evidencia_dinamica
        and violacao_oraculo
        and reproduzivel
    ):
        return ResultadoCorrelacao(
            estatica=evidencia_estatica,
            semantica=plausibilidade_semantica,
            dinamica=True,
            oracle=True,
            reproduzivel=True,
            estado="REPRODUZIDO_DINAMICAMENTE",
            justificativa=(
                "Execução observável, violação confirmada "
                "por Security Oracle e reprodução controlada."
            ),
        )

    if evidencia_estatica and plausibilidade_semantica:
        return ResultadoCorrelacao(
            estatica=True,
            semantica=True,
            dinamica=evidencia_dinamica,
            oracle=violacao_oraculo,
            reproduzivel=reproduzivel,
            estado="PLAUSIVEL_SEMANTICAMENTE",
            justificativa=(
                "Suporte estático e semântico sem "
                "confirmação dinâmica suficiente."
            ),
        )

    if evidencia_estatica:
        return ResultadoCorrelacao(
            estatica=True,
            semantica=plausibilidade_semantica,
            dinamica=evidencia_dinamica,
            oracle=violacao_oraculo,
            reproduzivel=reproduzivel,
            estado="CANDIDATO_ESTATICO",
            justificativa=(
                "Evidência estática sem confirmação dinâmica."
            ),
        )

    return ResultadoCorrelacao(
        estatica=False,
        semantica=plausibilidade_semantica,
        dinamica=evidencia_dinamica,
        oracle=violacao_oraculo,
        reproduzivel=reproduzivel,
        estado="INCONCLUSIVO",
        justificativa="Evidência insuficiente.",
    )
