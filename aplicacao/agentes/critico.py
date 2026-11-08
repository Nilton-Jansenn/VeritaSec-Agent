"""Crítico adversarial determinístico.

Tenta refutar suficiência da evidência antes da emissão
de um veredito forte.
"""

from aplicacao.dominio.enums import TipoEvidencia
from aplicacao.dominio.modelos import (
    DecisaoCritico,
    Investigacao,
)


class CriticoAdversarial:

    def revisar(
        self,
        investigacao: Investigacao,
    ) -> DecisaoCritico:

        tipos = {
            evidencia.tipo
            for evidencia in investigacao.evidencias
        }

        ausentes: list[str] = []
        conflitos: list[str] = []

        if not investigacao.hipotese:
            ausentes.append(
                "hipótese estruturada"
            )

        if (
            TipoEvidencia.CONTEXTO_CODIGO
            not in tipos
        ):
            ausentes.append(
                "contexto de código"
            )

        tem_dinamica = (
            TipoEvidencia.EXECUCAO_DINAMICA
            in tipos
        )

        tem_oraculo = (
            TipoEvidencia.ORACULO
            in tipos
        )

        if tem_dinamica != tem_oraculo:
            conflitos.append(
                "evidência dinâmica e oráculo "
                "não estão correlacionados em par"
            )

        suficiente = (
            investigacao.hipotese is not None
            and not ausentes
            and not conflitos
        )

        return DecisaoCritico(
            evidencia_suficiente=suficiente,
            conflitos=conflitos,
            evidencias_ausentes=ausentes,
            recomendacao=(
                "prosseguir_para_decisao"
                if suficiente
                else "adquirir_mais_evidencia"
            ),
            justificativa_resumida=(
                "A suficiência foi avaliada por regras "
                "determinísticas sobre as evidências."
            ),
        )
