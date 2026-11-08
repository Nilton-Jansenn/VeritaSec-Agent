from __future__ import annotations

from .contexto_expandido import (
    adquirir_contexto_expandido,
)


from typing import Any

from aplicacao.multiagente.executor import (
    ExecutorFerramentas,
)


class ExecutorAdaptativo:

    def __init__(self) -> None:
        self._executor = ExecutorFerramentas()

    def capacidades(self) -> set[str]:
        caps = self._executor.capacidades()

        if isinstance(caps, dict):
            return set(caps)

        if isinstance(caps, (list, tuple, set)):
            return set(caps)

        return set()

    def executar(
        self,
        pedido: dict[str, Any],
    ) -> dict[str, Any]:


        capacidade = str(
            pedido.get(
                "capacidade",
                "",
            )
        )

        if (
            capacidade
            == "revisao_codigo_seguro"
        ):

            achado = (
                pedido.get(
                    "achado"
                )
                or {}
            )

            metadados = (
                achado.get(
                    "metadados"
                )
                or {}
            )

            arquivo = achado.get(
                "arquivo"
            )

            linha = achado.get(
                "linha"
            )

            projeto = metadados.get(
                "projeto"
            )

            if (
                not arquivo
                or not projeto
            ):

                return {
                    "executada": False,
                    "capacidade":
                        capacidade,
                    "motivo":
                        "ESCOPO_ESTATICO_INCOMPLETO",
                    "resultado": None,
                }

            resultado = (
                adquirir_contexto_expandido(
                    arquivo=arquivo,
                    linha=linha,
                    projeto=projeto,
                )
            )

            return {
                "executada":
                    bool(
                        resultado.get(
                            "executada"
                        )
                    ),

                "capacidade":
                    capacidade,

                "motivo":
                    (
                        "EVIDENCIA_ESTATICA_ADQUIRIDA"
                        if resultado.get(
                            "executada"
                        )
                        else resultado.get(
                            "motivo"
                        )
                    ),

                "resultado":
                    resultado,
            }

        capacidade = pedido["capacidade"]
        contexto = pedido.get("contexto", {}) or {}
        sementes = list(
            pedido.get("sementes", [])
        )

        if capacidade in {
            "path_traversal",
            "busca_evolucionaria",
        }:
            raiz = contexto.get("raiz_sandbox")

            if not raiz:
                return {
                    "executada": False,
                    "motivo": "RAIZ_SANDBOX_AUSENTE",
                }

            if not sementes:
                sementes = ["../fora.txt"]

            return self._executor.executar_path_traversal(
                hipotese_id=str(
                    contexto.get(
                        "hipotese_id",
                        "adaptativa",
                    )
                ),
                raiz_sandbox=str(raiz),
                sementes=sementes,
                max_geracoes=int(
                    contexto.get(
                        "max_geracoes",
                        6,
                    )
                ),
            )

        if capacidade == "busca_codigo":
            arquivo = contexto.get("arquivo")

            if not arquivo:
                return {
                    "executada": False,
                    "motivo": "ARQUIVO_AUSENTE",
                }

            return self._executor.adquirir_contexto_codigo(
                arquivo=str(arquivo),
                linha=contexto.get("linha"),
            )

        if capacidade == "autorizacao_http":
            base_url = contexto.get("base_url")
            caminho = contexto.get("caminho")
            marcador = contexto.get("marcador")

            if not all(
                (base_url, caminho, marcador)
            ):
                return {
                    "executada": False,
                    "motivo": "CONTEXTO_HTTP_INCOMPLETO",
                }

            return self._executor.executar_autorizacao_http(
                base_url=str(base_url),
                caminho=str(caminho),
                marcador=str(marcador),
            )

        return {
            "executada": False,
            "motivo": "CAPACIDADE_NAO_IMPLEMENTADA",
            "capacidade": capacidade,
        }
