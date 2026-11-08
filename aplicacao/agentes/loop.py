"""Loop de investigação com orçamento e parada determinística."""

from __future__ import annotations

from aplicacao.agentes.critico import CriticoAdversarial
from aplicacao.dominio.enums import EstadoAcao
from aplicacao.dominio.modelos import (
    EstadoInvestigacaoPersistido,
    EstadoLoopAutonomo,
)
from aplicacao.investigacao.motor import MotorInvestigacao


class LoopInvestigacao:

    def __init__(
        self,
        motor: MotorInvestigacao,
        max_iteracoes: int = 10,
    ) -> None:

        if max_iteracoes < 1:
            raise ValueError(
                "max_iteracoes deve ser >= 1"
            )

        self.motor = motor
        self.max_iteracoes = max_iteracoes
        self.critico = CriticoAdversarial()

    def executar(
        self,
        estado: EstadoInvestigacaoPersistido,
    ) -> tuple[
        EstadoInvestigacaoPersistido,
        EstadoLoopAutonomo,
    ]:

        loop = EstadoLoopAutonomo()

        for numero in range(
            1,
            self.max_iteracoes + 1,
        ):
            loop.iteracao = numero

            if (
                estado.investigacao.orcamento
                .acoes_consumidas
                >= estado.investigacao.orcamento.max_acoes
            ):
                loop.encerrado = True
                loop.motivo = "orcamento_esgotado"
                break

            pendentes = []

            if estado.investigacao.plano:
                pendentes = [
                    acao
                    for acao
                    in estado.investigacao.plano.acoes
                    if acao.estado
                    == EstadoAcao.PLANEJADA
                ]

            if not pendentes:
                loop.encerrado = True
                loop.motivo = "sem_acoes_pendentes"
                break

            antes = len(
                estado.investigacao.evidencias
            )

            estado = (
                self.motor.executar_proxima_acao(
                    estado
                )
            )

            estado.investigacao.orcamento.acoes_consumidas += 1

            depois = len(
                estado.investigacao.evidencias
            )

            loop.ultima_acao = (
                pendentes[0].ferramenta
            )

            decisao = self.critico.revisar(
                estado.investigacao
            )

            if (
                decisao.evidencia_suficiente
                and depois > antes
            ):
                loop.encerrado = True
                loop.motivo = (
                    "evidencia_estatica_suficiente"
                )
                break

        if not loop.encerrado:
            loop.encerrado = True
            loop.motivo = "limite_iteracoes"

        self.motor.repositorio.salvar(
            estado
        )

        return estado, loop
