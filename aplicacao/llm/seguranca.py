from __future__ import annotations

import ipaddress
import re
from urllib.parse import urlparse


class ErroSegurancaLLM(RuntimeError):
    pass


_PADROES_SEGREDO = (
    re.compile(
        r"\bsk-[A-Za-z0-9_-]{20,}\b"
    ),
    re.compile(
        r"\bAIza[0-9A-Za-z_-]{30,}\b"
    ),
    re.compile(
        r"\bBearer\s+[A-Za-z0-9._~+/=-]{16,}\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"-----BEGIN "
        r"(?:RSA |EC |OPENSSH )?"
        r"PRIVATE KEY-----"
    ),
    re.compile(
        r"\beyJ[A-Za-z0-9_-]{8,}"
        r"\.[A-Za-z0-9_-]{8,}"
        r"\.[A-Za-z0-9_-]{8,}\b"
    ),
)


def contem_segredo(texto: str) -> bool:
    return any(
        padrao.search(texto or "")
        for padrao in _PADROES_SEGREDO
    )


def validar_url_loopback(base_url: str) -> None:
    parsed = urlparse(base_url)

    if parsed.scheme not in {"http", "https"}:
        raise ErroSegurancaLLM(
            "URL local precisa usar http ou https"
        )

    host = parsed.hostname

    if not host:
        raise ErroSegurancaLLM(
            "URL local sem host"
        )

    if host.lower() == "localhost":
        return

    try:
        ip = ipaddress.ip_address(host)

    except ValueError as exc:
        raise ErroSegurancaLLM(
            "Provedor local deve usar somente loopback"
        ) from exc

    if not ip.is_loopback:
        raise ErroSegurancaLLM(
            "Provedor local fora de loopback foi bloqueado"
        )
