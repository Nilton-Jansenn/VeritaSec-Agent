from __future__ import annotations

from aplicacao.http_runtime.modelos import (
    ObservacaoHttp,
    ResultadoOraculoHttp,
)


class OraculoAutorizacao:
    """
    Propriedade:

    uma identidade sem autorização não pode obter
    o mesmo recurso protegido disponibilizado a uma
    identidade autorizada.
    """

    def avaliar(
        self,
        autorizado: ObservacaoHttp,
        nao_autorizado: ObservacaoHttp,
        marcador_recurso: str,
    ) -> ResultadoOraculoHttp:

        autorizado_obteve = (
            autorizado.status_code == 200
            and marcador_recurso
            in autorizado.corpo
        )

        nao_autorizado_obteve = (
            nao_autorizado.status_code == 200
            and marcador_recurso
            in nao_autorizado.corpo
        )

        violado = (
            autorizado_obteve
            and nao_autorizado_obteve
        )

        if violado:
            justificativa = (
                "identidade não autorizada obteve "
                "o recurso protegido"
            )
        else:
            justificativa = (
                "não foi observada equivalência "
                "de acesso ao recurso protegido"
            )

        return ResultadoOraculoHttp(
            violado=violado,
            propriedade=(
                "controle de autorização "
                "sobre recurso protegido"
            ),
            justificativa=justificativa,
            evidencias={
                "status_autorizado": (
                    autorizado.status_code
                ),
                "status_nao_autorizado": (
                    nao_autorizado.status_code
                ),
                "marcador": marcador_recurso,
            },
        )
