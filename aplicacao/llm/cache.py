from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass
from hashlib import sha256
from typing import Any

import hmac
import json
import secrets
import threading
import time

from .contratos import (
    RespostaLLM,
    SolicitacaoLLM,
)
from .contexto import hash_evidencia


def _json_safe(value: Any) -> Any:
    if value is None or isinstance(
        value,
        (str, int, float, bool),
    ):
        return value

    if isinstance(value, dict):
        return {
            str(k): _json_safe(v)
            for k, v in sorted(
                value.items(),
                key=lambda item: str(item[0]),
            )
        }

    if isinstance(value, (list, tuple)):
        return [
            _json_safe(v)
            for v in value
        ]

    return repr(value)


@dataclass
class _EntradaCache:
    expira_em: float
    resposta: RespostaLLM


class CacheMemoriaTTL:
    def __init__(
        self,
        ttl_segundos: int = 1800,
        max_itens: int = 256,
    ) -> None:
        if ttl_segundos <= 0:
            raise ValueError(
                "ttl_segundos deve ser > 0"
            )

        if max_itens <= 0:
            raise ValueError(
                "max_itens deve ser > 0"
            )

        self.ttl_segundos = ttl_segundos
        self.max_itens = max_itens
        self._salt = secrets.token_bytes(32)

        self._dados: OrderedDict[
            str,
            _EntradaCache,
        ] = OrderedDict()

        self._lock = threading.RLock()

    def chave(
        self,
        provedor: str,
        modelo: str,
        solicitacao: SolicitacaoLLM,
    ) -> str:
        escopo = {
            chave: _json_safe(
                solicitacao.metadados.get(chave)
            )
            for chave in (
                "execution_id",
                "project_id",
                "tenant_id",
                "finding_id",
                "agente",
            )
            if chave in solicitacao.metadados
        }

        payload = {
            "provedor": provedor,
            "modelo": modelo,
            "prompt_sistema":
                solicitacao.prompt_sistema,
            "prompt_usuario":
                solicitacao.prompt_usuario,
            "evidencias": [
                {
                    "id": e.id,
                    "fonte": e.fonte,
                    "sha256": hash_evidencia(e),
                }
                for e in solicitacao.evidencias
            ],
            "max_tokens_saida":
                solicitacao.max_tokens_saida,
            "temperatura":
                solicitacao.temperatura,
            "esquema_resposta":
                _json_safe(
                    solicitacao.esquema_resposta
                ),
            "escopo": escopo,
        }

        blob = json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")

        return hmac.new(
            self._salt,
            blob,
            sha256,
        ).hexdigest()

    def obter(
        self,
        chave: str,
    ) -> RespostaLLM | None:
        agora = time.monotonic()

        with self._lock:
            entrada = self._dados.get(chave)

            if entrada is None:
                return None

            if entrada.expira_em <= agora:
                self._dados.pop(chave, None)
                return None

            self._dados.move_to_end(chave)

            return entrada.resposta

    def armazenar(
        self,
        chave: str,
        resposta: RespostaLLM,
    ) -> None:
        with self._lock:
            self._dados[chave] = _EntradaCache(
                expira_em=(
                    time.monotonic()
                    + self.ttl_segundos
                ),
                resposta=resposta,
            )

            self._dados.move_to_end(chave)

            while len(self._dados) > self.max_itens:
                self._dados.popitem(last=False)

    def limpar(self) -> None:
        with self._lock:
            self._dados.clear()
