from __future__ import annotations

import ipaddress
from urllib.parse import urlparse

from .modelos import AlvoHttpAutorizado


class AlvoNaoAutorizado(PermissionError):
    pass


def _resolver_literal(
    hostname: str,
) -> ipaddress.IPv4Address | ipaddress.IPv6Address | None:

    try:
        return ipaddress.ip_address(
            hostname
        )
    except ValueError:
        return None


def validar_alvo(
    alvo: AlvoHttpAutorizado,
) -> None:

    parsed = urlparse(
        alvo.base_url
    )

    if parsed.scheme not in {
        "http",
        "https",
    }:
        raise AlvoNaoAutorizado(
            "somente HTTP/HTTPS são permitidos"
        )

    hostname = parsed.hostname

    if not hostname:
        raise AlvoNaoAutorizado(
            "hostname ausente"
        )

    if hostname.lower() == "localhost":
        if not alvo.permitir_loopback:
            raise AlvoNaoAutorizado(
                "loopback não autorizado"
            )

        return

    endereco = _resolver_literal(
        hostname
    )

    if endereco is None:
        if not alvo.permitir_rede_publica:
            raise AlvoNaoAutorizado(
                "hostname não literal exige "
                "autorização explícita de rede pública"
            )

        return

    if endereco.is_loopback:
        if not alvo.permitir_loopback:
            raise AlvoNaoAutorizado(
                "loopback não autorizado"
            )

        return

    if endereco.is_private:
        if not alvo.permitir_rede_privada:
            raise AlvoNaoAutorizado(
                "rede privada não autorizada"
            )

        return

    if not alvo.permitir_rede_publica:
        raise AlvoNaoAutorizado(
            "rede pública não autorizada"
        )
