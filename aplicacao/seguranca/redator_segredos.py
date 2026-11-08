# Importa re para expressões regulares.
import re

# Define padrões simples de segredos.
PADROES_SEGREDOS = [
    re.compile(r"(?i)(api[_-]?key\s*[:=]\s*['\"][^'\"]+['\"])"),
    re.compile(r"(?i)(secret\s*[:=]\s*['\"][^'\"]+['\"])"),
    re.compile(r"(?i)(token\s*[:=]\s*['\"][^'\"]+['\"])"),
    re.compile(r"(?i)(password\s*[:=]\s*['\"][^'\"]+['\"])"),
    re.compile(r"\beyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9._-]+\.[a-zA-Z0-9._-]+\b"),
]


# Substitui segredos por marcadores genéricos.
def redigir_segredos(texto: str) -> str:
    # Inicia com o texto original.
    texto_redigido = texto

    # Percorre cada padrão.
    for padrao in PADROES_SEGREDOS:
        # Faz a substituição.
        texto_redigido = padrao.sub("[SEGREDO_REDACTED]", texto_redigido)

    # Retorna o texto protegido.
    return texto_redigido