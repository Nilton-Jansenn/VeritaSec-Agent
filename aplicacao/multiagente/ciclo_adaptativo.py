from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass(slots=True)
class OrcamentoAdaptativo:
    max_rodadas: int = 3
    max_acoes: int = 8
    rodadas_executadas: int = 0
    acoes_executadas: int = 0
    acoes_negadas: int = 0
    erros: int = 0

    def permite_rodada(self) -> bool:
        return self.rodadas_executadas < self.max_rodadas

    def permite_acao(self) -> bool:
        return self.acoes_executadas < self.max_acoes

    def registrar_rodada(self) -> None:
        self.rodadas_executadas += 1

    def registrar_execucao(self) -> None:
        self.acoes_executadas += 1

    def registrar_negacao(self) -> None:
        self.acoes_negadas += 1

    def registrar_erro(self) -> None:
        self.erros += 1

    def dump(self) -> dict[str, int]:
        return {
            "max_rodadas": self.max_rodadas,
            "max_acoes": self.max_acoes,
            "rodadas_executadas": self.rodadas_executadas,
            "acoes_executadas": self.acoes_executadas,
            "acoes_negadas": self.acoes_negadas,
            "erros": self.erros,
        }


@dataclass(slots=True)
class EvidenciaAdaptativa:
    rodada: int
    capacidade: str
    observavel: bool
    violacao: bool
    resultado: Any = None
    hash_evidencia: str | None = None

    def dump(self) -> dict[str, Any]:
        return {
            "rodada": self.rodada,
            "capacidade": self.capacidade,
            "observavel": self.observavel,
            "violacao": self.violacao,
            "resultado": self.resultado,
            "hash_evidencia": self.hash_evidencia,
        }


@dataclass(slots=True)
class RodadaAdaptativa:
    numero: int
    hipoteses: list[str] = field(default_factory=list)
    lacunas: list[str] = field(default_factory=list)
    estrategia: str | None = None
    sementes: list[str] = field(default_factory=list)
    capacidades_solicitadas: list[str] = field(default_factory=list)
    capacidades_autorizadas: list[str] = field(default_factory=list)
    evidencias: list[EvidenciaAdaptativa] = field(default_factory=list)

    def dump(self) -> dict[str, Any]:
        return {
            "numero": self.numero,
            "hipoteses": self.hipoteses,
            "lacunas": self.lacunas,
            "estrategia": self.estrategia,
            "sementes": self.sementes,
            "capacidades_solicitadas": self.capacidades_solicitadas,
            "capacidades_autorizadas": self.capacidades_autorizadas,
            "evidencias": [e.dump() for e in self.evidencias],
        }


@dataclass(slots=True)
class ResultadoCicloAdaptativo:
    rodadas: list[RodadaAdaptativa]
    orcamento: OrcamentoAdaptativo
    criterio_parada: str
    estado_sugerido: str
    evidencia_confirmatoria: bool

    def dump(self) -> dict[str, Any]:
        return {
            "rodadas": [r.dump() for r in self.rodadas],
            "orcamento": self.orcamento.dump(),
            "criterio_parada": self.criterio_parada,
            "estado_sugerido": self.estado_sugerido,
            "evidencia_confirmatoria": self.evidencia_confirmatoria,
        }


class CicloAdaptativoInvestigacao:

    def __init__(
        self,
        *,
        planejar: Callable[[dict[str, Any]], dict[str, Any]],
        autorizar: Callable[[dict[str, Any]], dict[str, Any]],
        executar: Callable[[dict[str, Any]], dict[str, Any]],
        avaliar_oraculo: Callable[[dict[str, Any]], dict[str, Any]],
        max_rodadas: int = 3,
        max_acoes: int = 8,
    ) -> None:

        self._planejar = planejar
        self._autorizar = autorizar
        self._executar = executar
        self._avaliar_oraculo = avaliar_oraculo

        self._orcamento = OrcamentoAdaptativo(
            max_rodadas=max_rodadas,
            max_acoes=max_acoes,
        )

    def executar(
        self,
        contexto: dict[str, Any],
    ) -> ResultadoCicloAdaptativo:

        rodadas: list[RodadaAdaptativa] = []

        criterio = "EVIDENCIA_INSUFICIENTE"
        estado = "INCONCLUSIVO"
        confirmado = False

        memoria = dict(contexto)

        while self._orcamento.permite_rodada():

            self._orcamento.registrar_rodada()

            numero = self._orcamento.rodadas_executadas

            plano = self._planejar(memoria) or {}

            rodada = RodadaAdaptativa(
                numero=numero,
                hipoteses=list(plano.get("hipoteses", [])),
                lacunas=list(plano.get("lacunas", [])),
                estrategia=plano.get("estrategia"),
                sementes=list(plano.get("sementes", [])),
                capacidades_solicitadas=list(
                    plano.get("capacidades", [])
                ),
            )

            decisao = self._autorizar(
                {
                    "contexto": memoria,
                    "plano": plano,
                }
            ) or {}

            autorizadas = list(
                decisao.get(
                    "capacidades_autorizadas",
                    [],
                )
            )

            rodada.capacidades_autorizadas = autorizadas

            if not autorizadas:
                self._orcamento.registrar_negacao()
                rodadas.append(rodada)

                criterio = decisao.get(
                    "criterio",
                    "ACAO_NAO_AUTORIZADA",
                )

                estado = "INCONCLUSIVO"
                break

            houve_execucao = False

            for capacidade in autorizadas:

                if not self._orcamento.permite_acao():
                    criterio = "ORCAMENTO_ESGOTADO"
                    break

                pedido = {
                    "capacidade": capacidade,
                    "sementes": rodada.sementes,
                    "contexto": memoria,
                    "rodada": numero,
                }

                try:
                    resultado = self._executar(pedido) or {}
                    self._orcamento.registrar_execucao()
                    houve_execucao = True

                except Exception as exc:
                    self._orcamento.registrar_erro()
                    resultado = {
                        "erro": repr(exc)
                    }

                oracle = self._avaliar_oraculo(
                    {
                        "capacidade": capacidade,
                        "resultado": resultado,
                        "contexto": memoria,
                    }
                ) or {}

                evidencia = EvidenciaAdaptativa(
                    rodada=numero,
                    capacidade=capacidade,
                    observavel=bool(
                        oracle.get("observavel", False)
                    ),
                    violacao=bool(
                        oracle.get("violacao", False)
                    ),
                    resultado=resultado,
                    hash_evidencia=oracle.get(
                        "hash_evidencia"
                    ),
                )

                rodada.evidencias.append(evidencia)

                if (
                    evidencia.observavel
                    and evidencia.violacao
                ):
                    confirmado = True
                    estado = "REPRODUZIDO_DINAMICAMENTE"
                    criterio = "EVIDENCIA_SUFICIENTE_CONFIRMADA"
                    break

            rodadas.append(rodada)

            memoria["evidencias_adquiridas"] = [
                e.dump()
                for r in rodadas
                for e in r.evidencias
            ]

            if confirmado:
                break

            if not self._orcamento.permite_acao():
                criterio = "ORCAMENTO_ESGOTADO"
                estado = "INCONCLUSIVO"
                break

            if not houve_execucao:
                criterio = "EVIDENCIA_INSUFICIENTE"
                estado = "INCONCLUSIVO"
                break

            criterio = "NOVA_RODADA_NECESSARIA"

        else:
            criterio = "ORCAMENTO_ESGOTADO"

        return ResultadoCicloAdaptativo(
            rodadas=rodadas,
            orcamento=self._orcamento,
            criterio_parada=criterio,
            estado_sugerido=estado,
            evidencia_confirmatoria=confirmado,
        )
