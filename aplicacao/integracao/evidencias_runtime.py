from __future__ import annotations

from typing import Any

from aplicacao.dominio.enums import TipoEvidencia
from aplicacao.dominio.modelos import (
    Evidencia,
    Investigacao,
)
from aplicacao.investigacao.evidencias import (
    hash_evidencia,
)
from aplicacao.investigacao.servico import (
    ServicoInvestigacao,
)


class RegistradorEvidenciaRuntime:

    def __init__(self) -> None:
        self.servico = ServicoInvestigacao()

    @staticmethod
    def _hipotese_id(
        investigacao: Investigacao,
    ) -> str:

        if investigacao.hipotese:
            return investigacao.hipotese.id

        return investigacao.achado.id

    def registrar_dinamica(
        self,
        investigacao: Investigacao,
        origem: str,
        descricao: str,
        observacao: str,
        metadados: dict[str, Any] | None = None,
    ) -> Evidencia:

        evidencia = Evidencia(
            hipotese_id=self._hipotese_id(
                investigacao
            ),
            tipo=TipoEvidencia.EXECUCAO_DINAMICA,
            origem=origem,
            descricao=descricao,
            observacao=observacao,
            hash_sha256=hash_evidencia(
                {
                    "origem": origem,
                    "descricao": descricao,
                    "observacao": observacao,
                    "metadados": metadados or {},
                }
            ),
            reproduzivel=True,
            metadados=metadados or {},
        )

        self.servico.registrar_evidencia(
            investigacao,
            evidencia,
        )

        return evidencia

    def registrar_oraculo(
        self,
        investigacao: Investigacao,
        origem: str,
        propriedade: str,
        observacao: str,
        violado: bool,
        metadados: dict[str, Any] | None = None,
    ) -> Evidencia:

        dados = dict(
            metadados or {}
        )

        dados["propriedade_violada"] = violado

        evidencia = Evidencia(
            hipotese_id=self._hipotese_id(
                investigacao
            ),
            tipo=TipoEvidencia.ORACULO,
            origem=origem,
            descricao=propriedade,
            observacao=observacao,
            hash_sha256=hash_evidencia(
                {
                    "origem": origem,
                    "propriedade": propriedade,
                    "observacao": observacao,
                    "violado": violado,
                    "metadados": dados,
                }
            ),
            reproduzivel=True,
            metadados=dados,
        )

        self.servico.registrar_evidencia(
            investigacao,
            evidencia,
        )

        return evidencia
