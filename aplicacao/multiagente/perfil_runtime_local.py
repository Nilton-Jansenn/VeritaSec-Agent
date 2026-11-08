from __future__ import annotations

import os

from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse


@dataclass(frozen=True)
class PerfilRuntimeLocal:
    habilitado: bool
    base_url: str | None
    projeto_autorizado: bool
    loopback: bool
    motivo: str


def _bool_env(
    nome: str,
    padrao: bool,
) -> bool:

    valor = os.getenv(
        nome
    )

    if valor is None:
        return padrao

    return (
        valor.strip().lower()
        in {
            "1",
            "true",
            "sim",
            "yes",
            "on",
        }
    )


def _eh_loopback(
    base_url: str,
) -> bool:

    try:
        parsed = urlparse(
            base_url
        )
    except Exception:
        return False

    return (
        parsed.scheme in {"http", "https"}
        and parsed.hostname in {
            "127.0.0.1",
            "localhost",
            "::1",
        }
        and parsed.port is not None
        and parsed.username is None
        and parsed.password is None
        and not parsed.query
        and not parsed.fragment
        and parsed.path in {"", "/"}
    )


def obter_perfil_runtime_local(
    projeto_path: str,
) -> PerfilRuntimeLocal:

    projeto = Path(
        projeto_path
    ).expanduser().resolve()

    habilitado = _bool_env(
        "VERITASSEC_RUNTIME_LOCAL",
        False,
    )

    if not habilitado:

        return PerfilRuntimeLocal(
            habilitado=False,
            base_url=None,
            projeto_autorizado=False,
            loopback=False,
            motivo="RUNTIME_LOCAL_DESABILITADO",
        )

    projeto_autorizado = (
        projeto.is_dir()
        and projeto.is_absolute()
    )

    if not projeto_autorizado:

        return PerfilRuntimeLocal(
            habilitado=False,
            base_url=None,
            projeto_autorizado=False,
            loopback=False,
            motivo=(
                "PROJETO_NAO_AUTORIZADO_"
                "PARA_RUNTIME_LOCAL"
            ),
        )

    base_url = (
        os.getenv(
            "VERITASSEC_RUNTIME_LOCAL_BASE_URL"
        )
        or os.getenv(
            "VERITASSEC_RUNTIME_BASE_URL"
        )
        or ""
    ).strip().rstrip("/")

    if not base_url:
        return PerfilRuntimeLocal(
            habilitado=False,
            base_url=None,
            projeto_autorizado=True,
            loopback=False,
            motivo="BASE_URL_NAO_CONFIGURADA",
        )

    if not _eh_loopback(
        base_url
    ):

        return PerfilRuntimeLocal(
            habilitado=False,
            base_url=None,
            projeto_autorizado=True,
            loopback=False,
            motivo="BASE_URL_NAO_LOOPBACK",
        )

    return PerfilRuntimeLocal(
        habilitado=True,
        base_url=base_url,
        projeto_autorizado=True,
        loopback=True,
        motivo="RUNTIME_LOCAL_AUTORIZADO",
    )
