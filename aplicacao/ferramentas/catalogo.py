"""Catálogo explícito de capacidades autorizáveis."""

from dataclasses import dataclass

from aplicacao.dominio.enums import RiscoAcao


@dataclass(frozen=True)
class DefinicaoFerramenta:
    nome: str
    descricao: str
    risco: RiscoAcao
    requer_execucao_dinamica: bool = False
    requer_rede: bool = False


class CatalogoFerramentas:

    def __init__(self) -> None:
        self._ferramentas = {
            "sarif": DefinicaoFerramenta(
                nome="sarif",
                descricao="Leitura estruturada de achados SARIF.",
                risco=RiscoAcao.BAIXO,
            ),
            "busca_codigo": DefinicaoFerramenta(
                nome="busca_codigo",
                descricao=(
                    "Busca local e controlada em código-fonte."
                ),
                risco=RiscoAcao.BAIXO,
            ),
            "revisao_codigo_seguro": DefinicaoFerramenta(
                nome="revisao_codigo_seguro",
                descricao=(
                    "Avaliação determinística de propriedades "
                    "de segurança no código."
                ),
                risco=RiscoAcao.BAIXO,
            ),
            "execucao_dinamica": DefinicaoFerramenta(
                nome="execucao_dinamica",
                descricao=(
                    "Execução dinâmica controlada."
                ),
                risco=RiscoAcao.MEDIO,
                requer_execucao_dinamica=True,
            ),
        }

    def obter(
        self,
        nome: str,
    ) -> DefinicaoFerramenta:

        if nome not in self._ferramentas:
            raise KeyError(
                f"ferramenta desconhecida: {nome}"
            )

        return self._ferramentas[nome]

    def nomes(self) -> set[str]:
        return set(self._ferramentas)
