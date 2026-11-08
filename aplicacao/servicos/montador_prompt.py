"""
Módulo: montador_prompt.py

Objetivo:
---------
Centralizar os prompts usados pelo VeritasSec.

Modos suportados:

1. contextual
   Mantém o comportamento atual da aplicação.
   Usa trecho de código, contexto expandido e contexto relacionado.

2. analitico
   Novo prompt experimental.
   Foca em evidências de mitigação, explorabilidade, red flags,
   exposições indevidas e possíveis falsos negativos.

Compatibilidade:
----------------
As funções montar_prompt_analise() e montar_prompt_correcao() foram preservadas
para não quebrar chamadas existentes no rotas.py.
"""

from textwrap import dedent

from aplicacao.nucleo.configuracoes import configuracoes


def montar_prompt_analise_contextual(dados_achado: dict) -> str:
    """
    Prompt contextual atual.

    Este é o prompt que já estava na aplicação.
    Deve ser usado como cenário controle do experimento.
    """

    return dedent(f"""
    Você é um especialista sênior em segurança de software, revisão segura de código,
    modelagem de ameaças e validação contextual de achados SAST.

    Sua tarefa não é repetir o alerta da ferramenta.
    Sua tarefa é verificar a veracidade do achado no contexto real da aplicação.

    O resultado deve classificar o achado como:
    - verdadeiro_positivo
    - falso_positivo
    - inconclusivo

    Processo obrigatório:
    1. Analise o trecho exato do código.
    2. Analise o contexto expandido do arquivo.
    3. Analise o contexto de outras camadas.
    4. Identifique o fluxo de dados:
       entrada -> validacao -> transformacao -> uso sensivel.
    5. Verifique controles compensatórios:
       - regex
       - allowlist
       - validacao de tipo
       - validacao de faixa
       - wrappers de sanitizacao
       - middleware
       - prepared statements
       - ORM seguro
       - autenticacao/autorizacao
    6. Tente refutar o achado.
    7. Mesmo se a explorabilidade for baixa ou nula, avalie defesa em profundidade.

    Regra especial para SQL Injection:
    não classifique automaticamente como verdadeiro_positivo apenas por concatenação.
    Se houver validação forte, restritiva, observável e consistente, o caso pode ser
    falso_positivo ou inconclusivo.
    Ainda assim, recomende consulta parametrizada como defesa em profundidade quando cabível.

    Regra especial para identificador_regra git.diff.change_review:
    trate o trecho como um diff git. Linhas iniciadas por '+' foram adicionadas e
    linhas iniciadas por '-' foram removidas. Avalie se a mudança introduz uma
    vulnerabilidade, remove um controle de segurança, expõe segredo, enfraquece
    validação/autorização/autenticação, ou aumenta risco operacional. Não trate
    automaticamente a mudança como vulnerável: justifique com evidências do diff
    e do contexto disponível.

    Responda apenas em JSON.

    Dados do achado:
    {dados_achado}
    """).strip()


def montar_prompt_analise_analitico(dados_achado: dict) -> str:
    """
    Prompt analítico experimental.

    Este prompt não deve depender de linhas próximas como conceito principal.
    Ele deve avaliar se há mitigação efetiva, explorabilidade, red flags,
    exposições indevidas e possíveis falsos negativos.
    """

    return dedent(f"""
    Você é um especialista sênior em AppSec, Secure Code Review,
    triagem SAST e inferência contextual de explorabilidade.

    Sua tarefa é complementar o SAST.

    O SAST apontou um achado potencial.
    Você deve avaliar se esse achado permanece explorável considerando evidências
    de mitigação, validação, sanitização, transformação, autorização e uso seguro
    ou inseguro de APIs.

    Além disso, procure evidências complementares que o SAST pode não ter apontado,
    incluindo red flags e exposições indevidas no código.

    Neste modo, contexto não significa linhas acima ou abaixo do achado.
    Contexto significa evidência relevante para decidir se há explorabilidade,
    mitigação efetiva, má prática ou falso positivo.

    Você deve avaliar:

    1. Se o achado SAST é:
       - verdadeiro_positivo
       - falso_positivo
       - mitigado
       - ma_pratica_sem_explorabilidade
       - inconclusivo

    2. Se há indícios de possíveis falsos negativos, como:
       - SQL Injection não reportado
       - Command Injection
       - XSS
       - Path Traversal
       - SSRF
       - uso inseguro de eval/exec
       - autenticação/autorização fraca
       - validação insuficiente
       - uso inseguro de arquivos
       - logs sensíveis
       - exposição de dados sensíveis

    3. Se há exposições indevidas no código, como:
       - tokens
       - secrets
       - senhas
       - chaves de API
       - connection strings
       - certificados privados
       - debug habilitado
       - log.debug com dados sensíveis
       - prints de dados sensíveis
       - md5
       - sha1
       - verify=False
       - comentários com credenciais

    Regras obrigatórias:

    - Não repita mecanicamente o alerta do SAST.
    - Não classifique como verdadeiro positivo apenas porque existe padrão inseguro.
    - Não classifique como falso positivo apenas porque existe uma função chamada validate, sanitize ou escape.
    - Avalie se a mitigação é tecnicamente suficiente contra o vetor analisado.
    - Diferencie vulnerabilidade explorável de má prática de desenvolvimento seguro.
    - Se faltar evidência, classifique como inconclusivo.
    - Se encontrar possível problema não apontado pelo SAST, registre como possível falso negativo.
    - Se encontrar token, secret, senha, chave, debug ou log sensível, registre como exposição.
    - Não invente evidências.
    - Não use resultado de DAST isoladamente como base do veredito. DAST, incluindo OWASP ZAP quando explicitamente autorizado pela política, constitui fonte de evidência dinâmica e deve ser correlacionado com código, hipótese, execução e Security Oracle
    - Procure por Vulnerabilidades que não foram apontadas no SAST 
    - Você pode esta verificando uma aplicaçao propositamente vulneravel nesse caso deve buscar todo tipo de achados
    - Lembrando que os  achados podem ser exploraveis ou não
    - busque por red flag
    Responda apenas em JSON válido.

    Contrato obrigatório:

    {{
      "avaliacao_sast": {{
        "classificacao": "verdadeiro_positivo | falso_positivo | mitigado | ma_pratica_sem_explorabilidade | inconclusivo",
        "exploravel": false,
        "mitigacao_efetiva": false,
        "confianca": 0.0,
        "tipo_vulnerabilidade": "",
        "severidade_reavaliada": "critica | alta | media | baixa | informativa",
        "risco_residual": "",
        "justificativa": "",
        "evidencias_consideradas": [],
        "evidencias_de_mitigacao": [],
        "limitacoes_da_analise": [],
        "decisao_para_pipeline": "bloquear | permitir_com_alerta | permitir | revisar_manualmente"
      }},
      "analise_complementar": {{
        "houve_indicio_de_falso_negativo": false,
        "achados_nao_apontados_pelo_sast": [],
        "red_flags": []
      }},
      "exposicoes_codigo": {{
        "houve_exposicao": false,
        "itens_encontrados": []
      }},
      "organizacao_achado": {{
        "categoria_final": "verdadeiro_positivo | falso_positivo | mitigado | ma_pratica_sem_explorabilidade | inconclusivo | possivel_falso_negativo | red_flag_ou_ma_pratica",
        "prioridade": "critica | alta | media | baixa | informativa",
        "acao_recomendada": "corrigir | aceitar_com_alerta | revisar_manualmente | apenas_documentar",
        "motivo_classificacao": ""
      }},
      "recomendacoes": {{
        "recomendacao_segura": "",
        "recomendacao_linguagem": "",
        "necessita_validacao_manual": false,
        "necessita_validacao_dinamica": false
      }}
    }}

    Dados do achado:
    {dados_achado}
    """).strip()


def montar_prompt_analise(dados_achado: dict) -> str:
    """
    Monta o prompt de análise conforme o tipo definido em configuracoes.TIPO_PROMPT.

    Valores aceitos:
    - contextual
    - analitico

    Se o valor estiver ausente ou inválido, usa contextual para manter compatibilidade.
    """

    tipo_prompt = getattr(configuracoes, "TIPO_PROMPT", "contextual")
    tipo_prompt = str(tipo_prompt).strip().lower()

    if tipo_prompt == "analitico":
        return montar_prompt_analise_analitico(dados_achado)

    return montar_prompt_analise_contextual(dados_achado)


def montar_prompt_correcao(dados_achado: dict) -> str:
    """
    Monta o prompt de correção.

    Este prompt foi preservado para não quebrar a aplicação.
    """

    return dedent(f"""
    Você é um especialista em desenvolvimento seguro.

    Gere uma correção segura e minimalista para o achado.
    Regras:
    - preserve o comportamento legítimo;
    - evite mudanças desnecessárias;
    - prefira correções pequenas e auditáveis;
    - se for SQL, prefira consulta parametrizada;
    - se for validação, use allowlist, tipo e faixa;
    - não remova controles de segurança já existentes.
    - se o achado vier de git.diff.change_review, gere a correção como patch
      incremental sobre a mudança analisada.

    Responda apenas em JSON.

    Dados do achado:
    {dados_achado}
    """).strip()
