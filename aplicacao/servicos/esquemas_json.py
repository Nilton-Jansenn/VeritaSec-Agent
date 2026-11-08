# Esquema JSON para a resposta de análise.
ESQUEMA_ANALISE = {
    "type": "object",
    "properties": {
        "classificacao": {
            "type": "string",
            "enum": ["verdadeiro_positivo", "falso_positivo", "inconclusivo"]
        },
        "confianca": {"type": "number"},
        "severidade": {
            "type": "string",
            "enum": ["baixa", "media", "alta", "critica"]
        },
        "cwe_estimado": {"type": ["string", "null"]},
        "cvss_estimado": {"type": ["number", "null"]},
        "explicacao": {"type": "string"},
        "xai": {
            "type": "object",
            "properties": {
                "evidencias": {"type": "array", "items": {"type": "string"}},
                "motivos_verdadeiro_positivo": {"type": "array", "items": {"type": "string"}},
                "motivos_falso_positivo": {"type": "array", "items": {"type": "string"}},
                "suposicoes": {"type": "array", "items": {"type": "string"}},
                "observacoes_explorabilidade": {"type": "array", "items": {"type": "string"}},
                "exemplos_remediacao": {"type": "array", "items": {"type": "string"}}
            },
            "required": [
                "evidencias",
                "motivos_verdadeiro_positivo",
                "motivos_falso_positivo",
                "suposicoes",
                "observacoes_explorabilidade",
                "exemplos_remediacao"
            ],
            "additionalProperties": False
        },
        "mitigacoes": {
            "type": "object",
            "properties": {
                "codigo": {"type": "array", "items": {"type": "string"}},
                "api": {"type": "array", "items": {"type": "string"}},
                "aplicacao": {"type": "array", "items": {"type": "string"}},
                "banco_dados": {"type": "array", "items": {"type": "string"}},
                "infraestrutura": {"type": "array", "items": {"type": "string"}},
                "pipeline": {"type": "array", "items": {"type": "string"}},
                "monitoramento": {"type": "array", "items": {"type": "string"}}
            },
            "required": [
                "codigo", "api", "aplicacao", "banco_dados",
                "infraestrutura", "pipeline", "monitoramento"
            ],
            "additionalProperties": False
        },
        "resumo_correcao_segura": {"type": "array", "items": {"type": "string"}},
        "correcao_necessaria": {"type": "boolean"}
    },
    "required": [
        "classificacao",
        "confianca",
        "severidade",
        "cwe_estimado",
        "cvss_estimado",
        "explicacao",
        "xai",
        "mitigacoes",
        "resumo_correcao_segura",
        "correcao_necessaria"
    ],
    "additionalProperties": False
}


# Esquema JSON para a resposta de correção.
ESQUEMA_CORRECAO = {
    "type": "object",
    "properties": {
        "linguagem": {"type": "string"},
        "resumo": {"type": "string"},
        "diff_unificado": {"type": "string"},
        "exemplo_codigo_seguro": {"type": "string"},
        "observacoes": {"type": "array", "items": {"type": "string"}}
    },
    "required": ["linguagem", "resumo", "diff_unificado", "exemplo_codigo_seguro", "observacoes"],
    "additionalProperties": False
}