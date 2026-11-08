"""Motor coordenador da investigação adaptativa."""

from __future__ import annotations

from pathlib import Path

from aplicacao.dominio.enums import (
    EstadoAcao,
    EstadoInvestigacao,
    TipoEvidencia,
)
from aplicacao.dominio.modelos import (
    EscopoAutorizado,
    EstadoInvestigacaoPersistido,
    Evidencia,
    Investigacao,
    ReferenciaAchado,
)
from aplicacao.ferramentas.codigo import FerramentaCodigo
from aplicacao.investigacao.evidencias import hash_evidencia
from aplicacao.investigacao.lacunas import identificar_lacunas
from aplicacao.investigacao.planejador import PlanejadorAdaptativo
from aplicacao.investigacao.proveniencia import criar_registro
from aplicacao.investigacao.servico import ServicoInvestigacao
from aplicacao.orquestracao.deterministico import (
    OrquestradorDeterministico,
)
from aplicacao.persistencia.investigacoes import (
    RepositorioInvestigacoesJson,
)
from aplicacao.revisao_codigo.motor import (
    MotorRevisaoCodigoSeguro,
)


class MotorInvestigacao:

    def __init__(
        self,
        raiz_projeto: str | Path,
        repositorio: RepositorioInvestigacoesJson,
        orquestrador=None,
    ) -> None:

        self.raiz_projeto = Path(
            raiz_projeto
        ).resolve()

        self.repositorio = repositorio

        self.orquestrador = (
            orquestrador
            or OrquestradorDeterministico()
        )

        self.servico = ServicoInvestigacao()

        self.codigo = FerramentaCodigo(
            self.raiz_projeto
        )

        self.revisor = MotorRevisaoCodigoSeguro(
            self.codigo
        )

    async def criar(
        self,
        achado: ReferenciaAchado,
        escopo: EscopoAutorizado,
    ) -> EstadoInvestigacaoPersistido:

        investigacao = Investigacao(
            achado=achado,
            escopo=escopo,
        )

        hipotese = await (
            self.orquestrador.formular_hipotese(
                investigacao
            )
        )

        investigacao.hipotese = hipotese
        investigacao.estado = (
            EstadoInvestigacao.HIPOTESE_FORMULADA
        )

        lacunas = identificar_lacunas(
            investigacao
        )

        investigacao.plano = (
            PlanejadorAdaptativo().planejar(
                investigacao,
                lacunas,
            )
        )

        proveniencia = [
            criar_registro(
                investigacao.id,
                "formular_hipotese",
                type(
                    self.orquestrador
                ).__name__,
                achado.regra,
                hipotese.tipo,
                True,
            )
        ]

        estado = EstadoInvestigacaoPersistido(
            investigacao=investigacao,
            lacunas=lacunas,
            proveniencia=proveniencia,
        )

        self.repositorio.salvar(
            estado
        )

        return estado

    def executar_proxima_acao(
        self,
        estado: EstadoInvestigacaoPersistido,
    ) -> EstadoInvestigacaoPersistido:

        investigacao = estado.investigacao

        if not investigacao.plano:
            return estado

        for acao in investigacao.plano.acoes:

            if acao.estado.value != "planejada":
                continue

            decisao = self.servico.autorizar_acao(
                investigacao,
                acao,
            )

            if not decisao.autorizada:
                estado.proveniencia.append(
                    criar_registro(
                        investigacao.id,
                        "bloquear_acao",
                        "PoliticaExecucao",
                        acao.ferramenta,
                        decisao.motivo,
                        False,
                    )
                )
                continue

            if acao.ferramenta == "busca_codigo":
                try:
                    conteudo = self.codigo.ler(
                        investigacao.achado.arquivo
                    )

                    observacao = (
                        f"arquivo lido com "
                        f"{len(conteudo)} caracteres"
                    )

                    evidencia = Evidencia(
                        hipotese_id=(
                            investigacao.hipotese.id
                            if investigacao.hipotese
                            else investigacao.achado.id
                        ),
                        tipo=TipoEvidencia.CONTEXTO_CODIGO,
                        origem="busca_codigo",
                        descricao=(
                            "contexto do arquivo reportado"
                        ),
                        observacao=observacao,
                        hash_sha256=hash_evidencia(
                            conteudo
                        ),
                        reproduzivel=True,
                    )

                    self.servico.registrar_evidencia(
                        investigacao,
                        evidencia,
                    )

                    acao.estado = EstadoAcao.EXECUTADA

                    estado.proveniencia.append(
                        criar_registro(
                            investigacao.id,
                            "executar_ferramenta",
                            "FerramentaCodigo",
                            investigacao.achado.arquivo,
                            observacao,
                            True,
                        )
                    )

                except Exception as exc:
                    acao.estado = EstadoAcao.FALHOU

                    estado.proveniencia.append(
                        criar_registro(
                            investigacao.id,
                            "executar_ferramenta",
                            "FerramentaCodigo",
                            investigacao.achado.arquivo,
                            type(exc).__name__,
                            False,
                        )
                    )

                break

            if acao.ferramenta == "revisao_codigo_seguro":
                try:
                    resultado = self.revisor.revisar(
                        investigacao.achado.arquivo
                    )

                    serializado = (
                        resultado.model_dump_json()
                    )

                    evidencia = Evidencia(
                        hipotese_id=(
                            investigacao.hipotese.id
                            if investigacao.hipotese
                            else investigacao.achado.id
                        ),
                        tipo=(
                            TipoEvidencia
                            .REVISAO_CODIGO_SEGURO
                        ),
                        origem=(
                            "revisao_codigo_seguro"
                        ),
                        descricao=(
                            "observações estruturais "
                            "de controles de segurança"
                        ),
                        observacao=serializado,
                        hash_sha256=hash_evidencia(
                            resultado.model_dump()
                        ),
                        reproduzivel=True,
                    )

                    self.servico.registrar_evidencia(
                        investigacao,
                        evidencia,
                    )

                    acao.estado = EstadoAcao.EXECUTADA

                    estado.proveniencia.append(
                        criar_registro(
                            investigacao.id,
                            "executar_ferramenta",
                            (
                                "MotorRevisaoCodigoSeguro"
                            ),
                            investigacao.achado.arquivo,
                            "revisão concluída",
                            True,
                        )
                    )

                except Exception as exc:
                    acao.estado = EstadoAcao.FALHOU

                    estado.proveniencia.append(
                        criar_registro(
                            investigacao.id,
                            "executar_ferramenta",
                            (
                                "MotorRevisaoCodigoSeguro"
                            ),
                            investigacao.achado.arquivo,
                            type(exc).__name__,
                            False,
                        )
                    )

                break

            # Ferramentas dinâmicas são deliberadamente
            # deixadas para a etapa especializada posterior.
            estado.proveniencia.append(
                criar_registro(
                    investigacao.id,
                    "acao_nao_executada",
                    "MotorInvestigacao",
                    acao.ferramenta,
                    (
                        "executor especializado ainda "
                        "não registrado"
                    ),
                    False,
                )
            )

            break

        self.repositorio.salvar(
            estado
        )

        return estado
