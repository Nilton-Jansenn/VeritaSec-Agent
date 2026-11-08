from aplicacao.dominio.enums import RiscoAcao
from aplicacao.dominio.modelos import (
    AcaoInvestigacao,
    Investigacao,
    LacunaEvidencia,
    PlanoInvestigacao,
)


class PlanejadorAdaptativo:

    MAPA_FERRAMENTAS = {
        "contexto_codigo": "busca_codigo",
        "validacao_entrada": "revisao_codigo_seguro",
        "autorizacao": "revisao_codigo_seguro",
        "fluxo_dados": "busca_codigo",
        "execucao_dinamica": "execucao_dinamica",
        "oraculo": "execucao_dinamica",
    }

    def planejar(
        self,
        investigacao: Investigacao,
        lacunas: list[LacunaEvidencia],
    ) -> PlanoInvestigacao:

        pendentes = sorted(
            (
                lacuna
                for lacuna in lacunas
                if not lacuna.satisfeita
            ),
            key=lambda item: item.prioridade,
            reverse=True,
        )

        acoes: list[AcaoInvestigacao] = []

        vistos: set[str] = set()

        for lacuna in pendentes:
            ferramenta = self.MAPA_FERRAMENTAS.get(
                lacuna.tipo
            )

            if not ferramenta:
                continue

            chave = f"{ferramenta}:{lacuna.tipo}"

            if chave in vistos:
                continue

            vistos.add(chave)

            acoes.append(
                AcaoInvestigacao(
                    ferramenta=ferramenta,
                    objetivo=(
                        "adquirir evidência para: "
                        + lacuna.descricao
                    ),
                    parametros={
                        "lacuna": lacuna.tipo,
                        "arquivo": investigacao.achado.arquivo,
                    },
                    risco=(
                        RiscoAcao.MEDIO
                        if ferramenta == "execucao_dinamica"
                        else RiscoAcao.BAIXO
                    ),
                )
            )

        return PlanoInvestigacao(
            hipotese_id=(
                investigacao.hipotese.id
                if investigacao.hipotese
                else investigacao.achado.id
            ),
            objetivo=(
                "reduzir incerteza por aquisição "
                "adaptativa de evidências"
            ),
            acoes=acoes,
        )
