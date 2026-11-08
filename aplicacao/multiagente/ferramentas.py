from __future__ import annotations

import importlib.util
from dataclasses import dataclass


@dataclass(frozen=True)
class Capacidade:
    nome: str
    modulo: str
    classe: str | None
    tipo: str
    ativa: bool


DEFINICOES = (
    (
        "busca_codigo",
        "aplicacao.ferramentas.codigo",
        "FerramentaCodigo",
        "estatica",
    ),
    (
        "revisao_codigo_seguro",
        "aplicacao.revisao_codigo.motor",
        None,
        "estatica",
    ),
    (
        "path_traversal",
        "aplicacao.integracao.path_traversal",
        None,
        "dinamica",
    ),
    (
        "runtime_http",
        "aplicacao.http_runtime.executor",
        "ExecutorHttpControlado",
        "dinamica",
    ),
    (
        "autorizacao_http",
        "aplicacao.integracao.autorizacao_http",
        None,
        "dinamica",
    ),
    (
        "busca_evolucionaria",
        "aplicacao.evolucao.path_traversal",
        "BuscaEvolutivaPathTraversal",
        "evolutiva",
    ),
    (
        "zap",
        "aplicacao.integracoes.zap.cliente",
        "ClienteZap",
        "dinamica",
    ),
    (
        "oraculo_path_traversal",
        "aplicacao.dinamica.oraculos",
        "OraculoPathTraversal",
        "oraculo",
    ),
    (
        "oraculo_autorizacao",
        "aplicacao.oraculos.autorizacao",
        "OraculoAutorizacao",
        "oraculo",
    ),
    (
        "proveniencia",
        "aplicacao.investigacao.proveniencia",
        None,
        "evidencia",
    ),
)


def _modulo_existe(nome: str) -> bool:
    try:
        return importlib.util.find_spec(nome) is not None
    except Exception:
        return False


def catalogo_capacidades() -> dict[str, Capacidade]:
    resultado = {}

    for nome, modulo, classe, tipo in DEFINICOES:
        resultado[nome] = Capacidade(
            nome=nome,
            modulo=modulo,
            classe=classe,
            tipo=tipo,
            ativa=_modulo_existe(modulo),
        )

    return resultado
