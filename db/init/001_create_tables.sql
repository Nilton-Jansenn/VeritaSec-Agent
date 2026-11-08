
CREATE TABLE IF NOT EXISTS execucoes (
    id SERIAL PRIMARY KEY,
    raiz_projeto TEXT,
    caminho_sarif TEXT,
    nome_sistema TEXT,
    tipo_entrada TEXT,
    quantidade_achados INTEGER,
    linhas_contexto INTEGER,
    prompt_version TEXT,
    contrato_ativo BOOLEAN,
    fallback_ativo BOOLEAN,
    usar_gemini BOOLEAN,
    usar_openai BOOLEAN,
    usar_ollama BOOLEAN,
    modelo_gemini TEXT,
    modelo_openai TEXT,
    modelo_ollama TEXT,
    hash_arquivo TEXT,
    status TEXT,
    erro_execucao TEXT,
    iniciado_em TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS achados (
    id SERIAL PRIMARY KEY,
    id_execucao INTEGER REFERENCES execucoes(id),
    dados JSONB
);

CREATE INDEX IF NOT EXISTS idx_achados_id_execucao
    ON achados(id_execucao);

CREATE TABLE IF NOT EXISTS dataset_analise (
    id SERIAL PRIMARY KEY,
    criado_em TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    id_execucao INTEGER,
    identificador_achado TEXT,
    regra TEXT,
    linguagem TEXT,
    arquivo TEXT,
    linha_inicio INTEGER,
    linha_fim INTEGER,
    trecho_codigo TEXT,
    contexto_expandido TEXT,
    contexto_relacionado TEXT,
    classificacao TEXT,
    severidade TEXT,
    cwe TEXT,
    cvss DOUBLE PRECISION,
    risco INTEGER,
    consenso TEXT,
    confianca DOUBLE PRECISION,
    explicacao TEXT,
    xai_evidencias TEXT,
    xai_falso_positivo TEXT,
    xai_verdadeiro_positivo TEXT,
    mitigacao_codigo TEXT,
    mitigacao_api TEXT,
    mitigacao_infra TEXT
);

CREATE INDEX IF NOT EXISTS idx_dataset_analise_id_execucao
    ON dataset_analise(id_execucao);

CREATE INDEX IF NOT EXISTS idx_dataset_analise_classificacao
    ON dataset_analise(classificacao);

