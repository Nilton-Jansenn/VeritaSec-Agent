from __future__ import annotations

from pathlib import Path
from typing import Any

from .executor import ExecutorFerramentas


class ExecutorFerramentasComEstaticas(ExecutorFerramentas):
    """
    Acrescenta leitura contextual de codigo.

    Nao executa shell, comandos arbitrarios, HTTP ou DAST.
    """

    _EXTENSOES = frozenset({
        ".py", ".js", ".jsx", ".ts", ".tsx",
        ".java", ".go", ".php", ".rb",
        ".c", ".cc", ".cpp", ".h",
        # VERITASSEC_PASSO02_EXTENSOES
        ".cs", ".kt", ".swift", ".vue",
        ".html", ".htm", ".yaml", ".yml",
        ".json", ".xml", ".sh", ".sql",
        ".css", ".svelte", ".properties",

    })

    @staticmethod
    def _campo(obj: Any, nome: str, padrao=None):
        if isinstance(obj, dict):
            return obj.get(nome, padrao)
        return getattr(obj, nome, padrao)

    def _obter_arquivo(self, achado: Any) -> Path:
        metadados = self._campo(
            achado, "metadados", {}
        ) or {}

        if not isinstance(metadados, dict):
            raise ValueError("METADADOS_INVALIDOS")

        projeto = metadados.get("projeto")
        arquivo = self._campo(achado, "arquivo")

        if not projeto or not arquivo:
            raise ValueError("ESCOPO_ESTATICO_NAO_INFORMADO")

        raiz = Path(projeto).expanduser().resolve()
        alvo = Path(arquivo).expanduser()

        if not raiz.is_dir():
            raise ValueError("RAIZ_PROJETO_INVALIDA")

        if not alvo.is_absolute():
            alvo = raiz / alvo

        alvo = alvo.resolve()

        if not alvo.is_relative_to(raiz):
            raise ValueError("ARQUIVO_FORA_DO_PROJETO")

        if not alvo.is_file():
            raise ValueError("ARQUIVO_NAO_ENCONTRADO")

        if alvo.suffix.lower() not in self._EXTENSOES:
            raise ValueError("EXTENSAO_NAO_AUTORIZADA")

        if alvo.stat().st_size > 2 * 1024 * 1024:
            raise ValueError("ARQUIVO_ACIMA_DO_LIMITE")

        return alvo

    def busca_codigo(
        self,
        *,
        achado: Any,
        sementes: list[str] | None = None,
    ) -> dict[str, Any]:

        # VERITASSEC_PASSO02_ERRO_ESTATICO
        try:
            arquivo = self._obter_arquivo(achado)
        except ValueError as exc:
            codigo = str(exc)

            if codigo in {
                "ARQUIVO_NAO_ENCONTRADO",
                "EXTENSAO_NAO_AUTORIZADA",
                "ARQUIVO_ACIMA_DO_LIMITE",
                "ESCOPO_ESTATICO_NAO_INFORMADO",
                "RAIZ_PROJETO_INVALIDA",
                "METADADOS_INVALIDOS",
            }:
                return {
                    "capacidade": "busca_codigo",
                    "executada": False,
                    "tipo_evidencia": None,
                    "confirmacao_vulnerabilidade": False,
                    "motivo": codigo,
                }

            # Tentativas fora do projeto continuam
            # bloqueadas por excecao.
            raise

        linha = self._campo(
            achado, "linha", 1
        )

        try:
            linha = max(1, int(linha or 1))
        except (ValueError, TypeError):
            linha = 1

        contexto = self.adquirir_contexto_codigo(
            str(arquivo),
            linha,
            contexto=12,
        )

        return {
            "capacidade": "busca_codigo",
            "executada": bool(
                contexto.get("executada")
            ),
            "tipo_evidencia": "CONTEXTO_ESTATICO",
            "confirmacao_vulnerabilidade": False,
            "resultado": contexto,
        }

    def revisao_codigo_seguro(
        self,
        *,
        achado: Any,
        sementes: list[str] | None = None,
    ) -> dict[str, Any]:

        contexto = self.busca_codigo(
            achado=achado,
            sementes=sementes,
        )

        contexto["capacidade"] = (
            "revisao_codigo_seguro"
        )

        contexto["tipo_evidencia"] = (
            "INSUMO_PARA_REVISAO_ESTATICA"
        )

        return contexto
