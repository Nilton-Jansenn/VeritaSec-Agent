from __future__ import annotations

from typing import Any


PROVEDORES_SUPORTADOS = frozenset(
    {
        "openai",
        "gemini",
        "ollama",
        "llama_cpp",
    }
)


def construir_modelo_agno(
    *,
    provedor: str,
    modelo: str,
    api_key: str = "",
    temperatura: float = 0.1,
    max_tokens: int = 2500,
    timeout: float = 5.0,
    ollama_url: str = (
        "http://127.0.0.1:11434"
    ),
) -> Any:

    provedor = (
        str(provedor)
        .strip()
        .lower()
    )

    modelo = str(
        modelo
    ).strip()

    if not modelo:
        raise ValueError(
            "MODELO_VAZIO"
        )

    if provedor == "gemini":

        if not api_key:
            raise ValueError(
                "API_KEY_GEMINI_AUSENTE"
            )

        from agno.models.google import (
            Gemini,
        )

        # VERITASSEC_AGNO_GEMINI_25_CORRIGIDO
        # Gemini 2.5 Flash permite thinking_budget=0.
        # Nao aplicar essa opcao a outros modelos.
        configuracao = {
            "id": modelo,
            "api_key": api_key,
            "temperature": temperatura,
            "max_output_tokens": max_tokens,
            "timeout": timeout,
            "retries": 0,
        }

        if modelo.startswith("gemini-2.5-flash"):
            configuracao["thinking_budget"] = 0

        return Gemini(**configuracao)

    if provedor == "openai":

        if not api_key:
            raise ValueError(
                "API_KEY_OPENAI_AUSENTE"
            )

        from agno.models.openai import (
            OpenAIResponses,
        )

        return OpenAIResponses(
            id=modelo,
            api_key=api_key,
            temperature=temperatura,
            max_output_tokens=max_tokens,
            timeout=timeout,
            max_retries=0,
        )


    # VERITASSEC_LLAMA_CPP_OPENAI_20261022
    if provedor == "llama_cpp":
        import os

        from agno.models.openai import OpenAIChat

        base_url = os.getenv(
            "VERITASSEC_LLAMA_BASE_URL",
            "",
        ).strip().rstrip("/")

        chave_local = os.getenv(
            "VERITASSEC_LLAMA_API_KEY",
            "",
        ).strip()

        if not base_url:
            raise ValueError(
                "LLAMA_CPP_URL_AUSENTE"
            )

        if not chave_local:
            raise ValueError(
                "LLAMA_CPP_API_KEY_AUSENTE"
            )

        # VERITASSEC_LLAMA_RFC1918_V1
        import ipaddress
        from urllib.parse import urlsplit

        url = urlsplit(base_url)
        host = url.hostname or ""

        if host == "localhost":
            autorizado = True
        else:
            try:
                ip = ipaddress.ip_address(host)
                redes = (
                    "127.0.0.0/8",
                    "10.0.0.0/8",
                    "172.16.0.0/12",
                    "192.168.0.0/16",
                )
                autorizado = (
                    ip.version == 4
                    and any(
                        ip in ipaddress.ip_network(rede)
                        for rede in redes
                    )
                )
            except ValueError:
                autorizado = False

        if not (
            autorizado
            and url.scheme == "http"
            and url.port is not None
            and not url.username
            and not url.password
            and not url.query
            and not url.fragment
            and url.path.rstrip("/") in ("", "/v1")
        ):
            raise ValueError(
                "LLAMA_CPP_ENDPOINT_NAO_LOCAL"
            )

        if not base_url.endswith("/v1"):
            base_url += "/v1"

        return OpenAIChat(
            id=modelo,
            api_key=chave_local,
            base_url=base_url,
            temperature=temperatura,
            max_tokens=max_tokens,
            timeout=timeout,
            max_retries=0,
        )

    if provedor == "ollama":

        from agno.models.ollama import (
            Ollama,
        )

        return Ollama(
            id=modelo,
            host=ollama_url,
            api_key=None,
            options={
                "temperature":
                    temperatura,

                "num_predict":
                    max_tokens,
            },
            timeout=timeout,
        )

    raise ValueError(
        "PROVEDOR_NAO_SUPORTADO:"
        + provedor
    )
