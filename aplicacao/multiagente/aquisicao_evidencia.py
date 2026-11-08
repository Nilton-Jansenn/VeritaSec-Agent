from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import Any


@dataclass
class OrcamentoInvestigacao:
    max_acoes: int = 8
    max_sementes_por_acao: int = 16
    acoes_executadas: int = 0
    acoes_negadas: int = 0
    erros: int = 0

    def pode_executar(
        self,
    ) -> bool:
        return (
            self.acoes_executadas
            < self.max_acoes
        )


def _serializar(
    valor: Any,
) -> Any:

    if valor is None:
        return None

    if isinstance(
        valor,
        (
            str,
            int,
            float,
            bool,
        ),
    ):
        return valor

    if isinstance(
        valor,
        dict,
    ):
        return {
            str(k): _serializar(v)
            for k, v in valor.items()
        }

    if isinstance(
        valor,
        (
            list,
            tuple,
            set,
        ),
    ):
        return [
            _serializar(x)
            for x in valor
        ]

    if hasattr(
        valor,
        "model_dump",
    ):
        try:
            return _serializar(
                valor.model_dump()
            )
        except Exception:
            pass

    if hasattr(
        valor,
        "__dict__",
    ):
        try:
            return _serializar(
                vars(valor)
            )
        except Exception:
            pass

    return repr(valor)


class ExecutorAquisicaoEvidencia:

    def __init__(
        self,
        executor: Any,
        *,
        orcamento: (
            OrcamentoInvestigacao
            | None
        ) = None,
    ):
        self.executor = executor

        self.orcamento = (
            orcamento
            or OrcamentoInvestigacao()
        )

    def _resolver(
        self,
        capacidade: str,
    ):
        """
        Resolve SOMENTE capacidades declaradas.

        Nunca resolve atributos arbitrários oriundos da LLM.
        """

        mapa = {
            "busca_codigo": (
                "busca_codigo",
                "buscar_codigo",
                "executar_busca_codigo",
            ),
            "revisao_codigo_seguro": (
                "revisao_codigo_seguro",
                "revisar_codigo_seguro",
            ),
            "path_traversal": (
                "path_traversal",
                "validar_path_traversal",
                "executar_path_traversal",
            ),
            "busca_evolucionaria": (
                "busca_evolucionaria",
                "executar_busca_evolutiva",
                "executar_busca_evolucionaria",
            ),
            "runtime_http": (
                "runtime_http",
                "executar_http",
                "executar_runtime_http",
            ),
            "autorizacao_http": (
                "autorizacao_http",
                "validar_autorizacao_http",
                "executar_autorizacao_http",
            ),
            "zap": (
                "zap",
                "executar_zap",
            ),
            "oraculo_path_traversal": (
                "oraculo_path_traversal",
                "executar_oraculo_path_traversal",
            ),
            "oraculo_autorizacao": (
                "oraculo_autorizacao",
                "executar_oraculo_autorizacao",
            ),
            "proveniencia": (
                "proveniencia",
                "registrar_proveniencia",
            ),
        }

        for nome in mapa.get(
            capacidade,
            (),
        ):
            metodo = getattr(
                self.executor,
                nome,
                None,
            )

            if callable(metodo):
                return metodo

        # Dispatcher genérico somente se já fizer parte
        # do executor operacional.
        for nome in (
            "executar_capacidade",
            "executar",
        ):
            metodo = getattr(
                self.executor,
                nome,
                None,
            )

            if callable(metodo):
                return metodo

        return None

    def _invocar(
        self,
        metodo,
        *,
        capacidade: str,
        achado: Any,
        sementes: list[str],
    ) -> Any:

        assinatura = inspect.signature(
            metodo
        )

        params = assinatura.parameters

        kwargs = {}

        valores = {
            "capacidade":
                capacidade,
            "achado":
                achado,
            "sementes":
                sementes,
            "seeds":
                sementes,
            "entrada":
                (
                    sementes[0]
                    if sementes
                    else ""
                ),
            "hipotese_id":
                getattr(
                    achado,
                    "id",
                    "investigacao",
                ),
        }

        for nome, valor in (
            valores.items()
        ):
            if nome in params:
                kwargs[nome] = valor

        if kwargs:
            return metodo(
                **kwargs
            )

        nome_metodo = getattr(
            metodo,
            "__name__",
            "",
        )

        if nome_metodo in {
            "executar",
            "executar_capacidade",
        }:
            return metodo(
                capacidade
            )

        raise TypeError(
            "CONTRATO_EXECUTOR_NAO_SUPORTADO:"
            + capacidade
        )

    def executar_plano(
        self,
        *,
        achado: Any,
        plano: dict[str, Any],
    ) -> dict[str, Any]:

        resultados = []

        criterio_parada = (
            "PLANO_CONCLUIDO"
        )
        # O limite contabiliza tentativas reais, inclusive erros.
        tentativas_ferramentas = 0

        for decisao in plano.get(
            "decisoes_politica",
            [],
        ):
            capacidade = str(
                decisao.get(
                    "capacidade",
                    "",
                )
            )

            autorizada = bool(
                decisao.get(
                    "autorizada",
                    False,
                )
            )

            motivo = str(
                decisao.get(
                    "motivo",
                    "",
                )
            )

            sementes = [
                str(x)
                for x in decisao.get(
                    "sementes",
                    [],
                )
            ][
                :self.orcamento
                .max_sementes_por_acao
            ]

            if not autorizada:
                self.orcamento.acoes_negadas += 1

                resultados.append({
                    "capacidade":
                        capacidade,
                    "autorizada":
                        False,
                    "executada":
                        False,
                    "motivo":
                        motivo,
                    "sementes": [],
                    "resultado": None,
                })

                continue

            if tentativas_ferramentas >= self.orcamento.max_acoes:
                criterio_parada = (
                    "ORCAMENTO_ESGOTADO"
                )
                break

            metodo = self._resolver(
                capacidade
            )

            if metodo is None:
                resultados.append({
                    "capacidade":
                        capacidade,
                    "autorizada":
                        True,
                    "executada":
                        False,
                    "motivo":
                        "FERRAMENTA_INDISPONIVEL",
                    "sementes":
                        sementes,
                    "resultado": None,
                })

                continue

            tentativas_ferramentas += 1
            try:
                retorno = self._invocar(
                    metodo,
                    capacidade=capacidade,
                    achado=achado,
                    sementes=sementes,
                )

                if inspect.isawaitable(
                    retorno
                ):
                    if hasattr(
                        retorno,
                        "close",
                    ):
                        retorno.close()

                    resultados.append({
                        "capacidade":
                            capacidade,
                        "autorizada":
                            True,
                        "executada":
                            False,
                        "motivo":
                            "INTEGRADOR_ASSINCRONO_REQUERIDO",
                        "sementes":
                            sementes,
                        "resultado":
                            None,
                    })

                    continue

                # VERITASSEC_PASSO02_STATUS_REAL
                # Respeitar executada=False de QUALQUER
                # ferramenta, inclusive das estaticas.
                executada_real = (
                    retorno.get("executada", True)
                    if isinstance(retorno, dict)
                    else True
                )
                if executada_real:
                    self.orcamento.acoes_executadas += 1
                else:
                    self.orcamento.acoes_negadas += 1

                resultados.append({
                    "capacidade":
                        capacidade,
                    "autorizada":
                        True,
                    "executada":
                        bool(executada_real),
                    "motivo":
                        (
                            "EXECUTADA"
                            if executada_real
                            else str(
                                retorno.get(
                                    "motivo",
                                    "NAO_EXECUTADA",
                                )
                            )
                        ),
                    "sementes":
                        sementes,
                    "resultado":
                        _serializar(
                            retorno
                        ),
                })

            except Exception as exc:
                self.orcamento.erros += 1

                resultados.append({
                    "capacidade":
                        capacidade,
                    "autorizada":
                        True,
                    "executada":
                        False,
                    "motivo":
                        "ERRO_DE_EXECUCAO",
                    "sementes":
                        sementes,
                    "resultado":
                        None,
                    "erro": (
                        type(exc).__name__
                        + ": "
                        + str(exc)
                    )[:2000],
                })

        return {
            "criterio_parada":
                criterio_parada,
            "orcamento": {
                "max_acoes":
                    self.orcamento.max_acoes,
                "acoes_executadas":
                    self.orcamento.acoes_executadas,
                "acoes_negadas":
                    self.orcamento.acoes_negadas,
                "erros":
                    self.orcamento.erros,
            },
            "resultados":
                resultados,
        }
