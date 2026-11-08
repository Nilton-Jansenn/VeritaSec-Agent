"""Revisão estrutural conservadora.

Este componente produz evidência contextual. Ele não declara,
isoladamente, existência ou ausência de vulnerabilidade.
"""

from aplicacao.ferramentas.codigo import FerramentaCodigo
from aplicacao.revisao_codigo.modelos import (
    ObservacaoControle,
    ResultadoRevisaoCodigo,
)


class MotorRevisaoCodigoSeguro:

    VALIDACAO = (
        "validate",
        "validator",
        "sanitize",
        "sanitizer",
        "escape",
        "normaliz",
        "whitelist",
        "allowlist",
    )

    AUTORIZACAO = (
        "authorize",
        "authorization",
        "permission",
        "role",
        "owner",
        "ownership",
        "access_control",
        "is_admin",
    )

    SINKS_CAMINHO = (
        "open(",
        "read_text(",
        "read_bytes(",
        "send_file(",
        "file(",
        "path(",
    )

    def __init__(
        self,
        ferramenta_codigo: FerramentaCodigo,
    ) -> None:
        self.codigo = ferramenta_codigo

    def _controle(
        self,
        conteudo: str,
        nome: str,
        termos: tuple[str, ...],
    ) -> ObservacaoControle:

        linhas = conteudo.splitlines()
        ocorrencias: list[int] = []

        for numero, linha in enumerate(
            linhas,
            start=1,
        ):
            texto = linha.lower()

            if any(
                termo.lower() in texto
                for termo in termos
            ):
                ocorrencias.append(numero)

        return ObservacaoControle(
            controle=nome,
            observado=bool(ocorrencias),
            ocorrencias=ocorrencias,
            observacao=(
                "marcadores estruturais observados"
                if ocorrencias
                else "marcadores estruturais não observados"
            ),
        )

    def revisar(
        self,
        arquivo: str,
    ) -> ResultadoRevisaoCodigo:

        conteudo = self.codigo.ler(arquivo)

        controles = [
            self._controle(
                conteudo,
                "validacao_ou_sanitizacao",
                self.VALIDACAO,
            ),
            self._controle(
                conteudo,
                "autorizacao",
                self.AUTORIZACAO,
            ),
            self._controle(
                conteudo,
                "sink_de_caminho",
                self.SINKS_CAMINHO,
            ),
        ]

        return ResultadoRevisaoCodigo(
            arquivo=arquivo,
            controles=controles,
            limitacoes=[
                (
                    "A análise é estrutural e não prova "
                    "explorabilidade."
                ),
                (
                    "Ausência de marcador textual não prova "
                    "ausência do controle."
                ),
            ],
        )
