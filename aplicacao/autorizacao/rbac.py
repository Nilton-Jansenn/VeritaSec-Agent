from __future__ import annotations

from enum import StrEnum


class Papel(StrEnum):
    ADMINISTRADOR = "administrador"
    AVALIADOR = "avaliador"


class Permissao(StrEnum):
    CONFIGURAR_SISTEMA = "configurar_sistema"
    GERENCIAR_USUARIOS = "gerenciar_usuarios"
    CONSULTAR_AUDITORIA = "consultar_auditoria"

    CRIAR_INVESTIGACAO = "criar_investigacao"
    EXECUTAR_VALIDACAO = "executar_validacao"
    CONSULTAR_EVIDENCIA = "consultar_evidencia"
    EXPORTAR_RESULTADO = "exportar_resultado"


MATRIZ: dict[
    Papel,
    frozenset[Permissao],
] = {
    Papel.ADMINISTRADOR: frozenset(
        Permissao
    ),

    Papel.AVALIADOR: frozenset(
        {
            Permissao.CRIAR_INVESTIGACAO,
            Permissao.EXECUTAR_VALIDACAO,
            Permissao.CONSULTAR_EVIDENCIA,
            Permissao.EXPORTAR_RESULTADO,
        }
    ),
}


def autorizado(
    papel: Papel,
    permissao: Permissao,
) -> bool:

    return (
        permissao
        in MATRIZ[papel]
    )


def exigir(
    papel: Papel,
    permissao: Permissao,
) -> None:

    if not autorizado(
        papel,
        permissao,
    ):
        raise PermissionError(
            f"{papel.value} não possui "
            f"{permissao.value}"
        )
