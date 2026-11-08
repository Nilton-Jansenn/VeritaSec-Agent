from __future__ import annotations

from dataclasses import dataclass
from ipaddress import ip_address
from pathlib import Path
from urllib.parse import urlparse

from .provedores import (
    ESCOPO_LOCAL,
    ProvedorOpenAICompativel,
)


@dataclass(frozen=True)
class ConfiguracaoRuntimeLocal:
    base_url: str
    modelo: str
    api_key_file: Path
    container_ip: str


def _ler_env(
    path: Path,
) -> dict[str, str]:
    dados: dict[str, str] = {}

    for raw in path.read_text(
        encoding="utf-8"
    ).splitlines():

        linha = raw.strip()

        if (
            not linha
            or linha.startswith("#")
            or "=" not in linha
        ):
            continue

        k, v = linha.split("=", 1)
        dados[k.strip()] = v.strip()

    return dados


def carregar_configuracao_runtime_local(
    path: str | Path | None = None,
) -> ConfiguracaoRuntimeLocal:

    arquivo = (
        Path(path).expanduser()
        if path is not None
        else (
            Path.home()
            / ".config"
            / "veritassec"
            / "local-runtime"
            / "runtime.env"
        )
    )

    dados = _ler_env(arquivo)

    base_url = dados[
        "VERITASSEC_LOCAL_BASE_URL"
    ]

    ip = dados[
        "VERITASSEC_LOCAL_CONTAINER_IP"
    ]

    parsed = urlparse(base_url)

    if (
        parsed.scheme != "http"
        or parsed.hostname != ip
    ):
        raise RuntimeError(
            "Endpoint interno invalido"
        )

    endereco = ip_address(ip)

    if (
        not endereco.is_private
        or endereco.is_loopback
    ):
        raise RuntimeError(
            "IP do runtime deve ser privado"
        )

    key_file = Path(
        dados[
            "VERITASSEC_LOCAL_API_KEY_FILE"
        ]
    ).expanduser()

    if not key_file.is_file():
        raise RuntimeError(
            "Credencial ausente"
        )

    if key_file.stat().st_mode & 0o077:
        raise RuntimeError(
            "Credencial permissiva"
        )

    return ConfiguracaoRuntimeLocal(
        base_url=base_url,
        modelo=dados[
            "VERITASSEC_LOCAL_MODEL"
        ],
        api_key_file=key_file,
        container_ip=ip,
    )


class ProvedorDockerInterno(
    ProvedorOpenAICompativel
):
    def __init__(
        self,
        cfg: ConfiguracaoRuntimeLocal,
    ) -> None:

        def obter_chave() -> str:
            chave = cfg.api_key_file.read_text(
                encoding="utf-8"
            ).strip()

            if not chave:
                raise RuntimeError(
                    "Credencial vazia"
                )

            return chave

        super().__init__(
            nome="local",
            modelo=cfg.modelo,
            base_url=cfg.base_url,
            api_key_getter=obter_chave,
            timeout_segundos=5.0,
            local_only=False,
        )

        self.escopo = ESCOPO_LOCAL


def criar_provedor_runtime_local():
    return ProvedorDockerInterno(
        carregar_configuracao_runtime_local()
    )
