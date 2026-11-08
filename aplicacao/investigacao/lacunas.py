from aplicacao.dominio.modelos import (
    Investigacao,
    LacunaEvidencia,
)


def identificar_lacunas(
    investigacao: Investigacao,
) -> list[LacunaEvidencia]:

    lacunas = [
        LacunaEvidencia(
            tipo="contexto_codigo",
            descricao=(
                "confirmar contexto do código no local "
                "reportado pelo SAST"
            ),
            prioridade=100,
        ),
        LacunaEvidencia(
            tipo="validacao_entrada",
            descricao=(
                "verificar presença de validação ou "
                "sanitização relevante"
            ),
            prioridade=90,
        ),
        LacunaEvidencia(
            tipo="fluxo_dados",
            descricao=(
                "avaliar relação entre entrada e "
                "operação sensível"
            ),
            prioridade=80,
        ),
    ]

    regra = (
        f"{investigacao.achado.regra} "
        f"{investigacao.achado.cwe or ''} "
        f"{investigacao.achado.mensagem}"
    ).lower()

    if any(
        termo in regra
        for termo in (
            "auth",
            "authorization",
            "bola",
            "idor",
            "cwe-639",
            "cwe-862",
        )
    ):
        lacunas.append(
            LacunaEvidencia(
                tipo="autorizacao",
                descricao=(
                    "verificar controle de autorização "
                    "no fluxo relevante"
                ),
                prioridade=95,
            )
        )

    return lacunas
