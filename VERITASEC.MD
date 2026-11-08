# VeritasSec — Documento Descritivo (Arquitetura Atual + Feature de Análise de Diffs em CSV)

## 1) Proposta do sistema (o “porquê”)

O **VeritasSec** é uma plataforma que recebe achados de ferramentas **SAST/SCA** no formato **SARIF**, enriquece esses achados com **contexto real do código-fonte** e usa múltiplos provedores de LLM para:

- validar o achado (reduzir falsos positivos/negativos),
- classificar (ex.: verdadeiro_positivo, falso_positivo, inconclusivo),
- estimar severidade/risco (incluindo campos como CWE/CVSS quando aplicável),
- justificar tecnicamente a decisão (XAI),
- sugerir uma correção segura,
- persistir e exportar resultados (JSON/CSV/Markdown/métricas/gráficos).

A rota principal já existente implementa esse fluxo end-to-end em [`aplicacao.api.rotas.analisar`](aplicacao/api/rotas.py) usando contratos em [`aplicacao.modelos.contratos`](aplicacao/modelos/contratos.py).

---

## 2) Como o sistema é implementado (o “como”)

### 2.1 Componentes principais

**API (FastAPI)**
- Implementa endpoints e orquestra o pipeline.
- Principal rota: [`aplicacao.api.rotas.analisar`](aplicacao/api/rotas.py).
- Roteador: [`aplicacao.api.rotas.roteador`](aplicacao/api/rotas.py).

**Validação de entrada**
- Valida caminhos e limites de tamanho antes de processar/mandar para LLM.
- Funções centrais:  
  - [`aplicacao.seguranca.validador_entrada.validar_caminho_projeto`](aplicacao/seguranca/validador_entrada.py)  
  - [`aplicacao.seguranca.validador_entrada.validar_caminho_sarif`](aplicacao/seguranca/validador_entrada.py)  
  - [`aplicacao.seguranca.validador_entrada.limitar_tamanho_texto`](aplicacao/seguranca/validador_entrada.py)

**Leitura de SARIF**
- Extrai resultados do SARIF e normaliza em um modelo interno.
- Função central: [`aplicacao.servicos.leitor_sarif.carregar_achados_sarif`](aplicacao/servicos/leitor_sarif.py)  
- Iterator de arquivos: [`aplicacao.servicos.leitor_sarif.iterar_arquivos_sarif`](aplicacao/servicos/leitor_sarif.py)

**Coleta/enriquecimento de contexto**
- Obtém trecho exato, contexto expandido e arquivos relacionados (multicamadas).
- Serviço central: [`aplicacao.servicos.coletor_contexto.enriquecer_achado_com_contexto_multicamadas`](aplicacao/servicos/coletor_contexto.py)  
- Resolução de arquivo: [`aplicacao.servicos.coletor_contexto.resolver_arquivo_fonte`](aplicacao/servicos/coletor_contexto.py)  
- Leitura segura de arquivos: [`aplicacao.utilitarios.arquivos.ler_texto_seguro`](aplicacao/utilitarios/arquivos.py)

**Redação de segredos**
- Redige tokens/credenciais do código/contexto antes do envio aos modelos.
- Função: [`aplicacao.seguranca.redator_segredos.redigir_segredos`](aplicacao/seguranca/redator_segredos.py)

**Provedores de análise (LLMs)**
- Execução (condicional) por OpenAI/Gemini/Local e posterior consolidação.
- Funções:  
  - [`aplicacao.servicos.provedor_openai.analisar_com_openai`](aplicacao/servicos/provedor_openai.py)  
  - [`aplicacao.servicos.provedor_gemini.analisar_com_gemini`](aplicacao/servicos/provedor_gemini.py)  
  - [`aplicacao.servicos.provedor_local.analisar_com_modelo_local`](aplicacao/servicos/provedor_local.py)  
- Consolidação: [`aplicacao.servicos.consolidador.consolidar_avaliacoes`](aplicacao/servicos/consolidador.py)

**Geração de correção**
- Com base na decisão final, sugere correção segura.
- Função: [`aplicacao.servicos.gerador_correcao.gerar_melhor_correcao`](aplicacao/servicos/gerador_correcao.py)

**Persistência**
- Registra execução e achados analisados.
- Funções:  
  - [`aplicacao.servicos.persistencia.persistir_execucao`](aplicacao/servicos/persistencia.py)  
  - [`aplicacao.servicos.persistencia.persistir_achado`](aplicacao/servicos/persistencia.py)

**Exportação de artefatos**
- Exporta relatórios e dados estruturados.
- Funções em [`aplicacao.servicos.exportador_artefatos`](aplicacao/servicos/exportador_artefatos.py):  
  - [`aplicacao.servicos.exportador_artefatos.exportar_json`](aplicacao/servicos/exportador_artefatos.py)  
  - [`aplicacao.servicos.exportador_artefatos.exportar_markdown`](aplicacao/servicos/exportador_artefatos.py)  
  - [`aplicacao.servicos.exportador_artefatos.exportar_csv`](aplicacao/servicos/exportador_artefatos.py)  
  - [`aplicacao.servicos.exportador_artefatos.exportar_metricas`](aplicacao/servicos/exportador_artefatos.py)

**Gráficos**
- Gera visualizações agregadas.
- Funções:  
  - [`aplicacao.servicos.gerador_graficos.gerar_grafico_classificacoes`](aplicacao/servicos/gerador_graficos.py)  
  - [`aplicacao.servicos.gerador_graficos.gerar_grafico_riscos`](aplicacao/servicos/gerador_graficos.py)

---

## 3) Estrutura do projeto (visão prática)

Pontos principais do workspace:

- [`aplicacao/api/rotas.py`](aplicacao/api/rotas.py): orquestra o pipeline e expõe endpoints.
- [`aplicacao/modelos/contratos.py`](aplicacao/modelos/contratos.py): modelos Pydantic (requisição, achado, resposta).
- [`aplicacao/servicos/leitor_sarif.py`](aplicacao/servicos/leitor_sarif.py): leitura e normalização SARIF.
- [`aplicacao/servicos/coletor_contexto.py`](aplicacao/servicos/coletor_contexto.py): enriquecimento de contexto.
- [`aplicacao/servicos/exportador_artefatos.py`](aplicacao/servicos/exportador_artefatos.py): exportação (JSON/CSV/MD/métricas).
- [`saidas/`](saidas/): diretórios de execução com timestamp (ex.: `YYYYMMDD_HHMMSS`).

---

## 4) Como funciona hoje: do `.sarif` até a análise

### 4.1 Entrada e validação
A API recebe uma requisição com (principalmente):
- `raiz_projeto`: diretório do código alvo
- `caminho_sarif`: arquivo `.sarif` (ou diretório contendo `.sarif`)
- parâmetros de contexto e flags de provedores

Contrato: [`aplicacao.modelos.contratos.RequisicaoAnalise`](aplicacao/modelos/contratos.py)

Validação:
- raiz do projeto: [`validar_caminho_projeto`](aplicacao/seguranca/validador_entrada.py)
- caminho do sarif: [`validar_caminho_sarif`](aplicacao/seguranca/validador_entrada.py)

> Observação do estado atual: “no momento, funciona apontando o caminho do `.sarif`”, conforme o fluxo implementado em [`aplicacao.api.rotas.analisar`](aplicacao/api/rotas.py).

### 4.2 Leitura do SARIF
A leitura converte `runs[].results[]` em uma lista de [`aplicacao.modelos.contratos.AchadoSarif`](aplicacao/modelos/contratos.py), extraindo:
- `ruleId`, `level`, `message`
- `artifactLocation.uri` (arquivo)
- `region.startLine/endLine/startColumn/endColumn` (localização)

Implementação: [`carregar_achados_sarif`](aplicacao/servicos/leitor_sarif.py)

### 4.3 Enriquecimento de contexto (multicamadas)
Para cada achado, o sistema:
1. resolve o arquivo real no projeto (quando possível)  
   [`resolver_arquivo_fonte`](aplicacao/servicos/coletor_contexto.py)
2. coleta trecho e contexto expandido (com linhas ao redor)  
   [`enriquecer_achado_com_contexto_multicamadas`](aplicacao/servicos/coletor_contexto.py)
3. redige segredos no texto a ser enviado aos modelos  
   [`redigir_segredos`](aplicacao/seguranca/redator_segredos.py)
4. aplica limite de tamanho  
   [`limitar_tamanho_texto`](aplicacao/seguranca/validador_entrada.py)

### 4.4 Análise por múltiplos modelos + consolidação
A API chama provedores habilitados:
- [`analisar_com_openai`](aplicacao/servicos/provedor_openai.py)
- [`analisar_com_gemini`](aplicacao/servicos/provedor_gemini.py)
- [`analisar_com_modelo_local`](aplicacao/servicos/provedor_local.py)

Depois consolida em uma decisão final:
- [`consolidar_avaliacoes`](aplicacao/servicos/consolidador.py)

### 4.5 Correção e persistência
- correção: [`gerar_melhor_correcao`](aplicacao/servicos/gerador_correcao.py)
- persistência: [`persistir_execucao`](aplicacao/servicos/persistencia.py) e [`persistir_achado`](aplicacao/servicos/persistencia.py)

---

## 5) Como o sistema exibe/exporta resultados

### 5.1 Resposta HTTP estruturada
O endpoint retorna [`aplicacao.modelos.contratos.RespostaAnalise`](aplicacao/modelos/contratos.py), contendo:
- `total` de achados
- lista de [`aplicacao.modelos.contratos.RespostaAchado`](aplicacao/modelos/contratos.py) com:
  - achado enriquecido,
  - avaliações por provedor,
  - decisão final consolidada,
  - correção sugerida (quando aplicável).

### 5.2 Artefatos em disco (`saidas/<timestamp>`)
A rota gera uma pasta de execução e exporta artefatos **de forma resiliente**:
- helper: [`aplicacao.api.rotas.gerar_artefatos_com_resiliencia`](aplicacao/api/rotas.py)
- JSON: [`exportar_json`](aplicacao/servicos/exportador_artefatos.py)
- Markdown: [`exportar_markdown`](aplicacao/servicos/exportador_artefatos.py)
- CSV: [`exportar_csv`](aplicacao/servicos/exportador_artefatos.py)
- métricas: [`exportar_metricas`](aplicacao/servicos/exportador_artefatos.py)
- gráficos: [`gerar_grafico_classificacoes`](aplicacao/servicos/gerador_graficos.py) e [`gerar_grafico_riscos`](aplicacao/servicos/gerador_graficos.py)

---

## 6) Feature a ser implementada: Análise de Vulnerabilidades em Diffs de Git via CSV

### 6.1 Objetivo
Criar uma **nova rota** que faça “a mesma coisa que o sistema já faz”, porém **a entrada não será um `.sarif`** — será um **arquivo `.csv` contendo diffs do git** (ex.: export do GitHub/GitHub Classroom/GitHub Actions), como o dataset [`diffs_semana_SEMANA_2.csv`](diffs_semana_SEMANA_2.csv).

O que importa para a análise é o **diff**: detectar se **entrou** vulnerabilidade (linhas `+`) e/ou se **saiu** algo sensível/importante (linhas `-`), avaliando impacto e risco.

### 6.2 Premissas e restrições
- **Não** é uma ferramenta de *static scan completo* do repo; é um **scanner de mudanças** (change-based security review).
- O diff pode mencionar arquivos/linhas que:
  - não existem no checkout atual (ex.: linhas removidas),
  - foram renomeados,
  - estão fora da raiz real do projeto.
- Ainda assim, o sistema deve produzir **Respostas e Artefatos no mesmo padrão** já estabelecido por [`RespostaAnalise`](aplicacao/modelos/contratos.py) e exportadores em [`exportador_artefatos`](aplicacao/servicos/exportador_artefatos.py).

### 6.3 Contrato proposto da nova rota
**Nova rota (sugestão):**
- `POST /api/analisar-diffs-csv`

**Novo contrato de requisição (sugestão mínima):**
- `raiz_projeto: str` (mantém compatibilidade com contexto multicamadas quando possível)
- `caminho_csv_diffs: str` (arquivo `.csv` com diffs)
- `linhas_contexto: int` (opcional; mesmo papel do SARIF)
- flags de provedores (reaproveitar campos de [`RequisicaoAnalise`](aplicacao/modelos/contratos.py))

**Resposta:**
- Mesma saída de [`RespostaAnalise`](aplicacao/modelos/contratos.py)

> Padrão do projeto: manter a rota como orquestradora, e “empurrar” parsing/normalização para `servicos/` + validação para `seguranca/`.

---

## 7) Como o CSV de diffs será interpretado

### 7.1 Estrutura típica do CSV (exemplo real do workspace)
O arquivo [`diffs_semana_SEMANA_2.csv`](diffs_semana_SEMANA_2.csv) contém colunas como:
- `repositorio`, `branch`, `diffs`

E dentro de `diffs` há texto com:
- blocos de commit (hash, autor, data),
- blocos `diff --git a/... b/...`,
- hunks com `@@ -old,+new @@`,
- linhas removidas (`-`) e adicionadas (`+`),
- separadores e metadados.

### 7.2 Estratégia de extração (normalização para “achados internos”)
Para reaproveitar o pipeline atual (que é achado → contexto → LLM → consolidação → exportação), a feature deve **converter diffs em “unidades analisáveis”**.

**Unidade analisável recomendada (mínimo viável):** “um hunk de diff por arquivo”
- Identificar cada `diff --git a/X b/Y`
- Dentro dele, separar por hunks `@@ ... @@`
- Para cada hunk:
  - montar um “trecho” com:
    - cabeçalho (arquivo/commit),
    - linhas `+` e `-` (com um pouco de contexto do hunk),
  - preencher um objeto semelhante a [`AchadoSarif`](aplicacao/modelos/contratos.py), mesmo que seja um “achado sintético”.

**Mapeamento sugerido para [`AchadoSarif`](aplicacao/modelos/contratos.py):**
- `caminho_arquivo`: usar o caminho `b/<arquivo>` (ou o melhor disponível no diff)
- `linha_inicial`/`linha_final`: quando o hunk tiver `@@`, usar a faixa “new” como aproximação
- `trecho_codigo`: o próprio hunk (com `+/-`)
- `mensagem` e `identificador_regra`: valores sintéticos (ex.: `git.diff.change_review`), pois aqui não existe uma “ruleId” de ferramenta SAST — o “motor” passa a ser o LLM.

Isso permite manter:
- exportação de CSV/Markdown/JSON,
- persistência,
- gráficos,
- o mesmo shape de resposta ao cliente.

---

## 8) Como a análise por LLM deve funcionar com diffs

### 8.1 Contexto “cirúrgico” para diffs (equivalente ao SARIF)
Hoje, o contexto cirúrgico nasce de:
- arquivo + região do SARIF + linhas ao redor.

Para diffs, o contexto cirúrgico deve nascer do próprio **hunk**, contendo:
- **o que entrou** (`+`) e **o que saiu** (`-`),
- nome do arquivo,
- metadados de commit/branch quando disponíveis.

### 8.2 Contexto multicamadas (quando aplicável)
O enriquecimento multicamadas em [`enriquecer_achado_com_contexto_multicamadas`](aplicacao/servicos/coletor_contexto.py) pode ser reaproveitado parcialmente:
- Quando `caminho_arquivo` existir no `raiz_projeto`, coletar contexto do arquivo atual.
- Quando o arquivo **não existir** (ou quando o trecho removido não existe mais), o sistema deve:
  - **não falhar**,
  - continuar com o contexto do diff como fonte primária,
  - anexar a observação “contexto não resolvido no working tree”.

Isso mantém o princípio já aplicado na exportação resiliente em [`gerar_artefatos_com_resiliencia`](aplicacao/api/rotas.py): falhar o mínimo possível e seguir o pipeline.

---

## 9) Como exibir/exportar resultados na feature de diffs

A feature deve **reusar exatamente o mesmo mecanismo** de saída:
- resposta HTTP com [`RespostaAnalise`](aplicacao/modelos/contratos.py)
- artefatos gerados por [`exportador_artefatos`](aplicacao/servicos/exportador_artefatos.py)
- diretório `saidas/<timestamp>` (mesma organização aplicada em [`aplicacao.api.rotas.analisar`](aplicacao/api/rotas.py))

**Interpretação na exportação (sem mudar formato):**
- Cada “achado” corresponderá a um hunk analisado.
- O CSV exportado por [`exportar_csv`](aplicacao/servicos/exportador_artefatos.py) continuará útil, pois a coluna `caminho_arquivo`, linhas e `identificador_regra` (sintético) ainda classificam o item.
- O Markdown de [`exportar_markdown`](aplicacao/servicos/exportador_artefatos.py) será o relatório humano para revisão de PR.

---

## 10) Mudanças mínimas necessárias (sem implementar agora)

A seguir está o **mínimo de alterações estruturais** para a feature ser viável e seguir os padrões atuais (API orquestra; `servicos` processam; `seguranca` valida; contratos em `modelos`).

### 10.1 Novas peças (mínimas)
1) **Validador de caminho do CSV**
- Arquivo: [`aplicacao/seguranca/validador_entrada.py`](aplicacao/seguranca/validador_entrada.py)
- Nova função (análogo a `validar_caminho_sarif`): `validar_caminho_csv_diffs(caminho: str) -> Path`

2) **Serviço de leitura/parsing de CSV + diffs**
- Novo arquivo sugerido: `aplicacao/servicos/leitor_diffs_csv.py`
- Responsabilidade: ler o CSV, extrair texto de diff e produzir “achados sintéticos” compatíveis com [`AchadoSarif`](aplicacao/modelos/contratos.py)

3) **Nova rota**
- Arquivo: [`aplicacao/api/rotas.py`](aplicacao/api/rotas.py)
- Endpoint novo: `POST /api/analisar-diffs-csv`
- Orquestra:
  - valida raiz + csv,
  - chama `leitor_diffs_csv` para obter lista de “achados”,
  - reusa o restante do pipeline (contexto → provedores → consolidação → correção → persistência → exportação).

4) **(Opcional, mas recomendado) Contrato novo de requisição**
- Arquivo: [`aplicacao/modelos/contratos.py`](aplicacao/modelos/contratos.py)
- Ex.: `RequisicaoAnaliseDiffsCsv` para não “forçar” `caminho_sarif`.
- Alternativa mínima: reaproveitar [`RequisicaoAnalise`](aplicacao/modelos/contratos.py) e adicionar campo opcional `caminho_csv_diffs`, mas isso pode confundir validação (padrão mais limpo é um contrato separado).

### 10.2 “Código mínimo” (apenas assinaturas/skeleton) — para guiar a implementação futura
> Observação: isto **não é a implementação**, apenas o contorno mínimo para manter consistência do projeto.

**A) Novo validador (assinatura)**
```python
# filepath: aplicacao/seguranca/validador_entrada.py
# ...existing code...

from pathlib import Path

def validar_caminho_csv_diffs(caminho: str) -> Path:
    """
    Valida um arquivo CSV de diffs (export GitHub).
    Deve existir e ter sufixo .csv.
    """
    # implementação futura
    raise NotImplementedError
```

**B) Novo leitor/normalizador (assinaturas)**
```python
# filepath: aplicacao/servicos/leitor_diffs_csv.py
from typing import List
from aplicacao.modelos.contratos import AchadoSarif

def carregar_achados_de_diffs_csv(caminho_csv: str, maximo_achados: int | None = None) -> List[AchadoSarif]:
    """
    Lê o CSV e converte diffs em 'achados sintéticos' (um por hunk/arquivo).
    """
    # implementação futura
    raise NotImplementedError
```

**C) Nova rota (assinatura)**
```python
# filepath: aplicacao/api/rotas.py
# ...existing code...

@roteador.post("/analisar-diffs-csv", response_model=RespostaAnalise)
def analisar_diffs_csv(req: "RequisicaoAnaliseDiffsCsv") -> RespostaAnalise:
    """
    Mesma lógica de /api/analisar, porém com entrada via CSV contendo diffs do git.
    """
    # implementação futura
    raise NotImplementedError
```

---

## 11) Critérios de sucesso (feature de diffs)

1) A rota aceita um `.csv` no formato do dataset [`diffs_semana_SEMANA_2.csv`](diffs_semana_SEMANA_2.csv).
2) O sistema analisa **mudanças** (linhas `+`/`-`) e decide:
   - se uma vulnerabilidade foi introduzida,
   - se algo importante foi removido (ex.: validação, sanitização, autenticação),
   - qual a severidade/risco e a recomendação.
3) A resposta e artefatos seguem os padrões atuais:
   - retorna [`RespostaAnalise`](aplicacao/modelos/contratos.py),
   - exporta via [`exportador_artefatos`](aplicacao/servicos/exportador_artefatos.py),
   - gera pasta `saidas/<timestamp>` como já feito em [`aplicacao.api.rotas.analisar`](aplicacao/api/rotas.py).
   - é importante não criar arquivos e códigos desnecessários.
4) A feature não quebra o fluxo atual baseado em SARIF.

---

## 12) Observações finais (design choices)
- A escolha por “achados sintéticos” mantém o pipeline e os exportadores intactos (menor impacto).
- O risco principal é a resolução de contexto no working tree para linhas removidas; a feature deve ser tolerante e priorizar o diff.
- O padrão de resiliência já existe em [`gerar_artefatos_com_resiliencia`](aplicacao/api/rotas.py); a nova rota deve seguir a mesma filosofia.