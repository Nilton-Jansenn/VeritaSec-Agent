import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


def obter_str(chave: str, padrao: str = "") -> str:
    valor = os.getenv(chave)
    return valor.strip() if valor is not None else padrao


def obter_int(chave: str, padrao: int) -> int:
    try:
        return int(os.getenv(chave, padrao))
    except (TypeError, ValueError):
        return padrao


def obter_bool(chave: str, padrao: bool = False) -> bool:
    valor = os.getenv(chave)

    if valor is None:
        return padrao

    valor = valor.strip().lower()

    if valor in ("true", "1", "yes", "sim", "s"):
        return True

    if valor in ("false", "0", "no", "nao", "não", "n"):
        return False

    return padrao


class Configuracoes:
    """Configurações centrais do VeritasSec."""

    # Aplicação
    NOME_APLICACAO: str = obter_str("NOME_APLICACAO", "VeritasSec")
    AMBIENTE_APLICACAO: str = obter_str("AMBIENTE_APLICACAO", "desenvolvimento")

    HOST_API: str = obter_str("HOST_API", "0.0.0.0")
    PORTA_API: int = obter_int("PORTA_API", 8000)
    MODO_DEBUG: bool = obter_bool("MODO_DEBUG", False)

    # IA centralizada
    IA_HABILITADA: bool = obter_bool("IA_HABILITADA", True)

    PROVEDOR_IA: str = obter_str("PROVEDOR_IA", "gemini").lower()
    MODELO_IA: str = obter_str("MODELO_IA", "gemini-2.5-flash")

    PERMITIR_IA_EXTERNA: bool = obter_bool("PERMITIR_IA_EXTERNA", True)

    # Chaves de provedores
    CHAVE_OPENAI: str = obter_str("CHAVE_OPENAI")
    OPENAI_API_KEY: str = obter_str("OPENAI_API_KEY", CHAVE_OPENAI)

    CHAVE_GEMINI: str = obter_str("CHAVE_GEMINI")
    GEMINI_API_KEY: str = obter_str("GEMINI_API_KEY", CHAVE_GEMINI)

    # Ollama
    OLLAMA_URL: str = obter_str(
        "OLLAMA_URL",
        obter_str("URL_OLLAMA", "http://127.0.0.1:11434"),
    )

    TEMPO_LIMITE_IA_SEGUNDOS: int = obter_int("TEMPO_LIMITE_IA_SEGUNDOS", 120)

    # Prompt/contrato
    TIPO_PROMPT: str = obter_str("TIPO_PROMPT", "contextual").lower()
    USAR_CONTRATO_RESPOSTA: bool = obter_bool("USAR_CONTRATO_RESPOSTA", True)

    # Correção automática
    GERAR_CORRECAO_AUTOMATICA: bool = obter_bool("GERAR_CORRECAO_AUTOMATICA", False)

    # Diretório externo de artefatos e dados gerados
    DIRETORIO_SAIDAS: str = obter_str(
        "VERITASSEC_SAIDAS_DIR",
        str(Path.home() / "Documentos" / "Projetos" / "VeritasSec-Agent-Saidas"),
    )

    # PostgreSQL
    USAR_POSTGRES: bool = obter_bool("USAR_POSTGRES", True)
    URI_POSTGRES: str = obter_str("URI_POSTGRES")

    # Limites de segurança
    MAXIMO_BYTES_ARQUIVO: int = obter_int("MAXIMO_BYTES_ARQUIVO", 1048576)
    MAXIMO_CARACTERES_CONTEXTO: int = obter_int("MAXIMO_CARACTERES_CONTEXTO", 30000)
    MAXIMO_ACHADOS_REQUISICAO: int = obter_int("MAXIMO_ACHADOS_REQUISICAO", 200)
    LIMITE_ACHADOS_POR_EXECUCAO: int = obter_int("LIMITE_ACHADOS_POR_EXECUCAO", 0)

    # Auditoria
    CAMINHO_AUDITORIA_IA: str = obter_str(
        "CAMINHO_AUDITORIA_IA",
        str(Path(DIRETORIO_SAIDAS) / "logs" / "auditoria_ia.jsonl"),
    )

    def validar(self) -> None:
        provedores_validos = {"gemini", "openai", "ollama", "nenhum"}

        if self.PROVEDOR_IA not in provedores_validos:
            raise ValueError(
                f"PROVEDOR_IA inválido: {self.PROVEDOR_IA}. "
                f"Use um de: {sorted(provedores_validos)}"
            )

        if not self.IA_HABILITADA or self.PROVEDOR_IA == "nenhum":
            return

        if self.PROVEDOR_IA in {"gemini", "openai"} and not self.PERMITIR_IA_EXTERNA:
            raise ValueError(
                "PERMITIR_IA_EXTERNA=false, mas PROVEDOR_IA usa provedor externo."
            )

        if self.PROVEDOR_IA == "gemini" and not self.GEMINI_API_KEY:
            print(
                "Aviso: PROVEDOR_IA=gemini, mas GEMINI_API_KEY/CHAVE_GEMINI não foi configurada."
            )

        if self.PROVEDOR_IA == "openai" and not self.OPENAI_API_KEY:
            print(
                "Aviso: PROVEDOR_IA=openai, mas OPENAI_API_KEY/CHAVE_OPENAI não foi configurada."
            )

        if self.PROVEDOR_IA == "ollama" and not self.OLLAMA_URL:
            print("Aviso: PROVEDOR_IA=ollama, mas OLLAMA_URL não foi configurada.")


configuracoes = Configuracoes()
configuracoes.validar()
