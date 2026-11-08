from __future__ import annotations

def _vs_inicializar_provedor_externo(instancia, modelo, api_key_file):
    instancia.modelo = modelo
    instancia.api_key_file = api_key_file


import json
import time

from pathlib import Path
from urllib import error, request

from .contratos import (
    RespostaLLM,
    SolicitacaoLLM,
    UsoTokens,
)

from .provedores import (
    ESCOPO_EXTERNO,
    montar_conteudo_usuario,
)


class ErroProvedorExterno(RuntimeError):
    pass


def _chave(path: Path) -> str:
    if not path.is_file():
        raise ErroProvedorExterno(
            "Credencial ausente"
        )

    if path.stat().st_mode & 0o077:
        raise ErroProvedorExterno(
            "Credencial com permissao excessiva"
        )

    valor = path.read_text(
        encoding="utf-8"
    ).strip()

    if not valor:
        raise ErroProvedorExterno(
            "Credencial vazia"
        )

    return valor


def _post_json(
    url: str,
    headers: dict[str, str],
    payload: dict,
    timeout: float = 5.0,
) -> dict:

    ultimo = None

    for tentativa in range(1, 2):

        req = request.Request(
            url,
            data=json.dumps(
                payload,
                ensure_ascii=False,
            ).encode("utf-8"),
            headers={
                **headers,
                "Content-Type":
                    "application/json",
            },
            method="POST",
        )

        try:
            with request.urlopen(
                req,
                timeout=timeout,
            ) as resp:

                if resp.status != 200:
                    raise ErroProvedorExterno(
                        f"HTTP inesperado={resp.status}"
                    )

                return json.load(resp)

        except error.HTTPError as exc:
            body = exc.read().decode(
                "utf-8",
                errors="replace",
            )

            if (
                exc.code == 429
                and (
                    "insufficient_quota" in body
                    or "credit_balance_exhausted" in body
                )
            ):
                raise ErroProvedorExterno(
                    "Saldo da API esgotado"
                ) from exc

            if (
                exc.code == 429
                or 500 <= exc.code <= 599
            ):
                ultimo = exc

                if tentativa < 4:
                    time.sleep(
                        min(
                            2 ** tentativa,
                            12,
                        )
                    )
                    continue

            raise ErroProvedorExterno(
                f"HTTP provedor={exc.code}; "
                f"body={body[:300]}"
            ) from exc

        except error.URLError as exc:
            ultimo = exc

            if tentativa < 4:
                time.sleep(
                    min(
                        2 ** tentativa,
                        12,
                    )
                )
                continue

            raise ErroProvedorExterno(
                "Falha de rede no provedor"
            ) from exc

    raise ErroProvedorExterno(
        "Retries HTTP esgotados"
    ) from ultimo


def _uso_openai(payload: dict) -> UsoTokens:
    uso = payload.get(
        "usage",
        {},
    )

    return UsoTokens(
        entrada=uso.get(
            "input_tokens"
        ),
        saida=uso.get(
            "output_tokens"
        ),
        total=uso.get(
            "total_tokens"
        ),
    )


class ProvedorOpenAIResponses:
    nome = "gpt"
    escopo = ESCOPO_EXTERNO

    def __init__(
        self,
        modelo: str,
        api_key_file: Path,
    ) -> None:
        _vs_inicializar_provedor_externo(self, modelo, api_key_file)


    @staticmethod
    def _texto(
        payload: dict,
    ) -> str:

        partes = []

        for item in payload.get(
            "output",
            [],
        ):
            if item.get("type") != "message":
                continue

            for parte in item.get(
                "content",
                [],
            ):
                if (
                    parte.get("type")
                    == "output_text"
                    and parte.get("text")
                ):
                    partes.append(
                        parte["text"]
                    )

        return "\n".join(
            partes
        ).strip()


    def gerar(
        self,
        solicitacao: SolicitacaoLLM,
    ) -> RespostaLLM:

        key = _chave(
            self.api_key_file
        )

        limites = (
            max(
                2048,
                solicitacao.max_tokens_saida,
            ),
            4096,
            8192,
        )

        ultimo = None

        for limite in dict.fromkeys(
            limites
        ):

            payload = _post_json(
                "https://api.openai.com/v1/responses",
                {
                    "Authorization":
                        f"Bearer {key}",
                },
                {
                    "model":
                        self.modelo,

                    "instructions":
                        solicitacao.prompt_sistema,

                    "input":
                        montar_conteudo_usuario(
                            solicitacao
                        ),

                    "max_output_tokens":
                        limite,

                    "reasoning": {
                        "effort":
                            "low",
                    },

                    "store":
                        False,

                    "tools":
                        [],
                },
            )

            ultimo = payload

            texto = self._texto(
                payload
            )

            if texto:
                return RespostaLLM(
                    texto=texto,
                    provedor=self.nome,
                    modelo=self.modelo,
                    uso=_uso_openai(
                        payload
                    ),
                    metadados={
                        "response_id":
                            payload.get("id"),
                        "status":
                            payload.get("status"),
                        "store":
                            False,
                        "max_output_tokens":
                            limite,
                    },
                )

            status = payload.get(
                "status"
            )

            motivo = (
                payload.get(
                    "incomplete_details"
                )
                or {}
            ).get(
                "reason"
            )

            if (
                status == "incomplete"
                and motivo
                == "max_output_tokens"
            ):
                continue

            raise ErroProvedorExterno(
                "OpenAI sem texto; "
                f"status={status}; "
                f"incomplete_reason={motivo}"
            )

        raise ErroProvedorExterno(
            "OpenAI permaneceu sem texto apos "
            "aumento controlado de output; "
            f"status={ultimo.get('status') if ultimo else None}"
        )


class ProvedorGeminiREST:
    nome = "gemini"
    escopo = ESCOPO_EXTERNO

    def __init__(
        self,
        modelo: str,
        api_key_file: Path,
    ) -> None:
        _vs_inicializar_provedor_externo(self, modelo, api_key_file)


    @staticmethod
    def _diagnostico(
        payload: dict,
    ) -> tuple[
        list[str],
        list[str],
    ]:

        motivos = []
        mensagens = []

        for candidato in payload.get(
            "candidates",
            [],
        ):
            motivo = candidato.get(
                "finishReason"
            )

            if motivo:
                motivos.append(
                    str(motivo)
                )

            mensagem = candidato.get(
                "finishMessage"
            )

            if mensagem:
                mensagens.append(
                    str(mensagem)
                )

        return motivos, mensagens


    @staticmethod
    def _texto(
        payload: dict,
    ) -> str:

        textos = []

        for candidato in payload.get(
            "candidates",
            [],
        ):

            content = candidato.get(
                "content",
                {},
            )

            for parte in content.get(
                "parts",
                [],
            ):
                # Nunca tratamos pensamento interno
                # como resposta analitica.
                if parte.get(
                    "thought"
                ) is True:
                    continue

                texto = parte.get(
                    "text"
                )

                if texto:
                    textos.append(
                        texto
                    )

        return "\n".join(
            textos
        ).strip()


    def gerar(
        self,
        solicitacao: SolicitacaoLLM,
    ) -> RespostaLLM:

        key = _chave(
            self.api_key_file
        )

        limites = (
            max(
                2048,
                solicitacao.max_tokens_saida,
            ),
            4096,
            8192,
        )

        ultimo = None

        for limite in dict.fromkeys(
            limites
        ):

            payload = _post_json(
                "https://generativelanguage.googleapis.com/"
                f"v1beta/models/"
                f"{self.modelo}:generateContent",

                {
                    "x-goog-api-key":
                        key,
                },

                {
                    "systemInstruction": {
                        "parts": [
                            {
                                "text":
                                    solicitacao.prompt_sistema
                            }
                        ]
                    },

                    "contents": [
                        {
                            "role":
                                "user",

                            "parts": [
                                {
                                    "text":
                                        montar_conteudo_usuario(
                                            solicitacao
                                        )
                                }
                            ],
                        }
                    ],

                    "generationConfig": {
                        "temperature":
                            0,

                        "maxOutputTokens":
                            limite,

                        "responseMimeType":
                            "application/json",

                        "thinkingConfig": {
                            "thinkingLevel":
                                "LOW",
                        },
                    },
                },
            )

            ultimo = payload

            texto = self._texto(
                payload
            )

            motivos, mensagens = (
                self._diagnostico(
                    payload
                )
            )

            if texto:
                uso = payload.get(
                    "usageMetadata",
                    {},
                )

                return RespostaLLM(
                    texto=texto,

                    provedor=
                        self.nome,

                    modelo=
                        self.modelo,

                    uso=UsoTokens(
                        entrada=uso.get(
                            "promptTokenCount"
                        ),

                        saida=uso.get(
                            "candidatesTokenCount"
                        ),

                        total=uso.get(
                            "totalTokenCount"
                        ),
                    ),

                    metadados={
                        "response_id":
                            payload.get(
                                "responseId"
                            ),

                        "model_version":
                            payload.get(
                                "modelVersion"
                            ),

                        "finish_reasons":
                            motivos,

                        "max_output_tokens":
                            limite,

                        "thinking_level":
                            "LOW",
                    },
                )

            # Falha esperada e recuperavel:
            # raciocinio consumiu o limite.
            if (
                "MAX_TOKENS"
                in motivos
            ):
                continue

            prompt_feedback = (
                payload.get(
                    "promptFeedback",
                    {}
                )
            )

            raise ErroProvedorExterno(
                "Gemini sem texto final; "
                f"finishReason={motivos}; "
                f"finishMessage={mensagens}; "
                f"promptFeedback={prompt_feedback}"
            )

        motivos, mensagens = (
            self._diagnostico(
                ultimo or {}
            )
        )

        raise ErroProvedorExterno(
            "Gemini permaneceu sem texto apos "
            "8192 tokens; "
            f"finishReason={motivos}; "
            f"finishMessage={mensagens}"
        )
