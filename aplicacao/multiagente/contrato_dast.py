"""Contrato de entrada DAST: validação de intenção, sem executar requisições."""
from __future__ import annotations
from dataclasses import dataclass
from urllib.parse import urlsplit
import ipaddress

class ConfiguracaoDASTInvalida(ValueError):
    pass

@dataclass(frozen=True)
class ConfiguracaoDAST:
    habilitado: bool
    url_base: str | None
    autorizado: bool

def validar_configuracao_dast(habilitado: bool, url_base: str | None, autorizado: bool = False) -> ConfiguracaoDAST:
    if not isinstance(habilitado, bool):
        raise ConfiguracaoDASTInvalida('SINALIZADORES_INVALIDOS')
    if not habilitado:
        return ConfiguracaoDAST(False, None, False)
    if not isinstance(url_base, str) or not url_base.strip():
        raise ConfiguracaoDASTInvalida('URL_BASE_OBRIGATORIA')
    url_base=url_base.strip()
    try:
        u=urlsplit(url_base)
        port=u.port
    except ValueError as exc:
        raise ConfiguracaoDASTInvalida('URL_INVALIDA') from exc
    if u.scheme not in ('http','https') or not u.hostname or u.username or u.password or u.fragment or u.query:
        raise ConfiguracaoDASTInvalida('URL_INVALIDA')
    if u.path not in ('','/'):
        raise ConfiguracaoDASTInvalida('URL_BASE_DEVE_SER_ORIGEM')
    if port is not None and not 1 <= port <= 65535:
        raise ConfiguracaoDASTInvalida('PORTA_INVALIDA')
    # O endereço é apenas um identificador declarado. A resolução DNS e a
    # autorização do destino devem ocorrer imediatamente antes do acesso.
    if autorizado is not True:
        autorizado = _autorizacao_automatica_runtime(url_base)

    if autorizado is not True:
        raise ConfiguracaoDASTInvalida(
            'AUTORIZACAO_EXPLICITA_OBRIGATORIA'
        )

    return ConfiguracaoDAST(
        True,
        url_base.rstrip('/'),
        True,
    )


def _autorizacao_automatica_runtime(url_base: str) -> bool:
    """Autoriza exclusivamente o runtime local preconfigurado."""
    import os
    from urllib.parse import urlsplit

    verdadeiros = {"1", "true", "sim", "yes"}

    runtime_ativo = (
        os.environ.get("VERITASSEC_RUNTIME_LOCAL", "")
        .strip().lower() in verdadeiros
    )

    zap_ativo = (
        os.environ.get("VERITASSEC_ZAP_HABILITADO", "")
        .strip().lower() in verdadeiros
    )

    if not (runtime_ativo and zap_ativo):
        return False

    base = os.environ.get(
        "VERITASSEC_RUNTIME_LOCAL_BASE_URL", ""
    ).strip()

    try:
        declarada = urlsplit(url_base)
        aprovada = urlsplit(base)

        def origem(u):
            return (
                u.scheme.lower(),
                (u.hostname or "").lower(),
                u.port or (
                    443 if u.scheme == "https" else 80
                ),
            )

        return (
            declarada.scheme == "http"
            and declarada.hostname == "127.0.0.1"
            and declarada.port == 3001
            and origem(declarada) == origem(aprovada)
            and declarada.path in ("", "/")
            and aprovada.path in ("", "/")
            and not declarada.username
            and not declarada.password
            and not aprovada.username
            and not aprovada.password
            and not aprovada.query
            and not aprovada.fragment
        )
    except (ValueError, TypeError):
        return False
