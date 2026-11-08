# Importa expressões regulares.
import re


def validar_identificador_usuario(valor: str) -> int:
    # Remove espaços nas extremidades.
    valor = valor.strip()

    # Aceita apenas 1 a 10 dígitos.
    if not re.fullmatch(r"[0-9]{1,10}", valor):
        raise ValueError("Identificador inválido. Somente números são permitidos.")

    # Converte para inteiro.
    return int(valor)
