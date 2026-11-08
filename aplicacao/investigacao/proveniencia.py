import hashlib

from aplicacao.dominio.modelos import RegistroProveniencia


def criar_registro(
    investigacao_id: str,
    acao: str,
    componente: str,
    entrada: str | None,
    saida: str | None,
    sucesso: bool,
) -> RegistroProveniencia:

    material = "|".join([
        investigacao_id,
        acao,
        componente,
        entrada or "",
        saida or "",
        str(sucesso),
    ])

    digest = hashlib.sha256(
        material.encode("utf-8")
    ).hexdigest()

    return RegistroProveniencia(
        investigacao_id=investigacao_id,
        acao=acao,
        componente=componente,
        entrada_resumida=entrada,
        saida_resumida=saida,
        sucesso=sucesso,
        hash_sha256=digest,
    )
