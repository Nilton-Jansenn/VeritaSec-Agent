from __future__ import annotations

from dataclasses import dataclass
from ipaddress import ip_address
from pathlib import Path
from urllib.parse import urlparse
from typing import Any


CAPACIDADES_REGISTRADAS_PADRAO = frozenset(
    {
        "busca_codigo",
        "revisao_codigo_seguro",
        "path_traversal",
        "runtime_http",
        "autorizacao_http",
        "busca_evolucionaria",
        "zap",
        "oraculo_path_traversal",
        "oraculo_autorizacao",
        "proveniencia",
    }
)

CAPACIDADES_ESTATICAS = frozenset(
    {
        "busca_codigo",
        "revisao_codigo_seguro",
        "proveniencia",
    }
)

CAPACIDADES_PATH = frozenset(
    {
        "path_traversal",
        "busca_evolucionaria",
        "oraculo_path_traversal",
    }
)

CAPACIDADES_HTTP = frozenset(
    {
        "runtime_http",
        "autorizacao_http",
        "oraculo_autorizacao",
    }
)


@dataclass(frozen=True, slots=True)
class ResultadoPoliticaEscopo:
    capacidades_registradas: frozenset[str]
    capacidades_autorizadas: frozenset[str]
    capacidades_negadas: frozenset[str]
    motivos: dict[str, str]
    escopo: dict[str, Any]

    def dump(self) -> dict[str, Any]:
        return {
            "capacidades_registradas": sorted(
                self.capacidades_registradas
            ),
            "capacidades_autorizadas": sorted(
                self.capacidades_autorizadas
            ),
            "capacidades_negadas": sorted(
                self.capacidades_negadas
            ),
            "motivos": dict(self.motivos),
            "escopo": dict(self.escopo),
        }


def _valor(obj: Any, nome: str, default=None):
    if isinstance(obj, dict):
        return obj.get(nome, default)

    return getattr(
        obj,
        nome,
        default,
    )


def _metadados(achado: Any) -> dict[str, Any]:
    valor = _valor(
        achado,
        "metadados",
        {},
    )

    return (
        valor
        if isinstance(valor, dict)
        else {}
    )


def _arquivo_em_escopo(
    arquivo: str | None,
    projeto: str | None,
) -> bool:
    if not arquivo:
        return False

    try:
        alvo = Path(
            arquivo
        ).expanduser().resolve()
    except Exception:
        return False

    if not alvo.is_file():
        return False

    if not projeto:
        # Finding explícito sem projeto SARIF:
        # o próprio arquivo é o escopo estático.
        return True

    try:
        raiz = Path(
            projeto
        ).expanduser().resolve()

        if not raiz.is_dir():
            return False

        alvo.relative_to(
            raiz
        )

        return True

    except Exception:
        return False


def _sandbox_valida(
    raiz_sandbox: str | None,
) -> bool:
    if not raiz_sandbox:
        return False

    try:
        raiz = Path(
            raiz_sandbox
        ).expanduser().resolve()

        return raiz.is_dir()

    except Exception:
        return False


def _sementes_validas(
    sementes: Any,
    *,
    limite_quantidade: int = 16,
    limite_tamanho: int = 512,
) -> bool:
    if not isinstance(
        sementes,
        (list, tuple),
    ):
        return False

    if not sementes:
        return False

    if len(sementes) > limite_quantidade:
        return False

    for semente in sementes:
        if not isinstance(
            semente,
            str,
        ):
            return False

        if not semente:
            return False

        if len(semente) > limite_tamanho:
            return False

        if "\x00" in semente:
            return False

    return True


def _host_loopback(
    hostname: str | None,
) -> bool:
    if not hostname:
        return False

    nome = hostname.strip().lower()

    if nome == "localhost":
        return True

    try:
        return ip_address(
            nome
        ).is_loopback

    except ValueError:
        return False


def _base_url_http_autorizada(
    base_url: str | None,
) -> bool:
    if not base_url:
        return False

    try:
        parsed = urlparse(
            base_url
        )
    except Exception:
        return False

    if parsed.scheme not in {
        "http",
        "https",
    }:
        return False

    if not _host_loopback(
        parsed.hostname
    ):
        return False

    if parsed.username is not None:
        return False

    if parsed.password is not None:
        return False

    return True


def _caminho_http_valido(
    caminho: str | None,
) -> bool:
    if not caminho:
        return False

    if not isinstance(
        caminho,
        str,
    ):
        return False

    if "\x00" in caminho:
        return False

    if not caminho.startswith("/"):
        return False

    if "://" in caminho:
        return False

    return True


def _marcador_valido(
    marcador: str | None,
) -> bool:
    if not marcador:
        return False

    if not isinstance(
        marcador,
        str,
    ):
        return False

    if "\x00" in marcador:
        return False

    return len(marcador) <= 1024


def _calcular_capacidades_autorizadas_base_integral(
    *,
    achado: Any,
    capacidades_registradas: set[str] | frozenset[str] | None = None,
) -> ResultadoPoliticaEscopo:
    registradas = frozenset(
        capacidades_registradas
        or CAPACIDADES_REGISTRADAS_PADRAO
    )

    autorizadas: set[str] = set()
    motivos: dict[str, str] = {}

    metadata = _metadados(
        achado
    )

    arquivo = _valor(
        achado,
        "arquivo",
        None,
    )

    projeto = metadata.get(
        "projeto"
    )

    dinamica = bool(
        _valor(
            achado,
            "execucao_dinamica_permitida",
            False,
        )
    )

    raiz_sandbox = _valor(
        achado,
        "raiz_sandbox",
        None,
    )

    sementes = _valor(
        achado,
        "sementes",
        [],
    )

    max_iteracoes = _valor(
        achado,
        "max_iteracoes",
        0,
    )

    base_url = _valor(
        achado,
        "base_url_http",
        None,
    )

    caminho_http = _valor(
        achado,
        "caminho_http",
        None,
    )

    marcador = _valor(
        achado,
        "marcador_recurso",
        None,
    )

    # --------------------------------------------------------
    # CAPACIDADES ESTATICAS
    # --------------------------------------------------------

    escopo_estatico = _arquivo_em_escopo(
        arquivo,
        projeto,
    )

    for capacidade in CAPACIDADES_ESTATICAS:
        if capacidade not in registradas:
            continue

        if escopo_estatico:
            autorizadas.add(
                capacidade
            )

            motivos[capacidade] = (
                "AUTORIZADA_ESCopo_ESTATICO"
            )

        else:
            motivos[capacidade] = (
                "NEGADA_ARQUIVO_FORA_DO_ESCOPO"
            )

    # --------------------------------------------------------
    # PATH TRAVERSAL
    # --------------------------------------------------------

    sandbox_ok = _sandbox_valida(
        raiz_sandbox
    )

    sementes_ok = _sementes_validas(
        sementes
    )

    budget_ok = (
        isinstance(
            max_iteracoes,
            int,
        )
        and not isinstance(
            max_iteracoes,
            bool,
        )
        and 1 <= max_iteracoes <= 10
    )

    path_ok = (
        dinamica
        and sandbox_ok
        and sementes_ok
        and budget_ok
    )

    for capacidade in CAPACIDADES_PATH:
        if capacidade not in registradas:
            continue

        if path_ok:
            autorizadas.add(
                capacidade
            )

            motivos[capacidade] = (
                "AUTORIZADA_DINAMICA_SANDBOX"
            )

        elif not dinamica:
            motivos[capacidade] = (
                "NEGADA_EXECUCAO_DINAMICA_NAO_AUTORIZADA"
            )

        elif not sandbox_ok:
            motivos[capacidade] = (
                "NEGADA_SANDBOX_INVALIDA_OU_AUSENTE"
            )

        elif not sementes_ok:
            motivos[capacidade] = (
                "NEGADA_SEMENTES_INVALIDAS_OU_AUSENTES"
            )

        else:
            motivos[capacidade] = (
                "NEGADA_ORCAMENTO_INVALIDO"
            )

    # --------------------------------------------------------
    # HTTP
    #
    # Sem allowlist externa formal:
    # fail-closed para alvo externo e somente loopback.
    # --------------------------------------------------------

    base_url_ok = _base_url_http_autorizada(
        base_url
    )

    caminho_ok = _caminho_http_valido(
        caminho_http
    )

    marcador_ok = _marcador_valido(
        marcador
    )

    http_ok = (
        dinamica
        and base_url_ok
        and caminho_ok
        and marcador_ok
        and budget_ok
    )

    for capacidade in CAPACIDADES_HTTP:
        if capacidade not in registradas:
            continue

        if http_ok:
            autorizadas.add(
                capacidade
            )

            motivos[capacidade] = (
                "AUTORIZADA_HTTP_LOOPBACK_EXPLICITO"
            )

        elif not dinamica:
            motivos[capacidade] = (
                "NEGADA_EXECUCAO_DINAMICA_NAO_AUTORIZADA"
            )

        elif not base_url_ok:
            motivos[capacidade] = (
                "NEGADA_BASE_URL_NAO_AUTORIZADA"
            )

        elif not caminho_ok:
            motivos[capacidade] = (
                "NEGADA_CAMINHO_HTTP_INVALIDO"
            )

        elif not marcador_ok:
            motivos[capacidade] = (
                "NEGADA_MARCADOR_INVALIDO_OU_AUSENTE"
            )

        else:
            motivos[capacidade] = (
                "NEGADA_ORCAMENTO_INVALIDO"
            )

    # --------------------------------------------------------
    # ZAP
    #
    # Explicitamente NÃO autorizado por padrão.
    # --------------------------------------------------------

    if "zap" in registradas:
        motivos["zap"] = (
            "NEGADA_POR_PADRAO_SEM_POLITICA_EXPLICITA"
        )

    # --------------------------------------------------------
    # GARANTIA FINAL:
    # nada pode ser autorizado se sequer não está registrado.
    # --------------------------------------------------------

    autorizadas &= set(
        registradas
    )

    negadas = set(
        registradas
    ) - autorizadas

    return ResultadoPoliticaEscopo(
        capacidades_registradas=registradas,
        capacidades_autorizadas=frozenset(
            autorizadas
        ),
        capacidades_negadas=frozenset(
            negadas
        ),
        motivos=motivos,
        escopo={
            "arquivo": arquivo,
            "projeto": projeto,
            "execucao_dinamica_permitida": dinamica,
            "raiz_sandbox_informada": bool(
                raiz_sandbox
            ),
            "sementes_quantidade": (
                len(sementes)
                if isinstance(
                    sementes,
                    (list, tuple),
                )
                else 0
            ),
            "max_iteracoes": max_iteracoes,
            "base_url_http": base_url,
            "caminho_http": caminho_http,
            "marcador_recurso_informado": bool(
                marcador
            ),
            "http_externo_permitido": False,
            "zap_autorizado": False,
        },
    )


# ============================================================
# VERITASSEC — POLITICA RUNTIME INTEGRAL
# ============================================================

from urllib.parse import urlparse as _vs_integral_urlparse


def _vs_integral_get(
    objeto,
    nome,
    padrao=None,
):
    if isinstance(
        objeto,
        dict,
    ):
        return objeto.get(
            nome,
            padrao,
        )

    return getattr(
        objeto,
        nome,
        padrao,
    )


def _vs_integral_loopback(
    url,
):
    if not isinstance(
        url,
        str,
    ):
        return False

    try:
        parsed = _vs_integral_urlparse(
            url
        )
    except Exception:
        return False

    return (
        parsed.scheme
        in {
            "http",
            "https",
        }
        and parsed.hostname
        in {
            "127.0.0.1",
            "localhost",
            "::1",
        }
    )


def _vs_integral_caminho(
    valor,
):
    return (
        isinstance(
            valor,
            str,
        )
        and valor.startswith("/")
        and "://" not in valor
        and "\x00" not in valor
        and len(valor) <= 2048
    )


def _vs_integral_leitura_resultado(
    resultado,
):
    if isinstance(
        resultado,
        dict,
    ):
        return {
            "autorizadas":
                set(
                    resultado.get(
                        "capacidades_autorizadas",
                        [],
                    )
                    or []
                ),

            "negadas":
                set(
                    resultado.get(
                        "capacidades_negadas",
                        [],
                    )
                    or []
                ),

            "motivos":
                dict(
                    resultado.get(
                        "motivos",
                        {},
                    )
                    or {}
                ),
        }

    return {
        "autorizadas":
            set(
                getattr(
                    resultado,
                    "capacidades_autorizadas",
                    [],
                )
                or []
            ),

        "negadas":
            set(
                getattr(
                    resultado,
                    "capacidades_negadas",
                    [],
                )
                or []
            ),

        "motivos":
            dict(
                getattr(
                    resultado,
                    "motivos",
                    {},
                )
                or {}
            ),
    }


def _vs_integral_atualizar(
    resultado,
    *,
    autorizadas,
    negadas,
    motivos,
):
    update = {
        "capacidades_autorizadas":
            sorted(
                autorizadas
            ),

        "capacidades_negadas":
            sorted(
                negadas
            ),

        "motivos":
            dict(
                motivos
            ),
    }

    # dict
    if isinstance(
        resultado,
        dict,
    ):
        novo = dict(
            resultado
        )

        novo.update(
            update
        )

        return novo

    # Pydantic 2
    if hasattr(
        resultado,
        "model_copy",
    ):
        return resultado.model_copy(
            update=update,
            deep=True,
        )

    # objeto mutável/frozen
    for chave, valor in update.items():
        try:
            object.__setattr__(
                resultado,
                chave,
                valor,
            )
        except Exception:
            try:
                setattr(
                    resultado,
                    chave,
                    valor,
                )
            except Exception:
                pass

    return resultado


def calcular_capacidades_autorizadas(
    *args,
    **kwargs,
):
    resultado = (
        _calcular_capacidades_autorizadas_base_integral(
            *args,
            **kwargs,
        )
    )

    achado = kwargs.get(
        "achado"
    )

    if (
        achado is None
        and args
    ):
        achado = args[0]

    if achado is None:
        return resultado

    dinamica = (
        _vs_integral_get(
            achado,
            "execucao_dinamica_permitida",
            False,
        )
        is True
    )

    base_url = _vs_integral_get(
        achado,
        "base_url_http",
    )

    caminho = _vs_integral_get(
        achado,
        "caminho_http",
    )

    # --------------------------------------------------------
    # runtime_http é observação HTTP genérica.
    #
    # Requisitos:
    # - autorização dinâmica explícita;
    # - loopback;
    # - caminho HTTP relativo válido.
    #
    # marcador_recurso NÃO é requisito.
    # --------------------------------------------------------

    if not (
        dinamica
        and _vs_integral_loopback(
            base_url
        )
        and _vs_integral_caminho(
            caminho
        )
    ):
        return resultado

    dados = _vs_integral_leitura_resultado(
        resultado
    )

    autorizadas = dados[
        "autorizadas"
    ]

    negadas = dados[
        "negadas"
    ]

    motivos = dados[
        "motivos"
    ]

    autorizadas.add(
        "runtime_http"
    )

    negadas.discard(
        "runtime_http"
    )

    motivos[
        "runtime_http"
    ] = (
        "AUTORIZADA_RUNTIME_HTTP_LOOPBACK"
    )

    atualizado = _vs_integral_atualizar(
        resultado,
        autorizadas=autorizadas,
        negadas=negadas,
        motivos=motivos,
    )

    # --------------------------------------------------------
    # Verificação interna obrigatória.
    # --------------------------------------------------------

    if isinstance(
        atualizado,
        dict,
    ):
        finais = set(
            atualizado.get(
                "capacidades_autorizadas",
                [],
            )
            or []
        )
    else:
        finais = set(
            getattr(
                atualizado,
                "capacidades_autorizadas",
                [],
            )
            or []
        )

    if (
        "runtime_http"
        not in finais
    ):
        raise RuntimeError(
            "M25_RUNTIME_HTTP_NAO_MATERIALIZADO"
        )


    from .zap_sarif_vinculo import (
        autorizado as _zap_autorizado,
    )

    registradas = kwargs.get(
        "capacidades_registradas"
    )

    if registradas is None and len(args) > 1:
        registradas = args[1]

    if (
        registradas is not None
        and "zap" in registradas
        and _zap_autorizado(achado)
    ):
        dados_zap = _vs_integral_leitura_resultado(
            atualizado
        )

        autorizadas_zap = dados_zap["autorizadas"]
        negadas_zap = dados_zap["negadas"]
        motivos_zap = dados_zap["motivos"]

        autorizadas_zap.add("zap")
        negadas_zap.discard("zap")

        motivos_zap["zap"] = (
            "SARIF_RUNTIME_ENDPOINT_AUTORIZADOS"
        )

        atualizado = _vs_integral_atualizar(
            atualizado,
            autorizadas=autorizadas_zap,
            negadas=negadas_zap,
            motivos=motivos_zap,
        )

    return atualizado


calcular_capacidades_autorizadas.__veritassec_integral__ = True

