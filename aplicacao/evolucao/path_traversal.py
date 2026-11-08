from __future__ import annotations

import random
from pathlib import Path

from .modelos import (
    CasoDeTeste,
    ConfiguracaoEvolutiva,
    ResultadoEvolutivo,
)


class BuscaEvolutivaPathTraversal:
    """
    Busca limitada para um harness local controlado.

    Não executa rede, shell ou aplicações externas.
    O objetivo é validar o mecanismo evolutivo e
    o oráculo dentro de um ambiente autorizado.
    """

    MUTACOES = (
        "../",
        "..//",
        "./../",
        "sub/../../",
    )

    def __init__(
        self,
        raiz_autorizada: str | Path,
        configuracao: ConfiguracaoEvolutiva
        | None = None,
    ) -> None:

        self.raiz = Path(
            raiz_autorizada
        ).resolve()

        self.config = (
            configuracao
            or ConfiguracaoEvolutiva()
        )

        self.random = random.Random(
            self.config.semente_aleatoria
        )

    def _viola_propriedade(
        self,
        valor: str,
    ) -> bool:

        resolvido = (
            self.raiz / valor
        ).resolve()

        try:
            resolvido.relative_to(
                self.raiz
            )

            return False

        except ValueError:
            return True

    def _aptidao(
        self,
        valor: str,
    ) -> float:

        if self._viola_propriedade(
            valor
        ):
            return 1.0

        score = 0.0

        if ".." in valor:
            score += 0.4

        if "/" in valor:
            score += 0.2

        profundidade = valor.count(
            "../"
        )

        score += min(
            profundidade * 0.1,
            0.3,
        )

        return min(
            score,
            0.99,
        )

    # VERITASSEC_ETAPA2_CRUZAMENTO
    def _cruzar(
        self,
        pai: CasoDeTeste,
        mae: CasoDeTeste,
        geracao: int,
    ) -> CasoDeTeste:

        ponto_pai = self.random.randint(
            0, len(pai.valor)
        )

        ponto_mae = self.random.randint(
            0, len(mae.valor)
        )

        valor = (
            pai.valor[:ponto_pai]
            + mae.valor[ponto_mae:]
        )

        if not valor:
            valor = pai.valor or mae.valor

        return CasoDeTeste(
            valor=valor,
            geracao=geracao,
            origem="cruzamento",
            aptidao=self._aptidao(valor),
        )

    def _mutar(
        self,
        pai: CasoDeTeste,
        geracao: int,
    ) -> CasoDeTeste:

        prefixo = self.random.choice(
            self.MUTACOES
        )

        valor = (
            prefixo
            + pai.valor.lstrip("/")
        )

        return CasoDeTeste(
            valor=valor,
            geracao=geracao,
            origem="mutacao",
            aptidao=self._aptidao(
                valor
            ),
        )

    def executar(
        self,
        sementes: list[str],
    ) -> ResultadoEvolutivo:

        if not sementes:
            raise ValueError(
                "ao menos uma semente é obrigatória"
            )

        populacao = [
            CasoDeTeste(
                valor=valor,
                geracao=0,
                origem="semente",
                aptidao=self._aptidao(
                    valor
                ),
            )
            for valor in sementes
        ]

        execucoes = len(populacao)

        melhor = max(
            populacao,
            key=lambda x: x.aptidao,
        )

        historico = [
            melhor.aptidao
        ]

        if (
            melhor.aptidao == 1.0
            and self.config.parar_ao_confirmar
        ):
            return ResultadoEvolutivo(
                confirmado=True,
                geracoes_executadas=0,
                execucoes=execucoes,
                melhor=melhor,
                historico_melhor_aptidao=(
                    historico
                ),
            )

        for geracao in range(
            1,
            self.config.max_geracoes + 1,
        ):

            populacao.sort(
                key=lambda x: x.aptidao,
                reverse=True,
            )

            elite = populacao[
                : max(
                    1,
                    len(populacao) // 2,
                )
            ]

            nova = list(elite)

            while (
                len(nova)
                < self.config.tamanho_populacao
            ):
                pai = self.random.choice(elite)

                if (
                    len(elite) >= 2
                    and len(nova) % 2 == 0
                ):
                    mae = self.random.choice(elite)
                    filho = self._cruzar(
                        pai, mae, geracao
                    )
                else:
                    filho = self._mutar(
                        pai, geracao
                    )

                nova.append(filho)
                execucoes += 1

            populacao = nova

            melhor_geracao = max(
                populacao,
                key=lambda x: x.aptidao,
            )

            if (
                melhor_geracao.aptidao
                > melhor.aptidao
            ):
                melhor = melhor_geracao

            historico.append(
                melhor.aptidao
            )

            if (
                melhor.aptidao == 1.0
                and self.config.parar_ao_confirmar
            ):
                return ResultadoEvolutivo(
                    confirmado=True,
                    geracoes_executadas=geracao,
                    execucoes=execucoes,
                    melhor=melhor,
                    historico_melhor_aptidao=(
                        historico
                    ),
                )

        return ResultadoEvolutivo(
            confirmado=(
                melhor.aptidao == 1.0
            ),
            geracoes_executadas=(
                self.config.max_geracoes
            ),
            execucoes=execucoes,
            melhor=melhor,
            historico_melhor_aptidao=(
                historico
            ),
        )
