# aplicacao/ia/contratos.py
# -*- coding: utf-8 -*-

from __future__ import annotations

import json
import re
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

ClassificacaoIA = Literal[
    "verdadeiro_positivo",
    "falso_positivo",
    "inconclusivo",
]


def _texto(valor: Any) -> str:
    if valor is None:
        return ""

    if isinstance(valor, str):
        return valor.strip()

    if isinstance(valor, dict):
        for chave in (
            "descricao",
            "descrição",
            "explicacao",
            "explicação",
            "acao",
            "ação",
            "mensagem",
            "resumo",
            "texto",
            "valor",
            "conteudo",
            "conteúdo",
            "codigo",
            "código",
        ):
            if chave in valor and valor[chave]:
                return str(valor[chave]).strip()

        return json.dumps(valor, ensure_ascii=False, sort_keys=True)

    if isinstance(valor, list):
        return "; ".join(_texto(item) for item in valor if item is not None)

    return str(valor).strip()


def _lista_textual(valor: Any) -> list[str]:
    if valor is None:
        return []

    if isinstance(valor, list):
        saida: list[str] = []

        for item in valor:
            texto = _texto(item)
            if texto:
                saida.append(texto)

        return saida

    if isinstance(valor, dict):
        texto = _texto(valor)
        return [texto] if texto else []

    texto = _texto(valor)
    return [texto] if texto else []


def _confianca(valor: Any) -> float:
    if valor is None:
        return 0.0

    if isinstance(valor, (int, float)):
        numero = float(valor)
        if 1.0 < numero <= 100.0:
            return round(numero / 100.0, 4)
        return max(0.0, min(1.0, numero))

    texto = str(valor).strip().lower()

    mapa = {
        "muito alta": 0.95,
        "muito_alta": 0.95,
        "very high": 0.95,
        "very_high": 0.95,
        "alta": 0.85,
        "high": 0.85,
        "moderada": 0.60,
        "moderado": 0.60,
        "média": 0.60,
        "media": 0.60,
        "medium": 0.60,
        "baixa": 0.30,
        "baixo": 0.30,
        "low": 0.30,
        "muito baixa": 0.15,
        "very low": 0.15,
        "desconhecida": 0.0,
        "desconhecido": 0.0,
        "unknown": 0.0,
    }

    if texto in mapa:
        return mapa[texto]

    match = re.search(r"(\d+(?:[.,]\d+)?)", texto)

    if match:
        numero = float(match.group(1).replace(",", "."))

        if 1.0 < numero <= 100.0:
            return round(numero / 100.0, 4)

        return max(0.0, min(1.0, numero))

    return 0.0


def _classificacao(valor: Any) -> ClassificacaoIA:
    texto = _texto(valor).strip().lower()
    texto = texto.replace("-", "_").replace(" ", "_")

    falsos = {
        "falso_positivo",
        "false_positive",
        "fp",
        "não_vulnerável",
        "nao_vulneravel",
        "not_vulnerable",
        "not_a_vulnerability",
        "benigno",
        "informativo",
        "aviso",
        "alerta",
        "atenção",
        "atencao",
        "cuidado",
        "comentario_inseguro",
        "comentário_inseguro",
    }

    verdadeiros = {
        "verdadeiro_positivo",
        "true_positive",
        "tp",
        "vulnerabilidade",
        "vulnerável",
        "vulneravel",
        "possível_vulnerabilidade",
        "possivel_vulnerabilidade",
        "potencial_vulnerabilidade",
        "possível_risco_de_segurança",
        "possivel_risco_de_seguranca",
        "potencial_risco",
        "sql_injection",
        "injeção_sql",
        "injecao_sql",
        "xss",
        "path_traversal",
        "prototype_pollution",
        "command_injection",
        "redos",
    }

    inconclusivos = {
        "inconclusivo",
        "inconclusive",
        "indeterminado",
        "indeterminada",
        "unknown",
        "desconhecido",
        "desconhecida",
        "manual_review",
        "revisao_manual",
        "revisão_manual",
    }

    if texto in falsos:
        return "falso_positivo"

    if texto in verdadeiros:
        return "verdadeiro_positivo"

    if texto in inconclusivos:
        return "inconclusivo"

    if "falso" in texto or "false" in texto or "not_vulner" in texto:
        return "falso_positivo"

    if "inconclus" in texto or "indetermin" in texto or "manual" in texto:
        return "inconclusivo"

    if (
        "vulner" in texto
        or "risco" in texto
        or "security" in texto
        or "injection" in texto
        or "inje" in texto
        or "xss" in texto
        or "traversal" in texto
        or "pollution" in texto
        or "redos" in texto
        or "exec" in texto
        or "secret" in texto
    ):
        return "verdadeiro_positivo"

    return "inconclusivo"


class EntradaIA(BaseModel):
    tipo_tarefa: str
    achado_id: str | None = None
    contexto: dict[str, Any]


class SaidaIA(BaseModel):
    classificacao: ClassificacaoIA = "inconclusivo"
    confianca: float = Field(default=0.0, ge=0.0, le=1.0)
    justificativa: str = ""
    evidencias: list[str] = []
    recomendacoes: list[str] = []
    provedor: str = ""
    modelo: str = ""

    @field_validator("classificacao", mode="before")
    @classmethod
    def validar_classificacao(cls, valor: Any) -> ClassificacaoIA:
        return _classificacao(valor)

    @field_validator("confianca", mode="before")
    @classmethod
    def validar_confianca(cls, valor: Any) -> float:
        return _confianca(valor)

    @field_validator("justificativa", mode="before")
    @classmethod
    def validar_justificativa(cls, valor: Any) -> str:
        return _texto(valor)

    @field_validator("evidencias", "recomendacoes", mode="before")
    @classmethod
    def validar_lista_textual(cls, valor: Any) -> list[str]:
        return _lista_textual(valor)
