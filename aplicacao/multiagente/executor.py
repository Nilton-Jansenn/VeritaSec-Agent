from __future__ import annotations

from pathlib import Path
from typing import Any

from aplicacao.dinamica.executor import (
    ExecutorArquivoControlado,
)
from aplicacao.dinamica.servico import (
    ValidadorPathTraversal,
)
from aplicacao.evolucao.modelos import (
    ConfiguracaoEvolutiva,
)
from aplicacao.evolucao.path_traversal import (
    BuscaEvolutivaPathTraversal,
)

from .ferramentas import catalogo_capacidades
from .http_controlado import (
    executar_validacao_autorizacao_http,
)


class ExecutorFerramentas:
    """
    Registry operacional de ferramentas determinísticas.

    Nenhum Agent recebe shell, subprocess ou executor arbitrário.
    """

    def __init__(self) -> None:
        self.catalogo = catalogo_capacidades()

    def adquirir_contexto_codigo(
        self,
        arquivo: str,
        linha: int | None,
        contexto: int = 12,
    ) -> dict[str, Any]:

        if not arquivo:
            return {
                "executada": False,
                "motivo": "arquivo_nao_informado",
            }

        p = Path(arquivo).expanduser().resolve()

        if not p.is_file():
            return {
                "executada": False,
                "motivo": "arquivo_nao_encontrado",
                "arquivo": str(p),
            }

        linhas = p.read_text(
            encoding="utf-8",
            errors="replace",
        ).splitlines()

        alvo = max(1, int(linha or 1))
        inicio = max(1, alvo - contexto)
        fim = min(
            len(linhas),
            alvo + contexto,
        )

        trecho = "\n".join(
            f"{i}: {linhas[i - 1]}"
            for i in range(
                inicio,
                fim + 1,
            )
        )

        return {
            "executada": True,
            "arquivo": str(p),
            "linha": alvo,
            "inicio": inicio,
            "fim": fim,
            "trecho": trecho,
        }

    def executar_path_traversal(
        self,
        *,
        hipotese_id: str,
        raiz_sandbox: str,
        sementes: list[str],
        max_geracoes: int = 6,
    ) -> dict[str, Any]:

        raiz = Path(
            raiz_sandbox
        ).expanduser().resolve()

        if not raiz.is_dir():
            raise ValueError(
                "sandbox dinâmica inexistente"
            )

        sementes_efetivas = list(
            dict.fromkeys(
                sementes
                or [
                    "arquivo.txt",
                    "../arquivo.txt",
                ]
            )
        )

        config = ConfiguracaoEvolutiva(
            max_geracoes=max_geracoes,
            parar_ao_confirmar=True,
        )

        busca = BuscaEvolutivaPathTraversal(
            raiz,
            config,
        )

        evolucao = busca.executar(
            sementes_efetivas
        )

        melhor = evolucao.melhor

        executor = ExecutorArquivoControlado(
            raiz
        )

        validador = ValidadorPathTraversal(
            executor
        )

        dinamica, oraculo = validador.validar(
            hipotese_id,
            melhor.valor,
        )

        violacao = bool(
            oraculo.metadados.get(
                "violacao_confirmada",
                False,
            )
        )

        return {
            "executada": True,

            "busca_evolucionaria": {
                "confirmado": evolucao.confirmado,
                "geracoes_executadas": (
                    evolucao.geracoes_executadas
                ),
                "execucoes": evolucao.execucoes,
                "melhor": melhor.model_dump(),
                "historico_melhor_aptidao": (
                    evolucao
                    .historico_melhor_aptidao
                ),
            },

            "evidencia_dinamica": (
                dinamica.model_dump(
                    mode="json"
                )
            ),

            "evidencia_oraculo": (
                oraculo.model_dump(
                    mode="json"
                )
            ),

            "violacao_confirmada": violacao,

            "hashes": [
                dinamica.hash_sha256,
                oraculo.hash_sha256,
            ],
        }

    def executar_autorizacao_http(
        self,
        *,
        base_url: str,
        caminho: str,
        marcador: str,
        transport=None,
    ) -> dict[str, Any]:
        return executar_validacao_autorizacao_http(
            base_url=base_url,
            caminho=caminho,
            marcador=marcador,
            transport=transport,
        )


    def executar_zap(
        self,
        *,
        achado,
        sementes=None,
    ) -> dict[str, Any]:
        """Aquisição HTTP associada a hipótese originada de SARIF."""
        import hashlib
        import json
        import os
        import urllib.request

        from pathlib import Path
        from urllib.parse import urlencode

        from .zap_sarif_vinculo import (
            autorizado,
            alvo_privado,
            campo,
        )

        if not autorizado(achado):
            return {
                "executada": False,
                "motivo": "SARIF_OU_ESCOPO_NAO_AUTORIZADO",
                "evidencia_dinamica": False,
                "evidencia_oraculo": False,
                "violacao_confirmada": False,
            }

        destino = (
            alvo_privado().rstrip("/")
            + campo(achado, "caminho_http")
        )

        caminho_chave = os.getenv(
            "VERITASSEC_ZAP_API_KEY_FILE", ""
        )

        if not caminho_chave:
            raise PermissionError(
                "CHAVE_ZAP_NAO_CONFIGURADA"
            )

        arquivo_chave = Path(
            caminho_chave
        ).expanduser()

        if (
            arquivo_chave.is_symlink()
            or not arquivo_chave.is_file()
            or arquivo_chave.stat().st_mode & 0o077
        ):
            raise PermissionError("CHAVE_ZAP_INSEGURA")

        chave = arquivo_chave.read_text(
            encoding="utf-8"
        ).strip()

        if not chave:
            raise PermissionError("CHAVE_ZAP_VAZIA")

        parametros = urlencode({
            "url": destino,
            "followRedirects": "false",
        })

        requisicao = urllib.request.Request(
            "http://127.0.0.1:8090"
            "/JSON/core/action/accessUrl/?"
            + parametros,
            headers={
                "Accept": "application/json",
                "X-ZAP-API-Key": chave,
            },
        )

        opener = urllib.request.build_opener(
            urllib.request.ProxyHandler({})
        )

        with opener.open(
            requisicao,
            timeout=10,
        ) as resposta:
            if resposta.status != 200:
                raise RuntimeError(
                    "ZAP_HTTP_INVALIDO"
                )

            if "json" not in resposta.headers.get(
                "Content-Type", ""
            ).lower():
                raise RuntimeError(
                    "ZAP_RESPOSTA_NAO_JSON"
                )

            dados = json.loads(
                resposta.read(1048576).decode(
                    "utf-8"
                )
            )

        transacoes = dados.get("accessUrl")

        if (
            not isinstance(transacoes, list)
            or not transacoes
        ):
            raise RuntimeError(
                "ZAP_TRANSACAO_AUSENTE"
            )

        observacoes = []

        for transacao in transacoes:
            if not isinstance(transacao, dict):
                continue

            cabecalho = str(
                transacao.get("responseHeader", "")
            )

            linhas = cabecalho.splitlines()

            if not linhas:
                continue

            tokens = linhas[0].split()

            if (
                len(tokens) < 2
                or not tokens[0].startswith("HTTP/")
            ):
                continue

            try:
                status = int(tokens[1])
            except ValueError:
                continue

            observacoes.append({
                "status_http": status,
                "rtt": str(
                    transacao.get("rtt", "")
                ),
            })

        if not observacoes:
            raise RuntimeError(
                "ZAP_SEM_RESPOSTA_OBSERVAVEL"
            )

        evidencia = {
            "tipo": "AQUISICAO_HTTP_SARIF",
            "achado_id": str(
                campo(achado, "id")
            ),
            "regra": campo(
                achado, "regra"
            ),
            "endpoint": campo(
                achado, "caminho_http"
            ),
            "alvo": destino,
            "observacoes": observacoes,
            "procedencia": "SARIF",
            "vulnerabilidade_confirmada": False,
            "evidencia_oraculo": False,
            "active_scan": False,
            "spider": False,
        }

        serializado = json.dumps(
            evidencia,
            sort_keys=True,
            ensure_ascii=False,
        ).encode("utf-8")

        return {
            "executada": True,
            "motivo": "AQUISICAO_HTTP_SARIF",
            "evidencia_dinamica": True,
            "evidencia_oraculo": False,
            "violacao_confirmada": False,
            "vulnerabilidade_confirmada": False,
            "hash_sha256": hashlib.sha256(
                serializado
            ).hexdigest(),
            "evidencia": evidencia,
        }

    def capacidades(
        self,
    ) -> dict[str, Any]:

        return {
            nome: {
                "modulo": cap.modulo,
                "classe": cap.classe,
                "tipo": cap.tipo,
                "ativa": cap.ativa,
            }
            for nome, cap
            in self.catalogo.items()
        }
