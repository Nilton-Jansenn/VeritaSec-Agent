# Importa hashlib para cálculo de hash.
import hashlib


# Gera um hash SHA-256 truncado para uso como identificador estável.
def gerar_hash_curto(valor: str, tamanho: int = 24) -> str:
    # Calcula o hash completo.
    hash_completo = hashlib.sha256(valor.encode("utf-8")).hexdigest()

    # Retorna apenas a parte inicial desejada.
    return hash_completo[:tamanho]