# Importa Path para navegar no sistema de arquivos
from pathlib import Path


def buscar_arquivos_sarif(diretorio_raiz: str) -> list[str]:
    """
    Busca todos os arquivos .sarif dentro do diretório informado.
    """

    caminhos_sarif = []

    for caminho in Path(diretorio_raiz).rglob("*.sarif"):
        caminhos_sarif.append(str(caminho))

    if not caminhos_sarif:
        raise Exception("Nenhum arquivo SARIF encontrado no projeto.")

    return caminhos_sarif