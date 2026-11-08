from __future__ import annotations

import os

from pydantic import BaseModel


class ConfiguracaoRuntime(BaseModel):
    ia_habilitada: bool
    provedor_llm: str | None
    modelo_llm: str | None

    zap_habilitado: bool
    zap_url: str

    permitir_rede_publica: bool
    permitir_rede_privada: bool

    modo: str


def _bool(nome: str, padrao: bool = False) -> bool:
    valor = os.getenv(nome)

    if valor is None:
        return padrao

    return valor.strip().lower() in {
        "1",
        "true",
        "yes",
        "sim",
        "on",
    }


def carregar_configuracao_runtime() -> ConfiguracaoRuntime:
    ia = _bool("IA_HABILITADA", False)

    provedor = (
        os.getenv("VERITASSEC_LLM_PROVIDER")
        or None
    )

    modelo = (
        os.getenv("VERITASSEC_LLM_MODEL")
        or None
    )

    if ia and (not provedor or not modelo):
        raise ValueError(
            "IA habilitada exige "
            "VERITASSEC_LLM_PROVIDER e "
            "VERITASSEC_LLM_MODEL"
        )

    return ConfiguracaoRuntime(
        ia_habilitada=ia,
        provedor_llm=provedor,
        modelo_llm=modelo,
        zap_habilitado=_bool(
            "VERITASSEC_ZAP_HABILITADO",
            False,
        ),
        zap_url=os.getenv(
            "VERITASSEC_ZAP_URL",
            "http://127.0.0.1:8081",
        ),
        permitir_rede_publica=_bool(
            "VERITASSEC_REDE_PUBLICA",
            False,
        ),
        permitir_rede_privada=_bool(
            "VERITASSEC_REDE_PRIVADA",
            False,
        ),
        modo=os.getenv(
            "VERITASSEC_MODO",
            "offline-seguro",
        ),
    )
