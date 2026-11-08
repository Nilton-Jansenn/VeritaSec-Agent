"""
Módulo: extrator_fluxo.py

Objetivo:
---------
Extrair evidências básicas de fluxo de segurança para o VeritasSec.

Este módulo busca sinais de:

- source: origem de dado potencialmente controlado pelo usuário;
- sink: uso sensível/perigoso do dado;
- mitigação: validação, sanitização, cast, allowlist, prepared statement etc.;
- fluxo aproximado: relação textual entre entrada, transformação e uso sensível.

Papel arquitetural:
-------------------
Este módulo NÃO substitui SAST, DAST, CodeQL, Semgrep, análise manual ou
taint analysis completa.

Ele serve como camada complementar para enriquecer o prompt analítico da LLM.

Fluxo esperado no VeritasSec:

SARIF/CSV
    ↓
rotas.py identifica achado
    ↓
extrator_fluxo.py coleta evidências source/sink/mitigação
    ↓
extrator_exposicoes.py coleta secrets/red flags
    ↓
montador_prompt.py monta prompt analítico
    ↓
LLM realiza inferência contextual
    ↓
persistência/exportação

Limitações:
-----------
Esta versão é intencionalmente pragmática e regex-based.

Ela NÃO faz:
- AST completo;
- dataflow real;
- análise interprocedural;
- call graph;
- resolução de tipos;
- interpretação semântica profunda;
- análise perfeita por linguagem.

Essas limitações devem ser reconhecidas no artigo como ameaça à validade,
mas são aceitáveis para uma primeira etapa experimental reproduzível.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

TAMANHO_MAXIMO_ARQUIVO_BYTES = 2 * 1024 * 1024
JANELA_PADRAO_LINHAS = 40
LIMITE_EVIDENCIAS_POR_TIPO = 30


PADROES_SOURCE = [
    {
        "tipo": "http_query_param",
        "regex": r"(?i)(request\.args|getParameter|req\.query|\$_GET)",
        "descricao": "Entrada via parâmetro de query HTTP.",
    },
    {
        "tipo": "http_body",
        "regex": r"(?i)(request\.form|request\.json|req\.body|\$_POST)",
        "descricao": "Entrada via corpo da requisição HTTP.",
    },
    {
        "tipo": "http_header",
        "regex": r"(?i)(request\.headers|req\.headers|getHeader)",
        "descricao": "Entrada via cabeçalho HTTP.",
    },
    {
        "tipo": "path_param",
        "regex": r"(?i)(PathVariable|path_params|req\.params)",
        "descricao": "Entrada via parâmetro de rota.",
    },
    {
        "tipo": "input_console",
        "regex": r"(?i)(input\s*\(|Scanner\s*\(|readLine\s*\()",
        "descricao": "Entrada via console ou leitura direta.",
    },
    {
        "tipo": "environment_variable",
        "regex": r"(?i)(os\.getenv|System\.getenv|process\.env)",
        "descricao": "Entrada obtida de variável de ambiente.",
    },
    {
        "tipo": "file_input",
        "regex": r"(?i)(open\s*\(|FileInputStream|fs\.readFile|readFileSync)",
        "descricao": "Entrada ou conteúdo vindo de arquivo.",
    },
]


PADROES_SINK = [
    {
        "tipo": "sql_execution",
        "regex": r"(?i)(executeQuery\s*\(|executeUpdate\s*\(|execute\s*\(|cursor\.execute\s*\(|statement\.execute)",
        "descricao": "Execução de consulta SQL ou comando de banco.",
    },
    {
        "tipo": "command_execution",
        "regex": r"(?i)(os\.system\s*\(|subprocess\.|Runtime\.getRuntime\(\)\.exec|ProcessBuilder|child_process\.exec)",
        "descricao": "Execução de comando no sistema operacional.",
    },
    {
        "tipo": "dynamic_code_execution",
        "regex": r"(?i)(eval\s*\(|exec\s*\(|Function\s*\()",
        "descricao": "Execução dinâmica de código.",
    },
    {
        "tipo": "html_output",
        "regex": r"(?i)(innerHTML|dangerouslySetInnerHTML|res\.send\s*\(|response\.write\s*\()",
        "descricao": "Saída HTML potencialmente sensível.",
    },
    {
        "tipo": "file_access",
        "regex": r"(?i)(open\s*\(|File\s*\(|sendFile|readFileSync|fs\.readFile)",
        "descricao": "Acesso a arquivo ou caminho potencialmente controlável.",
    },
    {
        "tipo": "http_request",
        "regex": r"(?i)(requests\.get\s*\(|requests\.post\s*\(|axios\.|fetch\s*\(|HttpClient)",
        "descricao": "Chamada HTTP externa.",
    },
]


PADROES_MITIGACAO = [
    {
        "tipo": "validacao_numerica",
        "regex": r"(?i)(isdigit\s*\(|isnumeric\s*\(|Integer\.parseInt|Long\.parseLong|Number\s*\()",
        "descricao": "Validação ou conversão numérica.",
    },
    {
        "tipo": "regex_validation",
        "regex": r"(?i)(matches\s*\(|re\.match\s*\(|re\.fullmatch\s*\(|Pattern\.compile)",
        "descricao": "Validação por expressão regular.",
    },
    {
        "tipo": "allowlist",
        "regex": r"(?i)(allowlist|whitelist|lista_permitida|valores_permitidos|allowedValues)",
        "descricao": "Indício de allowlist.",
    },
    {
        "tipo": "sanitize_function",
        "regex": r"(?i)(sanitize\s*\(|sanitizar\s*\(|clean\s*\(|escape\s*\()",
        "descricao": "Função de sanitização ou escape.",
    },
    {
        "tipo": "html_escape",
        "regex": r"(?i)(html\.escape|escapeHtml|StringEscapeUtils|DOMPurify|sanitizeHtml)",
        "descricao": "Escape/sanitização para contexto HTML.",
    },
    {
        "tipo": "prepared_statement",
        "regex": r"(?i)(PreparedStatement|prepareStatement|setString\s*\(|setInt\s*\(|cursor\.execute\s*\([^,]+,\s*\()",
        "descricao": "Uso aparente de consulta parametrizada.",
    },
    {
        "tipo": "orm_seguro",
        "regex": r"(?i)(SQLAlchemy|EntityManager|JpaRepository|Hibernate|Prisma|Sequelize|TypeORM)",
        "descricao": "Uso de ORM ou abstração de persistência.",
    },
    {
        "tipo": "uuid_validation",
        "regex": r"(?i)(UUID\.fromString|uuid\.UUID)",
        "descricao": "Validação/conversão para UUID.",
    },
    {
        "tipo": "authorization_check",
        "regex": r"(?i)(hasRole|hasAuthority|isAuthenticated|authorize|authorization|permissao|permissão|RBAC)",
        "descricao": "Indício de autenticação/autorização.",
    },
]


def ler_arquivo_seguro(
    caminho_arquivo: str,
    tamanho_maximo_bytes: int = TAMANHO_MAXIMO_ARQUIVO_BYTES,
) -> list[str]:
    """
    Lê um arquivo de código de forma segura.

    Parâmetros:
    -----------
    caminho_arquivo:
        Caminho do arquivo a ser lido.

    tamanho_maximo_bytes:
        Limite máximo de leitura para evitar custo excessivo e degradação
        da análise.

    Retorno:
    --------
    Lista de linhas do arquivo.

    Observação:
    -----------
    Em caso de erro, retorna lista vazia. O pipeline não deve quebrar apenas
    porque um arquivo não pôde ser lido.
    """

    caminho = Path(caminho_arquivo)

    if not caminho.exists():
        return []

    try:
        if caminho.stat().st_size > tamanho_maximo_bytes:
            return []

        conteudo = caminho.read_text(
            encoding="utf-8",
            errors="ignore",
        )

        return conteudo.splitlines()

    except Exception:
        return []


def obter_janela_linhas(
    linhas: list[str],
    linha_referencia: int,
    linhas_antes: int = JANELA_PADRAO_LINHAS,
    linhas_depois: int = JANELA_PADRAO_LINHAS,
) -> list[tuple[int, str]]:
    """
    Obtém uma janela técnica de inspeção ao redor da linha do achado.

    Atenção metodológica:
    ---------------------
    Esta janela NÃO deve ser confundida com "linhas de contexto" do prompt
    contextual.

    No prompt analítico, a janela é usada apenas internamente pelo extrator
    para encontrar evidências próximas de fluxo, como source, sink e mitigação.

    O resultado enviado à LLM não é tratado como contexto bruto, mas como
    evidências estruturadas.

    Retorno:
    --------
    Lista de tuplas:
    (numero_linha_real, conteudo_linha)
    """

    if not linhas:
        return []

    total_linhas = len(linhas)

    inicio = max(1, linha_referencia - linhas_antes)
    fim = min(total_linhas, linha_referencia + linhas_depois)

    resultado = []

    for numero in range(inicio, fim + 1):
        resultado.append(
            (
                numero,
                linhas[numero - 1],
            )
        )

    return resultado


def aplicar_regras_em_linhas(
    linhas_numeradas: list[tuple[int, str]],
    regras: list[dict[str, str]],
    caminho_arquivo: str,
    limite: int = LIMITE_EVIDENCIAS_POR_TIPO,
) -> list[dict[str, Any]]:
    """
    Aplica regras regex em linhas numeradas.

    Esta função é genérica e serve para:
    - sources;
    - sinks;
    - mitigações.

    A função retorna evidências estruturadas com:
    - arquivo;
    - linha;
    - tipo;
    - descrição;
    - evidência textual.

    A limitação por quantidade evita payloads excessivos no prompt analítico.
    """

    evidencias: list[dict[str, Any]] = []

    for numero_linha, conteudo in linhas_numeradas:
        linha_processada = conteudo[:2000]

        for regra in regras:
            try:
                if re.search(regra["regex"], linha_processada):
                    evidencias.append(
                        {
                            "arquivo": caminho_arquivo,
                            "linha": numero_linha,
                            "tipo": regra["tipo"],
                            "descricao": regra["descricao"],
                            "evidencia": linha_processada.strip(),
                        }
                    )

                    if len(evidencias) >= limite:
                        return evidencias

            except Exception:
                continue

    return evidencias


def inferir_fluxo_resumido(
    sources: list[dict[str, Any]],
    mitigacoes: list[dict[str, Any]],
    sinks: list[dict[str, Any]],
) -> str:
    """
    Gera uma descrição textual resumida do fluxo encontrado.

    Importante:
    -----------
    Esta função NÃO comprova dataflow real.

    Ela apenas resume sinais próximos encontrados na janela técnica analisada.
    A LLM deverá tratar esse resumo como evidência auxiliar, não como prova.
    """

    partes = []

    if sources:
        tipos_source = sorted({item["tipo"] for item in sources})
        partes.append("source: " + ", ".join(tipos_source))

    if mitigacoes:
        tipos_mitigacao = sorted({item["tipo"] for item in mitigacoes})
        partes.append("mitigacao: " + ", ".join(tipos_mitigacao))

    if sinks:
        tipos_sink = sorted({item["tipo"] for item in sinks})
        partes.append("sink: " + ", ".join(tipos_sink))

    if not partes:
        return "nenhuma evidencia de fluxo identificada na janela analisada"

    return " -> ".join(partes)


def calcular_indicadores_fluxo(
    sources: list[dict[str, Any]],
    mitigacoes: list[dict[str, Any]],
    sinks: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Calcula indicadores booleanos simples sobre o fluxo.

    Esses indicadores ajudam a:
    - reduzir ambiguidade no prompt;
    - gerar métricas futuras;
    - apoiar a inferência da LLM.

    Atenção:
    --------
    São indicadores heurísticos, não prova formal.
    """

    return {
        "source_detectado": len(sources) > 0,
        "sink_detectado": len(sinks) > 0,
        "mitigacao_detectada": len(mitigacoes) > 0,
        "source_e_sink_detectados": len(sources) > 0 and len(sinks) > 0,
        "source_sink_sem_mitigacao_aparente": (
            len(sources) > 0 and len(sinks) > 0 and len(mitigacoes) == 0
        ),
        "mitigacao_presente_entre_evidencias": len(mitigacoes) > 0,
    }


def extrair_fluxo_contextual(
    caminho_arquivo: str,
    linha_achado: int | None,
    tipo_vulnerabilidade: str | None = None,
    janela_linhas: int = JANELA_PADRAO_LINHAS,
) -> dict[str, Any]:
    """
    Extrai evidências de fluxo para um achado específico.

    Parâmetros:
    -----------
    caminho_arquivo:
        Arquivo onde o achado foi identificado.

    linha_achado:
        Linha inicial apontada pelo SAST.

    tipo_vulnerabilidade:
        Tipo ou regra SAST, quando disponível.

    janela_linhas:
        Janela técnica usada internamente para procurar evidências próximas.
        No modo analítico, isso não representa uso de linhas de contexto no prompt.

    Retorno:
    --------
    Dicionário com:
    - arquivo_lido;
    - sources;
    - sinks;
    - mitigações;
    - indicadores;
    - fluxo_resumido;
    - limitações metodológicas.
    """

    if not caminho_arquivo or not linha_achado:
        return {
            "arquivo_lido": False,
            "arquivo": caminho_arquivo,
            "linha_achado": linha_achado,
            "tipo_vulnerabilidade": tipo_vulnerabilidade,
            "sources": [],
            "sinks": [],
            "mitigacoes": [],
            "indicadores": {},
            "fluxo_resumido": "dados insuficientes para extrair fluxo",
            "limitacoes": [
                "Caminho do arquivo ou linha do achado ausente.",
            ],
        }

    linhas = ler_arquivo_seguro(caminho_arquivo)

    if not linhas:
        return {
            "arquivo_lido": False,
            "arquivo": caminho_arquivo,
            "linha_achado": linha_achado,
            "tipo_vulnerabilidade": tipo_vulnerabilidade,
            "sources": [],
            "sinks": [],
            "mitigacoes": [],
            "indicadores": {},
            "fluxo_resumido": "arquivo nao lido ou vazio",
            "limitacoes": [
                "Arquivo não encontrado, vazio, muito grande ou ilegível.",
            ],
        }

    janela = obter_janela_linhas(
        linhas=linhas,
        linha_referencia=int(linha_achado),
        linhas_antes=janela_linhas,
        linhas_depois=janela_linhas,
    )

    sources = aplicar_regras_em_linhas(
        linhas_numeradas=janela,
        regras=PADROES_SOURCE,
        caminho_arquivo=caminho_arquivo,
    )

    sinks = aplicar_regras_em_linhas(
        linhas_numeradas=janela,
        regras=PADROES_SINK,
        caminho_arquivo=caminho_arquivo,
    )

    mitigacoes = aplicar_regras_em_linhas(
        linhas_numeradas=janela,
        regras=PADROES_MITIGACAO,
        caminho_arquivo=caminho_arquivo,
    )

    indicadores = calcular_indicadores_fluxo(
        sources=sources,
        mitigacoes=mitigacoes,
        sinks=sinks,
    )

    fluxo_resumido = inferir_fluxo_resumido(
        sources=sources,
        mitigacoes=mitigacoes,
        sinks=sinks,
    )

    return {
        "arquivo_lido": True,
        "arquivo": caminho_arquivo,
        "linha_achado": linha_achado,
        "tipo_vulnerabilidade": tipo_vulnerabilidade,
        "janela_tecnica_linhas": janela_linhas,
        "sources": sources,
        "sinks": sinks,
        "mitigacoes": mitigacoes,
        "indicadores": indicadores,
        "fluxo_resumido": fluxo_resumido,
        "limitacoes": [
            "Análise baseada em regex e janela técnica local.",
            "Não há prova de dataflow real nesta versão.",
            "Mitigações detectadas precisam ser avaliadas quanto à efetividade.",
            "Ausência de mitigação detectada não prova ausência de mitigação em outra camada.",
        ],
    }
