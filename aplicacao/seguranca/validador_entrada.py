# Importa Path para validar caminhos.
from pathlib import Path

# Importa as configurações globais.
from aplicacao.nucleo.configuracoes import configuracoes


# Valida o diretório do projeto.
def validar_caminho_projeto(caminho: str) -> Path:
    caminho = (caminho or "").strip()

    # Converte para Path.
    caminho_path = Path(caminho)

    # Verifica se existe e se é diretório.
    if not caminho_path.exists() or not caminho_path.is_dir():
        raise ValueError(f"Diretório do projeto inválido: {caminho}")

    # Retorna caminho absoluto resolvido.
    return caminho_path.resolve()


# Valida o caminho SARIF.
def validar_caminho_sarif(caminho: str) -> Path:
    caminho = (caminho or "").strip()

    # Converte para Path.
    caminho_path = Path(caminho)

    # Verifica se existe.
    if not caminho_path.exists():
        raise ValueError(f"Caminho SARIF inválido: {caminho}")

    # Retorna absoluto.
    return caminho_path.resolve()


# Valida o caminho CSV de diffs.
def validar_caminho_csv_diffs(caminho: str) -> Path:
    caminho = (caminho or "").strip()

    # Converte para Path.
    caminho_path = Path(caminho)

    # Verifica se existe e se é arquivo.
    if not caminho_path.exists() or not caminho_path.is_file():
        raise ValueError(f"Arquivo CSV de diffs inválido: {caminho}")

    # Verifica extensão esperada.
    if caminho_path.suffix.lower() != ".csv":
        raise ValueError(f"O arquivo de diffs deve ter extensão .csv: {caminho}")

    # Retorna absoluto.
    return caminho_path.resolve()


# Limita tamanho de texto antes de enviar aos modelos.
def limitar_tamanho_texto(texto: str) -> str:
    # Se o texto ultrapassar o limite, corta.
    if len(texto) > configuracoes.MAXIMO_CARACTERES_CONTEXTO:
        return texto[: configuracoes.MAXIMO_CARACTERES_CONTEXTO]

    # Caso contrário, mantém como está.
    return texto
