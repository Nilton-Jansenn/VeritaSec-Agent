# Importa Path para leitura de arquivos.
from pathlib import Path


# Lê arquivo texto com tolerância a problemas de encoding.
def ler_texto_seguro(caminho: Path) -> str:
    # Retorna o conteúdo lido.
    return caminho.read_text(encoding="utf-8", errors="ignore")