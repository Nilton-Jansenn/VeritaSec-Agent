from __future__ import annotations

from dataclasses import (
    dataclass,
    field,
    replace,
)
from threading import BoundedSemaphore
from typing import Mapping

from .cache import CacheMemoriaTTL
from .contexto import (
    GerenciadorContexto,
    PacoteContexto,
)
from .contratos import (
    ProvedorLLM,
    RespostaLLM,
    SolicitacaoLLM,
)
from .provedores import (
    ESCOPO_EXTERNO,
    ESCOPO_LOCAL,
)
from .seguranca import (
    ErroSegurancaLLM,
    contem_segredo,
)


@dataclass(frozen=True)
class PoliticaExecucaoLLM:
    max_tokens_saida: int = 512
    concorrencia_local: int = 1
    bloquear_segredo_em_provedor_externo: bool = True
    max_tokens_saida_por_agente: Mapping[str, int] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class ResultadoExecucaoLLM:
    resposta: RespostaLLM
    contexto: PacoteContexto
    cache_hit: bool
    cache_habilitado: bool


class RegistroProvedores:
    def __init__(self) -> None:
        self._provedores: dict[
            str,
            ProvedorLLM,
        ] = {}

    def registrar(
        self,
        nome: str,
        provedor: ProvedorLLM,
    ) -> None:
        if (
            not nome
            or nome in self._provedores
        ):
            raise ValueError(
                "Provedor duplicado ou invalido"
            )

        self._provedores[nome] = provedor

    def obter(
        self,
        nome: str,
    ) -> ProvedorLLM:
        try:
            return self._provedores[nome]

        except KeyError as exc:
            raise KeyError(
                f"Provedor nao registrado: {nome}"
            ) from exc

    def nomes(self) -> tuple[str, ...]:
        return tuple(
            sorted(self._provedores)
        )


class GerenciadorExecucaoLLM:
    def __init__(
        self,
        registro: RegistroProvedores,
        contexto: GerenciadorContexto,
        cache: CacheMemoriaTTL,
        politica: PoliticaExecucaoLLM,
    ) -> None:
        if politica.concorrencia_local <= 0:
            raise ValueError(
                "concorrencia_local deve ser > 0"
            )

        self.registro = registro
        self.contexto = contexto
        self.cache = cache
        self.politica = politica

        self._semaforo_local = (
            BoundedSemaphore(
                politica.concorrencia_local
            )
        )

    @staticmethod
    def _tem_segredo(
        solicitacao: SolicitacaoLLM,
    ) -> bool:
        if contem_segredo(
            solicitacao.prompt_sistema
        ):
            return True

        if contem_segredo(
            solicitacao.prompt_usuario
        ):
            return True

        return any(
            contem_segredo(
                evidencia.conteudo
            )
            for evidencia
            in solicitacao.evidencias
        )

    def _limite_saida(
        self,
        solicitacao: SolicitacaoLLM,
    ) -> int:
        limite = self.politica.max_tokens_saida

        agente = str(
            solicitacao.metadados.get(
                "agente",
                "",
            )
        )

        if (
            agente
            and agente
            in self.politica
            .max_tokens_saida_por_agente
        ):
            limite = min(
                limite,
                int(
                    self.politica
                    .max_tokens_saida_por_agente[
                        agente
                    ]
                ),
            )

        return min(
            solicitacao.max_tokens_saida,
            limite,
        )

    def executar(
        self,
        nome_provedor: str,
        solicitacao: SolicitacaoLLM,
    ) -> ResultadoExecucaoLLM:
        provedor = self.registro.obter(
            nome_provedor
        )

        pacote = self.contexto.preparar(
            solicitacao.prompt_sistema,
            solicitacao.prompt_usuario,
            solicitacao.evidencias,
        )

        preparada = replace(
            solicitacao,
            evidencias=pacote.incluidas,
            max_tokens_saida=self._limite_saida(
                solicitacao
            ),
            metadados={
                **dict(
                    solicitacao.metadados
                ),
                "contexto_truncado":
                    pacote.truncado,
                "evidencias_omitidas":
                    pacote.omitidas_ids,
                "evidencias_duplicadas":
                    pacote.duplicadas_ids,
                "tokens_entrada_estimados":
                    pacote.tokens_estimados,
                "proveniencia": tuple(
                    {
                        "id": item.id,
                        "fonte": item.fonte,
                        "sha256": item.sha256,
                    }
                    for item
                    in pacote.proveniencia
                ),
            },
        )

        tem_segredo = self._tem_segredo(
            preparada
        )

        if (
            tem_segredo
            and provedor.escopo
            == ESCOPO_EXTERNO
            and self.politica
            .bloquear_segredo_em_provedor_externo
        ):
            raise ErroSegurancaLLM(
                "Segredo bloqueado para provedor externo"
            )

        cache_habilitado = (
            preparada.deterministica
            and not tem_segredo
        )

        chave = None

        if cache_habilitado:
            chave = self.cache.chave(
                provedor.nome,
                provedor.modelo,
                preparada,
            )

            hit = self.cache.obter(chave)

            if hit is not None:
                return ResultadoExecucaoLLM(
                    resposta=hit,
                    contexto=pacote,
                    cache_hit=True,
                    cache_habilitado=True,
                )

        if provedor.escopo == ESCOPO_LOCAL:
            with self._semaforo_local:
                resposta = provedor.gerar(
                    preparada
                )
        else:
            resposta = provedor.gerar(
                preparada
            )

        if (
            cache_habilitado
            and chave is not None
        ):
            self.cache.armazenar(
                chave,
                resposta,
            )

        return ResultadoExecucaoLLM(
            resposta=resposta,
            contexto=pacote,
            cache_hit=False,
            cache_habilitado=cache_habilitado,
        )
