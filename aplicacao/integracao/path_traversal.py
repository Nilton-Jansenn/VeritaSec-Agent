from __future__ import annotations

from pathlib import Path

from aplicacao.dinamica.executor import (
    ExecutorArquivoControlado,
)
from aplicacao.dinamica.servico import (
    ValidadorPathTraversal,
)
from aplicacao.dominio.modelos import Investigacao
from aplicacao.evolucao.modelos import (
    ConfiguracaoEvolutiva,
)
from aplicacao.evolucao.path_traversal import (
    BuscaEvolutivaPathTraversal,
)

from .evidencias_runtime import (
    RegistradorEvidenciaRuntime,
)


class IntegradorPathTraversal:

    def __init__(
        self,
        raiz_autorizada: str | Path,
    ) -> None:

        self.raiz = Path(
            raiz_autorizada
        ).resolve()

        self.registrador = (
            RegistradorEvidenciaRuntime()
        )

    def executar(
        self,
        investigacao: Investigacao,
        sementes: list[str] | None = None,
    ) -> bool:

        if (
            not investigacao.escopo
            .execucao_dinamica_permitida
        ):
            raise PermissionError(
                "execução dinâmica não autorizada"
            )

        busca = BuscaEvolutivaPathTraversal(
            self.raiz,
            ConfiguracaoEvolutiva(
                max_geracoes=4,
                tamanho_populacao=8,
                semente_aleatoria=2026,
                parar_ao_confirmar=True,
            ),
        )

        resultado_busca = busca.executar(
            sementes
            or [
                "arquivo.txt",
                "sub/arquivo.txt",
            ]
        )

        entrada = resultado_busca.melhor.valor

        executor = ExecutorArquivoControlado(
            self.raiz
        )

        validador = ValidadorPathTraversal(
            executor
        )

        evidencias = validador.validar(
            investigacao.hipotese.id
            if investigacao.hipotese
            else investigacao.achado.id,
            entrada,
        )

        violado = False

        for evidencia in evidencias:
            if evidencia.tipo.value == "oraculo":
                violado = bool(
                    evidencia.metadados.get(
                        "violacao_confirmada",
                        False,
                    )
                )

        self.registrador.registrar_dinamica(
            investigacao=investigacao,
            origem="m6_busca_evolutiva_path_traversal",
            descricao=(
                "execução limitada de busca evolucionária "
                "sobre harness local autorizado"
            ),
            observacao=(
                "melhor entrada="
                + entrada
                + "; execucoes="
                + str(resultado_busca.execucoes)
            ),
            metadados={
                "geracoes": (
                    resultado_busca
                    .geracoes_executadas
                ),
                "execucoes": resultado_busca.execucoes,
                "aptidao": (
                    resultado_busca.melhor.aptidao
                ),
                "semente_aleatoria": 2026,
            },
        )

        self.registrador.registrar_oraculo(
            investigacao=investigacao,
            origem="m6_oraculo_path_traversal",
            propriedade=(
                "caminho controlável não deve resolver "
                "recurso fora da raiz autorizada"
            ),
            observacao=(
                "violacao_confirmada="
                + str(violado)
            ),
            violado=violado,
            metadados={
                "entrada": entrada,
                "raiz_autorizada": str(
                    self.raiz
                ),
            },
        )

        return violado
