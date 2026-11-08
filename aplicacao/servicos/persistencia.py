"""
Módulo: persistencia.py

Responsabilidade:
-----------------
Centralizar toda a persistência PostgreSQL do VeritasSec.

Este módulo registra:

1. Execuções da análise na tabela execucoes.
2. Achados SAST consolidados na tabela dataset_analise.
3. Avaliações individuais por provedor em avaliacoes_modelos.
4. Métricas operacionais por provedor em metricas_provedores.
5. Texto base para futura vetorização em base_conhecimento_vetorial.
6. Achados complementares/contextuais para LLM em achados_complementares.

Correção desta versão:
----------------------
A função persistir_achado_complementar() agora suporta o novo fluxo de
classificação inferencial dos complementares pela LLM.

Campos adicionados para complementares classificados:

- tipo_semantico;
- classificacao_llm;
- risco_llm;
- confianca_llm;
- decisao_final_llm;
- avaliacoes_llm;
- classificado_por_llm;
- classificado_em.

Correção importante contra duplicação:
--------------------------------------
O mesmo complementar pode ser persistido em dois momentos:

1. após normalização;
2. após classificação pela LLM.

Para não duplicar linhas, a função agora procura registro existente por:

- id_execucao;
- identificador_achado.

Se existir, atualiza.
Se não existir, insere.

Decisão metodológica:
---------------------
Achados SAST e achados complementares NÃO são a mesma entidade.

- persistir_achado():
    Persiste achados originados do SARIF/SAST avaliados pela LLM.

- persistir_achado_complementar():
    Persiste sinais, exposições, red flags e evidências contextuais coletadas
    pela varredura complementar para ampliar a inferência da LLM.

Achados complementares NÃO representam vulnerabilidades confirmadas.
Eles são entidades auxiliares persistíveis para análise científica,
rastreabilidade, gráficos e comparação experimental.
"""

import json
import logging
from typing import Any

import psycopg2
from psycopg2.extras import Json

from aplicacao.nucleo.configuracoes import configuracoes

logger = logging.getLogger(__name__)


def _remover_caracteres_nulos(valor: Any) -> Any:
    """
    Remove caracteres NUL de strings, listas e dicionários.

    Motivo:
    -------
    PostgreSQL rejeita strings contendo caractere NUL.
    Como trechos de código podem conter bytes estranhos, esta sanitização
    evita falha de persistência em massa.
    """

    if valor is None:
        return None

    if isinstance(valor, str):
        return valor.replace("\x00", "")

    if isinstance(valor, list):
        return [_remover_caracteres_nulos(item) for item in valor]

    if isinstance(valor, dict):
        return {
            _remover_caracteres_nulos(chave): _remover_caracteres_nulos(item)
            for chave, item in valor.items()
        }

    return valor


def _normalizar_texto(valor: Any, padrao: str | None = None) -> str | None:
    """
    Converte valores para texto seguro para PostgreSQL.
    """

    valor = _remover_caracteres_nulos(valor)

    if valor is None or valor == "":
        return padrao

    if isinstance(valor, (dict, list)):
        return json.dumps(valor, ensure_ascii=False)

    return str(valor)


def _normalizar_inteiro(valor: Any, padrao: int | None = None) -> int | None:
    """
    Converte valor para inteiro quando possível.
    """

    if valor is None or valor == "":
        return padrao

    try:
        return int(valor)
    except (TypeError, ValueError):
        return padrao


def _normalizar_float(valor: Any, padrao: float | None = None) -> float | None:
    """
    Converte valor para float quando possível.
    """

    if valor is None or valor == "":
        return padrao

    try:
        return float(valor)
    except (TypeError, ValueError):
        return padrao


def _dict_ou_vazio(valor: Any) -> dict:
    """
    Garante que o valor seja um dicionário.
    """

    if isinstance(valor, dict):
        return _remover_caracteres_nulos(valor)

    return {}


def _json_seguro(valor: Any, padrao: Any = None) -> Json:
    """
    Prepara um valor seguro para persistência em colunas JSONB.
    """

    if padrao is None:
        padrao = {}

    valor_limpo = _remover_caracteres_nulos(valor)

    if valor_limpo is None:
        valor_limpo = padrao

    return Json(valor_limpo)


def obter_conexao():
    """
    Abre conexão com PostgreSQL.
    """

    if not configuracoes.USAR_POSTGRES:
        raise RuntimeError("Persistência PostgreSQL desabilitada.")

    return psycopg2.connect(
        configuracoes.URI_POSTGRES,
        connect_timeout=5,
    )


def persistir_execucao(dados_execucao: dict) -> int:
    """
    Persiste uma execução de análise na tabela execucoes.
    """

    conexao = None
    cursor = None

    try:
        if not configuracoes.USAR_POSTGRES:
            logger.warning("Persistência PostgreSQL desabilitada.")
            return -1

        dados_execucao = _dict_ou_vazio(dados_execucao)

        conexao = obter_conexao()
        cursor = conexao.cursor()

        cursor.execute(
            """
            INSERT INTO execucoes (
                raiz_projeto,
                caminho_sarif,
                nome_sistema,
                tipo_entrada,
                quantidade_achados,
                linhas_contexto,
                prompt_version,
                contrato_ativo,
                fallback_ativo,
                usar_gemini,
                usar_openai,
                usar_ollama,
                modelo_gemini,
                modelo_openai,
                modelo_ollama,
                hash_arquivo,
                status,
                erro_execucao,
                iniciado_em
            )
            VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, NOW()
            )
            RETURNING id
            """,
            (
                _normalizar_texto(dados_execucao.get("raiz_projeto")),
                _normalizar_texto(dados_execucao.get("caminho_sarif")),
                _normalizar_texto(dados_execucao.get("nome_sistema"), "Sistema"),
                _normalizar_texto(dados_execucao.get("tipo_entrada"), "sarif"),
                _normalizar_inteiro(dados_execucao.get("quantidade_achados"), 0),
                _normalizar_inteiro(dados_execucao.get("linhas_contexto"), 0),
                _normalizar_texto(
                    dados_execucao.get("prompt_version"),
                    "prompt_contextual_v1",
                ),
                bool(dados_execucao.get("contrato_ativo", True)),
                bool(dados_execucao.get("fallback_ativo", False)),
                bool(dados_execucao.get("usar_gemini", False)),
                bool(dados_execucao.get("usar_openai", False)),
                bool(dados_execucao.get("usar_ollama", False)),
                _normalizar_texto(
                    dados_execucao.get("modelo_gemini"),
                    "nao_configurado",
                ),
                _normalizar_texto(
                    dados_execucao.get("modelo_openai"),
                    "nao_configurado",
                ),
                _normalizar_texto(
                    dados_execucao.get("modelo_ollama"),
                    "nao_configurado",
                ),
                _normalizar_texto(
                    dados_execucao.get("hash_arquivo"),
                    "hash_nao_calculado",
                ),
                _normalizar_texto(dados_execucao.get("status"), "iniciada"),
                _normalizar_texto(dados_execucao.get("erro_execucao"), "sem_erro"),
            ),
        )

        resultado = cursor.fetchone()

        if not resultado:
            raise RuntimeError("PostgreSQL não retornou id da execução.")

        id_execucao = resultado[0]

        conexao.commit()

        logger.info("Execução persistida com sucesso. id_execucao=%s", id_execucao)

        return id_execucao

    except Exception:
        if conexao is not None:
            conexao.rollback()

        logger.exception("Falha ao persistir execução.")
        return -1

    finally:
        if cursor is not None:
            cursor.close()

        if conexao is not None:
            conexao.close()


def atualizar_execucao_finalizada(
    id_execucao: int,
    status: str,
    duracao_ms: float,
    erro_execucao: str = "sem_erro",
) -> None:
    """
    Atualiza uma execução ao final do processamento.
    """

    conexao = None
    cursor = None

    try:
        if not configuracoes.USAR_POSTGRES:
            logger.warning("Persistência PostgreSQL desabilitada.")
            return

        id_execucao_normalizado = _normalizar_inteiro(id_execucao)

        if not id_execucao_normalizado or id_execucao_normalizado <= 0:
            logger.warning("id_execucao inválido para finalização: %s", id_execucao)
            return

        conexao = obter_conexao()
        cursor = conexao.cursor()

        cursor.execute(
            """
            UPDATE execucoes
            SET
                status = %s,
                finalizado_em = NOW(),
                duracao_ms = %s,
                erro_execucao = %s
            WHERE id = %s
            """,
            (
                _normalizar_texto(status, "finalizada"),
                _normalizar_float(duracao_ms, 0.0),
                _normalizar_texto(erro_execucao, "sem_erro"),
                id_execucao_normalizado,
            ),
        )

        conexao.commit()

        logger.info(
            "Execução finalizada. id_execucao=%s status=%s duracao_ms=%s",
            id_execucao_normalizado,
            status,
            duracao_ms,
        )

    except Exception:
        if conexao is not None:
            conexao.rollback()

        logger.exception("Falha ao atualizar finalização da execução.")

    finally:
        if cursor is not None:
            cursor.close()

        if conexao is not None:
            conexao.close()


def persistir_achado(dados_achado: dict) -> None:
    """
    Persiste um achado SAST completo.

    Esta função grava:
    ------------------
    1. Registro consolidado em dataset_analise.
    2. Uma linha por provedor em avaliacoes_modelos.
    3. Uma linha por provedor em metricas_provedores.
    4. Texto preparado para RAG em base_conhecimento_vetorial.

    Importante:
    -----------
    Esta função deve continuar sendo usada para achados originados do SAST/SARIF.

    Não use esta função para achados complementares/contextuais, pois isso
    misturaria entidades metodologicamente diferentes.
    """

    conexao = None
    cursor = None

    try:
        if not configuracoes.USAR_POSTGRES:
            logger.warning("Persistência PostgreSQL desabilitada.")
            return

        dados_achado = _dict_ou_vazio(dados_achado)

        conexao = obter_conexao()
        cursor = conexao.cursor()

        achado = _dict_ou_vazio(dados_achado.get("achado"))
        decisao_final = _dict_ou_vazio(dados_achado.get("decisao_final"))
        correcao = _dict_ou_vazio(dados_achado.get("correcao"))
        avaliacoes = _dict_ou_vazio(dados_achado.get("avaliacoes"))
        metricas_provedores = _dict_ou_vazio(dados_achado.get("metricas_provedores"))
        dados_achado_llm = _dict_ou_vazio(dados_achado.get("dados_achado_llm"))

        id_execucao = _normalizar_inteiro(dados_achado.get("id_execucao"))

        if not id_execucao or id_execucao <= 0:
            raise RuntimeError(f"id_execucao inválido: {id_execucao}")

        fingerprint = _normalizar_texto(dados_achado.get("fingerprint"))

        identificador_achado = _normalizar_texto(
            achado.get("identificador_achado")
            or achado.get("id")
            or dados_achado_llm.get("identificador_achado")
            or dados_achado_llm.get("id")
            or fingerprint
        )

        regra = _normalizar_texto(
            achado.get("regra")
            or achado.get("identificador_regra")
            or achado.get("rule_id")
            or dados_achado_llm.get("regra")
            or dados_achado_llm.get("identificador_regra")
        )

        linguagem = _normalizar_texto(
            achado.get("linguagem") or dados_achado_llm.get("linguagem")
        )

        arquivo = _normalizar_texto(
            achado.get("arquivo")
            or achado.get("caminho_arquivo")
            or dados_achado_llm.get("arquivo")
            or dados_achado_llm.get("caminho_arquivo")
        )

        linha_inicio = _normalizar_inteiro(
            achado.get("linha_inicio")
            or achado.get("linha_inicial")
            or dados_achado_llm.get("linha_inicio")
            or dados_achado_llm.get("linha_inicial")
        )

        linha_fim = _normalizar_inteiro(
            achado.get("linha_fim")
            or achado.get("linha_final")
            or dados_achado_llm.get("linha_fim")
            or dados_achado_llm.get("linha_final")
        )

        trecho_codigo = _normalizar_texto(
            achado.get("trecho_codigo") or dados_achado_llm.get("trecho_codigo")
        )

        contexto_expandido = _normalizar_texto(
            achado.get("contexto_expandido")
            or dados_achado_llm.get("contexto_expandido")
        )

        contexto_relacionado = _normalizar_texto(
            achado.get("contexto_relacionado")
            or dados_achado_llm.get("contexto_relacionado")
        )

        classificacao = _normalizar_texto(decisao_final.get("classificacao"))
        severidade = _normalizar_texto(decisao_final.get("severidade"))
        cwe = _normalizar_texto(decisao_final.get("cwe"))
        cvss = _normalizar_float(decisao_final.get("cvss"))
        risco = _normalizar_texto(decisao_final.get("risco"))
        consenso = _normalizar_texto(decisao_final.get("consenso"))
        confianca = _normalizar_float(decisao_final.get("confianca"))
        explicacao = _normalizar_texto(decisao_final.get("explicacao"))

        xai_evidencias = _remover_caracteres_nulos(
            decisao_final.get("xai_evidencias") or decisao_final.get("evidencias") or []
        )

        if not isinstance(xai_evidencias, (list, dict)):
            xai_evidencias = []

        xai_falso_positivo = _normalizar_texto(decisao_final.get("xai_falso_positivo"))

        xai_verdadeiro_positivo = _normalizar_texto(
            decisao_final.get("xai_verdadeiro_positivo")
        )

        mitigacao_codigo = _normalizar_texto(
            correcao.get("codigo") or correcao.get("mitigacao_codigo")
        )

        mitigacao_api = _normalizar_texto(
            correcao.get("api") or correcao.get("mitigacao_api")
        )

        mitigacao_infra = _normalizar_texto(
            correcao.get("infra")
            or correcao.get("infraestrutura")
            or correcao.get("mitigacao_infra")
        )

        tempo_resposta_ms = _normalizar_float(dados_achado.get("tempo_resposta_ms"))
        tempo_total_achado_ms = _normalizar_float(
            dados_achado.get("tempo_total_achado_ms")
        )

        logger.info(
            "Persistindo dataset_analise: id_execucao=%s classificacao=%s arquivo=%s regra=%s",
            id_execucao,
            classificacao,
            arquivo,
            regra,
        )

        cursor.execute(
            """
            INSERT INTO dataset_analise (
                id_execucao,
                fingerprint,
                identificador_achado,
                regra,
                linguagem,
                arquivo,
                linha_inicio,
                linha_fim,
                trecho_codigo,
                contexto_expandido,
                contexto_relacionado,
                dados_achado_llm,
                classificacao,
                severidade,
                cwe,
                cvss,
                risco,
                consenso,
                confianca,
                explicacao,
                xai_evidencias,
                xai_falso_positivo,
                xai_verdadeiro_positivo,
                mitigacao_codigo,
                mitigacao_api,
                mitigacao_infra,
                tempo_resposta_ms,
                tempo_total_achado_ms,
                metricas_provedores,
                avaliacoes,
                decisao_final,
                correcao
            )
            VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s
            )
            RETURNING id
            """,
            (
                id_execucao,
                fingerprint,
                identificador_achado,
                regra,
                linguagem,
                arquivo,
                linha_inicio,
                linha_fim,
                trecho_codigo,
                contexto_expandido,
                contexto_relacionado,
                _json_seguro(dados_achado_llm, {}),
                classificacao,
                severidade,
                cwe,
                cvss,
                risco,
                consenso,
                confianca,
                explicacao,
                _json_seguro(xai_evidencias, []),
                xai_falso_positivo,
                xai_verdadeiro_positivo,
                mitigacao_codigo,
                mitigacao_api,
                mitigacao_infra,
                tempo_resposta_ms,
                tempo_total_achado_ms,
                _json_seguro(metricas_provedores, {}),
                _json_seguro(avaliacoes, {}),
                _json_seguro(decisao_final, {}),
                _json_seguro(correcao, {}),
            ),
        )

        resultado = cursor.fetchone()

        if not resultado:
            raise RuntimeError("Falha ao obter id_dataset_analise.")

        id_dataset_analise = resultado[0]

        for nome_provedor, avaliacao in avaliacoes.items():
            if not isinstance(avaliacao, dict):
                continue

            avaliacao = _dict_ou_vazio(avaliacao)
            metrica = _dict_ou_vazio(metricas_provedores.get(nome_provedor))

            cursor.execute(
                """
                INSERT INTO avaliacoes_modelos (
                    id_execucao,
                    id_dataset_analise,
                    provedor,
                    modelo,
                    status,
                    classificacao,
                    severidade,
                    cwe,
                    cvss,
                    risco,
                    consenso,
                    confianca,
                    explicacao,
                    resposta_bruta,
                    erro_resumido,
                    tempo_resposta_ms
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s
                )
                """,
                (
                    id_execucao,
                    id_dataset_analise,
                    _normalizar_texto(nome_provedor),
                    _normalizar_texto(avaliacao.get("modelo")),
                    _normalizar_texto(metrica.get("status")),
                    _normalizar_texto(avaliacao.get("classificacao")),
                    _normalizar_texto(avaliacao.get("severidade")),
                    _normalizar_texto(avaliacao.get("cwe")),
                    _normalizar_float(avaliacao.get("cvss")),
                    _normalizar_texto(avaliacao.get("risco")),
                    _normalizar_texto(avaliacao.get("consenso")),
                    _normalizar_float(avaliacao.get("confianca")),
                    _normalizar_texto(avaliacao.get("explicacao")),
                    _json_seguro(avaliacao, {}),
                    _normalizar_texto(metrica.get("erro_resumido")),
                    _normalizar_float(metrica.get("tempo_resposta_ms")),
                ),
            )

        for nome_provedor, metrica in metricas_provedores.items():
            if not isinstance(metrica, dict):
                continue

            metrica = _dict_ou_vazio(metrica)

            cursor.execute(
                """
                INSERT INTO metricas_provedores (
                    id_execucao,
                    id_dataset_analise,
                    provedor,
                    status,
                    tempo_resposta_ms,
                    erro_resumido
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    id_execucao,
                    id_dataset_analise,
                    _normalizar_texto(nome_provedor),
                    _normalizar_texto(metrica.get("status")),
                    _normalizar_float(metrica.get("tempo_resposta_ms")),
                    _normalizar_texto(metrica.get("erro_resumido")),
                ),
            )

        texto_embedding = "\n".join(
            [
                f"Regra: {regra or ''}",
                f"Arquivo: {arquivo or ''}",
                f"Classificacao: {classificacao or ''}",
                f"Risco: {risco or ''}",
                f"CWE: {cwe or ''}",
                "",
                trecho_codigo or "",
                contexto_expandido or "",
                contexto_relacionado or "",
                explicacao or "",
            ]
        ).strip()

        texto_embedding = _normalizar_texto(texto_embedding)

        if texto_embedding:
            cursor.execute(
                """
                INSERT INTO base_conhecimento_vetorial (
                    id_execucao,
                    id_dataset_analise,
                    tipo_conteudo,
                    origem,
                    texto,
                    metadados,
                    modelo_embedding
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    id_execucao,
                    id_dataset_analise,
                    "achado_sast",
                    arquivo,
                    texto_embedding,
                    _json_seguro(
                        {
                            "fingerprint": fingerprint,
                            "identificador_achado": identificador_achado,
                            "regra": regra,
                            "arquivo": arquivo,
                            "classificacao": classificacao,
                            "risco": risco,
                            "cwe": cwe,
                            "embedding_status": "pendente",
                        },
                        {},
                    ),
                    "pendente_embedding_real",
                ),
            )

        conexao.commit()

        logger.info(
            "Persistência completa do achado SAST realizada. id_execucao=%s id_dataset=%s",
            id_execucao,
            id_dataset_analise,
        )

    except Exception:
        if conexao is not None:
            conexao.rollback()

        logger.exception("Falha ao persistir achado SAST.")

    finally:
        if cursor is not None:
            cursor.close()

        if conexao is not None:
            conexao.close()


def garantir_tabela_achados_complementares(cursor) -> None:
    """
    Garante a existência e evolução da tabela achados_complementares.

    Esta função é compatível com bancos antigos:
    - cria a tabela se não existir;
    - adiciona colunas novas com ALTER TABLE IF NOT EXISTS;
    - cria índices úteis para consulta e gráficos.
    """

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS achados_complementares (
            id SERIAL PRIMARY KEY,
            id_execucao INTEGER NOT NULL REFERENCES execucoes(id) ON DELETE CASCADE,
            identificador_achado TEXT NOT NULL,
            tipo_origem TEXT NOT NULL DEFAULT 'complementar_para_llm',
            origem TEXT NOT NULL DEFAULT 'varredura_complementar_projeto',
            nome_sistema TEXT,
            raiz_projeto TEXT,
            tipo TEXT,
            descricao TEXT,
            arquivo TEXT,
            linha INTEGER,
            trecho TEXT,
            severidade_sugerida TEXT,
            evidencia_original JSONB NOT NULL DEFAULT '{}'::jsonb,
            metadados JSONB NOT NULL DEFAULT '{}'::jsonb,
            observacao_metodologica TEXT,
            criado_em TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
        )
        """)

    cursor.execute("""
        ALTER TABLE achados_complementares
        ADD COLUMN IF NOT EXISTS tipo_semantico TEXT
        """)

    cursor.execute("""
        ALTER TABLE achados_complementares
        ADD COLUMN IF NOT EXISTS classificacao_llm TEXT
        """)

    cursor.execute("""
        ALTER TABLE achados_complementares
        ADD COLUMN IF NOT EXISTS risco_llm TEXT
        """)

    cursor.execute("""
        ALTER TABLE achados_complementares
        ADD COLUMN IF NOT EXISTS confianca_llm DOUBLE PRECISION
        """)

    cursor.execute("""
        ALTER TABLE achados_complementares
        ADD COLUMN IF NOT EXISTS decisao_final_llm JSONB NOT NULL DEFAULT '{}'::jsonb
        """)

    cursor.execute("""
        ALTER TABLE achados_complementares
        ADD COLUMN IF NOT EXISTS avaliacoes_llm JSONB NOT NULL DEFAULT '{}'::jsonb
        """)

    cursor.execute("""
        ALTER TABLE achados_complementares
        ADD COLUMN IF NOT EXISTS classificado_por_llm BOOLEAN NOT NULL DEFAULT FALSE
        """)

    cursor.execute("""
        ALTER TABLE achados_complementares
        ADD COLUMN IF NOT EXISTS classificado_em TIMESTAMP WITHOUT TIME ZONE
        """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_achados_complementares_execucao
        ON achados_complementares(id_execucao)
        """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_achados_complementares_tipo
        ON achados_complementares(tipo)
        """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_achados_complementares_tipo_origem
        ON achados_complementares(tipo_origem)
        """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_achados_complementares_arquivo
        ON achados_complementares(arquivo)
        """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_achados_complementares_classificacao_llm
        ON achados_complementares(classificacao_llm)
        """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_achados_complementares_risco_llm
        ON achados_complementares(risco_llm)
        """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_achados_complementares_classificado_por_llm
        ON achados_complementares(classificado_por_llm)
        """)


def persistir_achado_complementar(dados_complementares: dict) -> None:
    """
    Persiste ou atualiza um achado complementar/contextual para LLM.

    Esta função NÃO persiste achado SAST.

    Objetivo:
    ---------
    Registrar sinais contextuais extraídos do projeto e, quando disponível,
    registrar também a classificação inferencial feita pela LLM.

    Correção importante:
    --------------------
    O complementar pode chegar em dois estados:

    1. Antes da classificação:
       - apenas normalizado;
       - sem classificacao_llm.

    2. Depois da classificação:
       - com classificacao_llm;
       - com risco_llm;
       - com confianca_llm;
       - com decisao_final_llm;
       - com avaliacoes_llm.

    Para evitar duplicação, esta função atualiza o registro existente quando
    encontra o mesmo:

    - id_execucao;
    - identificador_achado.

    Se não encontrar, insere novo registro.
    """

    conexao = None
    cursor = None

    try:
        if not configuracoes.USAR_POSTGRES:
            logger.warning("Persistência PostgreSQL desabilitada.")
            return

        dados_complementares = _dict_ou_vazio(dados_complementares)

        id_execucao = _normalizar_inteiro(dados_complementares.get("id_execucao"))

        if not id_execucao or id_execucao <= 0:
            raise RuntimeError(
                f"id_execucao inválido para achado complementar: {id_execucao}"
            )

        identificador_achado = _normalizar_texto(
            dados_complementares.get("identificador_achado")
            or dados_complementares.get("id")
            or dados_complementares.get("fingerprint"),
            "complementar_sem_identificador",
        )

        tipo_origem = _normalizar_texto(
            dados_complementares.get("tipo_origem"),
            "complementar_para_llm",
        )

        origem = _normalizar_texto(
            dados_complementares.get("origem"),
            "varredura_complementar_projeto",
        )

        nome_sistema = _normalizar_texto(dados_complementares.get("nome_sistema"))
        raiz_projeto = _normalizar_texto(dados_complementares.get("raiz_projeto"))

        tipo = _normalizar_texto(
            dados_complementares.get("tipo")
            or dados_complementares.get("categoria")
            or dados_complementares.get("classificacao_complementar"),
            "exposicao_complementar",
        )

        tipo_semantico = _normalizar_texto(
            dados_complementares.get("tipo_semantico")
            or dados_complementares.get("tipo_exposicao")
            or tipo,
            "evidencia_contextual",
        )

        descricao = _normalizar_texto(
            dados_complementares.get("descricao")
            or dados_complementares.get("mensagem")
            or dados_complementares.get("regra"),
            "Exposição complementar identificada para inferência da LLM.",
        )

        arquivo = _normalizar_texto(
            dados_complementares.get("arquivo")
            or dados_complementares.get("caminho")
            or dados_complementares.get("caminho_arquivo")
        )

        linha = _normalizar_inteiro(
            dados_complementares.get("linha")
            or dados_complementares.get("linha_inicio")
            or dados_complementares.get("linha_inicial")
        )

        trecho = _normalizar_texto(
            dados_complementares.get("trecho")
            or dados_complementares.get("codigo")
            or dados_complementares.get("trecho_codigo")
        )

        severidade_sugerida = _normalizar_texto(
            dados_complementares.get("severidade_sugerida")
            or dados_complementares.get("severidade")
        )

        classificacao_llm = _normalizar_texto(
            dados_complementares.get("classificacao_llm")
        )

        risco_llm = _normalizar_texto(dados_complementares.get("risco_llm"))

        confianca_llm = _normalizar_float(dados_complementares.get("confianca_llm"))

        decisao_final_llm = _dict_ou_vazio(
            dados_complementares.get("decisao_final_llm")
        )

        avaliacoes_llm = _dict_ou_vazio(dados_complementares.get("avaliacoes_llm"))

        classificado_por_llm = bool(
            classificacao_llm
            or risco_llm
            or confianca_llm is not None
            or decisao_final_llm
            or avaliacoes_llm
        )

        evidencia_original = (
            dados_complementares.get("evidencia_original")
            or dados_complementares.get("evidencia")
            or dados_complementares
        )

        observacao_metodologica = _normalizar_texto(
            dados_complementares.get("observacao_metodologica"),
            (
                "Este item não representa vulnerabilidade confirmada. "
                "Ele é um sinal contextual persistível para ampliar o universo "
                "de inferência da LLM."
            ),
        )

        metadados = {
            "tipo_origem": tipo_origem,
            "origem": origem,
            "nome_sistema": nome_sistema,
            "raiz_projeto": raiz_projeto,
            "identificador_achado": identificador_achado,
            "tipo_semantico": tipo_semantico,
            "uso_metodologico": "complementar_para_inferencia_llm",
            "vulnerabilidade_confirmada": False,
            "classe_epistemologica": "evidencia_contextual",
            "classificado_por_llm": classificado_por_llm,
            "classificacao_llm": classificacao_llm,
            "risco_llm": risco_llm,
            "confianca_llm": confianca_llm,
        }

        conexao = obter_conexao()
        cursor = conexao.cursor()

        garantir_tabela_achados_complementares(cursor)

        cursor.execute(
            """
            SELECT id
            FROM achados_complementares
            WHERE id_execucao = %s
              AND identificador_achado = %s
            ORDER BY id ASC
            LIMIT 1
            """,
            (
                id_execucao,
                identificador_achado,
            ),
        )

        registro_existente = cursor.fetchone()

        if registro_existente:
            id_achado_complementar = registro_existente[0]

            cursor.execute(
                """
                UPDATE achados_complementares
                SET
                    tipo_origem = %s,
                    origem = %s,
                    nome_sistema = %s,
                    raiz_projeto = %s,
                    tipo = %s,
                    tipo_semantico = %s,
                    descricao = %s,
                    arquivo = %s,
                    linha = %s,
                    trecho = %s,
                    severidade_sugerida = %s,
                    evidencia_original = %s,
                    metadados = %s,
                    observacao_metodologica = %s,
                    classificacao_llm = %s,
                    risco_llm = %s,
                    confianca_llm = %s,
                    decisao_final_llm = %s,
                    avaliacoes_llm = %s,
                    classificado_por_llm = %s,
                    classificado_em = CASE
                        WHEN %s THEN NOW()
                        ELSE classificado_em
                    END
                WHERE id = %s
                """,
                (
                    tipo_origem,
                    origem,
                    nome_sistema,
                    raiz_projeto,
                    tipo,
                    tipo_semantico,
                    descricao,
                    arquivo,
                    linha,
                    trecho,
                    severidade_sugerida,
                    _json_seguro(evidencia_original, {}),
                    _json_seguro(metadados, {}),
                    observacao_metodologica,
                    classificacao_llm,
                    risco_llm,
                    confianca_llm,
                    _json_seguro(decisao_final_llm, {}),
                    _json_seguro(avaliacoes_llm, {}),
                    classificado_por_llm,
                    classificado_por_llm,
                    id_achado_complementar,
                ),
            )

            operacao = "atualizado"

        else:
            cursor.execute(
                """
                INSERT INTO achados_complementares (
                    id_execucao,
                    identificador_achado,
                    tipo_origem,
                    origem,
                    nome_sistema,
                    raiz_projeto,
                    tipo,
                    tipo_semantico,
                    descricao,
                    arquivo,
                    linha,
                    trecho,
                    severidade_sugerida,
                    evidencia_original,
                    metadados,
                    observacao_metodologica,
                    classificacao_llm,
                    risco_llm,
                    confianca_llm,
                    decisao_final_llm,
                    avaliacoes_llm,
                    classificado_por_llm,
                    classificado_em
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s,
                    CASE WHEN %s THEN NOW() ELSE NULL END
                )
                RETURNING id
                """,
                (
                    id_execucao,
                    identificador_achado,
                    tipo_origem,
                    origem,
                    nome_sistema,
                    raiz_projeto,
                    tipo,
                    tipo_semantico,
                    descricao,
                    arquivo,
                    linha,
                    trecho,
                    severidade_sugerida,
                    _json_seguro(evidencia_original, {}),
                    _json_seguro(metadados, {}),
                    observacao_metodologica,
                    classificacao_llm,
                    risco_llm,
                    confianca_llm,
                    _json_seguro(decisao_final_llm, {}),
                    _json_seguro(avaliacoes_llm, {}),
                    classificado_por_llm,
                    classificado_por_llm,
                ),
            )

            resultado = cursor.fetchone()

            if not resultado:
                raise RuntimeError("Falha ao obter id do achado complementar.")

            id_achado_complementar = resultado[0]
            operacao = "inserido"

        texto_embedding = "\n".join(
            [
                f"Tipo: {tipo or ''}",
                f"Tipo semantico: {tipo_semantico or ''}",
                f"Origem: {origem or ''}",
                f"Arquivo: {arquivo or ''}",
                f"Linha: {linha or ''}",
                f"Descricao: {descricao or ''}",
                f"Classificacao LLM: {classificacao_llm or ''}",
                f"Risco LLM: {risco_llm or ''}",
                f"Confianca LLM: {confianca_llm if confianca_llm is not None else ''}",
                "",
                trecho or "",
                "",
                observacao_metodologica or "",
            ]
        ).strip()

        texto_embedding = _normalizar_texto(texto_embedding)

        if texto_embedding:
            cursor.execute(
                """
                INSERT INTO base_conhecimento_vetorial (
                    id_execucao,
                    id_dataset_analise,
                    tipo_conteudo,
                    origem,
                    texto,
                    metadados,
                    modelo_embedding
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    id_execucao,
                    None,
                    "achado_complementar_para_llm",
                    arquivo,
                    texto_embedding,
                    _json_seguro(
                        {
                            **metadados,
                            "id_achado_complementar": id_achado_complementar,
                            "tipo": tipo,
                            "tipo_semantico": tipo_semantico,
                            "arquivo": arquivo,
                            "linha": linha,
                            "classificacao_llm": classificacao_llm,
                            "risco_llm": risco_llm,
                            "confianca_llm": confianca_llm,
                            "embedding_status": "pendente",
                        },
                        {},
                    ),
                    "pendente_embedding_real",
                ),
            )

        conexao.commit()

        logger.info(
            (
                "Achado complementar %s. "
                "id_execucao=%s id_achado_complementar=%s tipo=%s "
                "classificacao_llm=%s risco_llm=%s arquivo=%s"
            ),
            operacao,
            id_execucao,
            id_achado_complementar,
            tipo,
            classificacao_llm,
            risco_llm,
            arquivo,
        )

    except Exception:
        if conexao is not None:
            conexao.rollback()

        logger.exception("Falha ao persistir achado complementar.")

    finally:
        if cursor is not None:
            cursor.close()

        if conexao is not None:
            conexao.close()
