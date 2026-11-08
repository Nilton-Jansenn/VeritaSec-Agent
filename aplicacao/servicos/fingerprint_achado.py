"""
Arquivo: fingerprint_achado.py

Objetivo:
---------
Gerar uma chave única e determinística para cada achado.

A chave considera:
- repositório
- branch
- arquivo
- linha inicial
- linha final
- regra SAST
- hash do trecho de código

Assim, o VeritasSec evita reenviar o mesmo trecho para a LLM.
"""

import hashlib
import re


def normalizar_codigo_para_hash(codigo: str) -> str:
    """
    Normaliza o código antes de gerar hash.

    Remove diferenças irrelevantes de espaçamento para evitar que pequenas
    alterações de formatação gerem fingerprints diferentes.
    """

    codigo = codigo or ""
    codigo = re.sub(r"\s+", " ", codigo)
    codigo = codigo.strip()
    return codigo


def gerar_fingerprint_achado(
    repositorio: str,
    branch: str,
    arquivo: str,
    linha_inicial: int | None,
    linha_final: int | None,
    regra_sast: str,
    trecho_codigo: str,
) -> str:
    """
    Gera fingerprint único do achado.
    """

    trecho_normalizado = normalizar_codigo_para_hash(trecho_codigo)

    hash_trecho = hashlib.sha256(trecho_normalizado.encode("utf-8")).hexdigest()

    base = "|".join(
        [
            repositorio or "",
            branch or "",
            arquivo or "",
            str(linha_inicial or ""),
            str(linha_final or ""),
            regra_sast or "",
            hash_trecho,
        ]
    )

    return hashlib.sha256(base.encode("utf-8")).hexdigest()
