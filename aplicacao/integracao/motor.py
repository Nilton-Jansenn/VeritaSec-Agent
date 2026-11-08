from __future__ import annotations

from pathlib import Path

from aplicacao.agentes.critico import (
    CriticoAdversarial,
)
from aplicacao.dominio.modelos import (
    EscopoAutorizado,
    EstadoInvestigacaoPersistido,
    ReferenciaAchado,
)
from aplicacao.investigacao.lacunas import (
    identificar_lacunas,
)
from aplicacao.investigacao.motor import (
    MotorInvestigacao,
)
from aplicacao.investigacao.proveniencia import (
    criar_registro,
)
from aplicacao.investigacao.vereditos import (
    pode_confirmar_explorabilidade,
)
from aplicacao.persistencia.investigacoes import (
    RepositorioInvestigacoesJson,
)

from .correlacao import correlacionar
from .modelos import (
    EstadoEtapaM6,
    RegistroEtapaM6,
    ResultadoPipelineM6,
    TipoValidacaoM6,
)
from .path_traversal import (
    IntegradorPathTraversal,
)
from .autorizacao_http import (
    IntegradorAutorizacaoHttp,
)


class MotorIntegracaoM6:

    def __init__(
        self,
        raiz_projeto: str | Path,
        diretorio_estado: str | Path,
        orquestrador=None,
    ) -> None:

        self.raiz_projeto = Path(
            raiz_projeto
        ).resolve()

        self.repositorio = (
            RepositorioInvestigacoesJson(
                diretorio_estado
            )
        )

        self.motor = MotorInvestigacao(
            raiz_projeto=self.raiz_projeto,
            repositorio=self.repositorio,
            orquestrador=orquestrador,
        )

        self.critico = CriticoAdversarial()

    async def iniciar(
        self,
        achado: ReferenciaAchado,
        escopo: EscopoAutorizado,
    ) -> EstadoInvestigacaoPersistido:

        return await self.motor.criar(
            achado=achado,
            escopo=escopo,
        )

    def adquirir_evidencia_estatica(
        self,
        estado: EstadoInvestigacaoPersistido,
        max_acoes: int = 10,
    ) -> EstadoInvestigacaoPersistido:

        for _ in range(max_acoes):

            plano = estado.investigacao.plano

            if not plano:
                break

            pendentes_antes = [
                a.id
                for a in plano.acoes
                if a.estado.value == "planejada"
            ]

            if not pendentes_antes:
                break

            estado = (
                self.motor.executar_proxima_acao(
                    estado
                )
            )

            pendentes_depois = [
                a.id
                for a in plano.acoes
                if a.estado.value == "planejada"
            ]

            if (
                pendentes_depois
                == pendentes_antes
            ):
                break

        estado.lacunas = identificar_lacunas(
            estado.investigacao
        )

        self.repositorio.salvar(
            estado
        )

        return estado

    def validar_path_traversal(
        self,
        estado: EstadoInvestigacaoPersistido,
        raiz_harness: str | Path,
    ) -> bool:

        violado = IntegradorPathTraversal(
            raiz_harness
        ).executar(
            estado.investigacao
        )

        estado.proveniencia.append(
            criar_registro(
                estado.investigacao.id,
                "validar_path_traversal",
                "IntegradorPathTraversal",
                str(raiz_harness),
                f"violado={violado}",
                True,
            )
        )

        self.repositorio.salvar(
            estado
        )

        return violado

    async def validar_autorizacao_http(
        self,
        estado: EstadoInvestigacaoPersistido,
        app,
        caminho: str,
        marcador: str,
    ) -> bool:

        violado = await (
            IntegradorAutorizacaoHttp(
                app
            ).executar(
                investigacao=estado.investigacao,
                caminho=caminho,
                marcador=marcador,
            )
        )

        estado.proveniencia.append(
            criar_registro(
                estado.investigacao.id,
                "validar_autorizacao_http",
                "IntegradorAutorizacaoHttp",
                caminho,
                f"violado={violado}",
                True,
            )
        )

        self.repositorio.salvar(
            estado
        )

        return violado

    def consolidar(
        self,
        estado: EstadoInvestigacaoPersistido,
        propriedade_violada: bool,
        validacoes: list[TipoValidacaoM6],
    ) -> ResultadoPipelineM6:

        correlacao = correlacionar(
            estado.investigacao
        )

        confirmacao = (
            propriedade_violada
            and pode_confirmar_explorabilidade(
                estado.investigacao
            )
        )

        decisao_critico = (
            self.critico.revisar(
                estado.investigacao
            )
        )

        etapas = [
            RegistroEtapaM6(
                etapa="correlacao",
                estado=EstadoEtapaM6.EXECUTADA,
                componente="correlacionar",
                resumo=(
                    "evidências estática, dinâmica "
                    "e de oráculo correlacionadas"
                ),
                metadados={
                    "possui_estatica": (
                        correlacao.possui_estatica
                    ),
                    "possui_dinamica": (
                        correlacao.possui_dinamica
                    ),
                    "possui_oraculo": (
                        correlacao.possui_oraculo
                    ),
                },
            ),
            RegistroEtapaM6(
                etapa="critico_adversarial",
                estado=EstadoEtapaM6.EXECUTADA,
                componente="CriticoAdversarial",
                resumo=(
                    decisao_critico
                    .justificativa_resumida
                ),
                metadados={
                    "evidencia_suficiente": (
                        decisao_critico
                        .evidencia_suficiente
                    ),
                    "conflitos": (
                        decisao_critico.conflitos
                    ),
                    "evidencias_ausentes": (
                        decisao_critico
                        .evidencias_ausentes
                    ),
                },
            ),
        ]

        resultado = ResultadoPipelineM6(
            investigacao=estado,
            etapas=etapas,
            evidencia_dinamica=(
                correlacao.possui_dinamica
            ),
            evidencia_oraculo=(
                correlacao.possui_oraculo
            ),
            propriedade_violada=(
                propriedade_violada
            ),
            confirmacao_permitida=confirmacao,
            validacoes_executadas=validacoes,
            observacoes=[
                (
                    "confirmação exige execução "
                    "dinâmica + oráculo determinístico"
                ),
                (
                    "resultado de fixture/harness "
                    "não implica explorabilidade de "
                    "alvo externo"
                ),
            ],
        )

        self.repositorio.salvar(
            estado
        )

        return resultado
