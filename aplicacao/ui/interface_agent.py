def _vs_historico_pagina_interface_1() -> str:
    return r"""<!doctype html>
<html lang="pt-BR">

<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">

<title>VeritasSec-Agent </title>

<style>
:root{
    --fundo:#f4f6f8;
    --painel:#ffffff;
    --linha:#d7dde5;
    --texto:#18212b;
    --muted:#66727e;
    --azul:#174ea6;
    --escuro:#17202a;
    --vermelho:#b42318;
}

*{
    box-sizing:border-box;
}

body{
    margin:0;
    background:var(--fundo);
    color:var(--texto);
    font-family:Arial,Helvetica,sans-serif;
}

header{
    padding:20px 30px;
    background:var(--escuro);
    color:#fff;
}

header h1{
    margin:0;
    font-size:25px;
}

header p{
    margin:6px 0 0;
    color:#ccd5dd;
}

main{
    max-width:1180px;
    margin:24px auto;
    padding:0 18px;
}

.tabs{
    display:flex;
    gap:5px;
    border-bottom:1px solid var(--linha);
    margin-bottom:16px;
}

.tab{
    border:1px solid var(--linha);
    border-bottom:0;
    padding:11px 17px;
    background:#e7ebf0;
    color:var(--texto);
    border-radius:6px 6px 0 0;
    cursor:pointer;
}

.tab.active{
    background:#fff;
    color:var(--azul);
    font-weight:bold;
}

.panel{
    display:none;
    background:var(--painel);
    border:1px solid var(--linha);
    border-radius:7px;
    padding:22px;
}

.panel.active{
    display:block;
}

.grid{
    display:grid;
    grid-template-columns:1fr 1fr;
    gap:15px;
}

.full{
    grid-column:1/-1;
}

label{
    display:block;
    margin-bottom:6px;
    font-size:13px;
    font-weight:bold;
}

input,
select{
    width:100%;
    padding:10px;
    border:1px solid #bcc5cf;
    border-radius:5px;
    background:#fff;
}

.actions{
    margin-top:18px;
}

.action{
    margin:3px 5px 3px 0;
    padding:10px 14px;
    border:0;
    border-radius:5px;
    background:var(--azul);
    color:#fff;
    cursor:pointer;
}

.secondary{
    background:#59636e;
}

.danger{
    background:var(--vermelho);
}

.status{
    margin-top:15px;
    padding:12px;
    border:1px solid var(--linha);
    border-radius:5px;
    background:#f8fafc;
    white-space:pre-wrap;
}

pre{
    padding:15px;
    border-radius:6px;
    background:#101820;
    color:#dbe5ee;
    overflow:auto;
    max-height:500px;
}

table{
    width:100%;
    border-collapse:collapse;
    margin-top:15px;
}

th,
td{
    padding:9px;
    border-bottom:1px solid var(--linha);
    text-align:left;
    font-size:13px;
}

.small{
    font-size:12px;
    color:var(--muted);
}

@media(max-width:760px){
    .grid{
        grid-template-columns:1fr;
    }
}
</style>

<style>
/* VS_AGENT_M22C */

#vsAgentOperationalResults {
    margin-top: 18px;
}

.vs-summary {
    display: grid;
    grid-template-columns:
        repeat(auto-fit, minmax(140px,1fr));
    gap: 10px;
    margin-bottom: 16px;
}

.vs-summary > div,
.vs-finding,
.vs-agent-card,
.vs-plan-box,
.vs-policy-row,
.vs-evidence-row {
    border:
        1px solid
        rgba(127,127,127,.25);
    border-radius: 8px;
}

.vs-summary > div {
    padding: 11px;
}

.vs-summary strong,
.vs-summary span {
    display: block;
}

.vs-finding {
    padding: 14px;
    margin: 14px 0;
}

.vs-finding-header {
    display: flex;
    justify-content: space-between;
    gap: 12px;
    align-items: center;
}

.vs-verdict {
    font-weight: 700;
}

.vs-location {
    margin-top: 7px;
    opacity: .72;
    word-break: break-all;
}

.vs-agent-grid {
    display: grid;
    grid-template-columns:
        repeat(auto-fit,minmax(250px,1fr));
    gap: 9px;
    margin-top: 9px;
}

.vs-agent-card,
.vs-plan-box,
.vs-policy-row,
.vs-evidence-row {
    padding: 10px;
    margin-top: 8px;
}

.vs-agent-title {
    font-weight: 700;
    margin-bottom: 6px;
}

.vs-policy-row {
    display: grid;
    grid-template-columns:
        minmax(100px,1fr)
        minmax(130px,1fr)
        auto
        minmax(160px,2fr);
    gap: 8px;
    align-items: center;
}

.vs-plan-grid {
    display: grid;
    grid-template-columns:
        repeat(auto-fit,minmax(240px,1fr));
    gap: 10px;
}

.vs-budget {
    display: flex;
    flex-wrap: wrap;
    gap: 14px;
    margin: 9px 0;
}

.vs-ok {
    font-weight: 700;
}

.vs-denied {
    font-weight: 700;
    opacity: .70;
}

.vs-empty {
    opacity: .65;
    padding: 8px 0;
}

.vs-finding details {
    margin-top: 11px;
}

.vs-finding summary {
    cursor: pointer;
    font-weight: 600;
}

.vs-finding pre {
    white-space: pre-wrap;
    overflow-wrap: anywhere;
    overflow: auto;
    max-height: 420px;
}
</style>


<style id="vsBaseSeletoresStyle">

.vs-base-seletor {

    display:grid;

    grid-template-columns:
        minmax(0, 1fr)
        170px;

    gap:
        8px;

    align-items:center;

    width:100%;
}


.vs-base-seletor > div {

    min-width:0;
}


.vs-base-seletor input,
.vs-base-seletor select {

    width:100%;

    box-sizing:border-box;
}


.vs-base-botao-seletor {

    display:block !important;

    visibility:visible !important;

    opacity:1 !important;

    position:static !important;

    width:170px !important;

    min-width:170px !important;

    height:32px;

    margin:0 !important;

    padding:0 12px;

    border:
        1px solid
        #8996a3;

    border-radius:
        4px;

    background:
        #eef1f4;

    color:
        #17212b;

    cursor:pointer;

    white-space:nowrap;
}


.vs-base-botao-seletor:hover {

    background:
        #dfe6ed;

    border-color:
        #174ea6;
}


/*
 * Botões experimentais anteriores deixam de interessar.
 */
#vsSelecionarDiretorioFinal,
#vsSelecionarSarifFinal,
#btnSelecionarProjeto,
#btnSelecionarSarif {

    display:none !important;
}


@media(max-width:850px) {

    .vs-base-seletor {

        grid-template-columns:
            1fr;
    }


    .vs-base-botao-seletor {

        width:100% !important;

        min-width:0 !important;
    }
}

</style>

</head>

<body>

<header>
<h1>VeritasSec-Agent </h1>
<p>Analise contextual e validacao de achados de seguranca</p>
</header>

<main>

<div class="tabs">
<button class="tab active" data-tab="config">Configuracao</button>
<button class="tab" data-tab="analise">Analise</button>
<button class="tab" data-tab="resultados">Resultados</button>
<button class="tab" data-tab="agent">VeritasSec-Agent</button>
</div>

<section id="config" class="panel active">

<h2>Configuracao</h2>

<div class="grid">

<div>
<label>Provedor</label>
<select id="provedor" onchange="atualizarModelos()">
<option value="openai">OpenAI</option>
<option value="gemini">Gemini</option>
<option value="ollama">Ollama</option>
</select>
</div>

<div>
<label>Modelo</label>
<select id="modelo"></select>
</div>

<div class="full">
<label>API Key</label>
<input
    id="apiKey"
    type="password"
    autocomplete="off"
    placeholder="A chave nao sera exibida">
</div>

<div>
<label>Timeout</label>
<input id="timeout" type="number" value="120">
</div>

<div>
<label>Maximo de tokens</label>
<input id="tokens" type="number" value="2500">
</div>

<div>
<label>Temperatura</label>
<input
    id="temperatura"
    type="number"
    min="0"
    max="2"
    step="0.1"
    value="0.1">
</div>

</div>

<div class="actions">
<button class="action" onclick="salvarConfig()">
Salvar configuracao
</button>

<button class="action" onclick="salvarKey()">
Carregar API key
</button>

<button class="action danger" onclick="removerKey()">
Limpar API key
</button>

<button class="action secondary" onclick="testarConexao()">
Testar conexao
</button>
</div>

<div id="statusConfig" class="status"></div>

</section>

<section id="analise" class="panel">

<h2>Analise</h2>

<div class="grid">

<div>
<!-- VERITASSEC_BOTOES_BASE_DEFINITIVOS_20261019 -->
<label>Diretório do projeto</label>

<div class="vs-base-seletor">

    <select id="projeto"></select>

    <button
        id="vsBaseSelecionarDiretorio"
        type="button"
        class="vs-base-botao-seletor"
    >
        Selecionar Projeto
    </button>

</div>
</div>

<div>
<label>Arquivo SARIF</label>

<div class="vs-base-seletor">

    <select id="sarif"></select>

    <button
        id="vsBaseSelecionarSarif"
        type="button"
        class="vs-base-botao-seletor"
    >
        Selecionar SARIF
    </button>

</div>
</div>

<div>
<label>Diretorio de saida</label>
<input id="saida" value="interface">
</div>

</div>

<div class="actions">

<button class="action secondary" onclick="carregarInputs()">
Atualizar entradas
</button>

<button id="btnExecutarAnalise" class="action" type="button">
Executar analise
</button>

</div>

<div id="statusAnalise" class="status"></div>

<h3>Resultado</h3>

<pre id="resultado">{}</pre>

</section>

<section id="resultados" class="panel">

<h2>Resultados</h2>

<div class="actions">
<button class="action" onclick="carregarOutputs()">
Atualizar resultados
</button>
</div>

<div id="statusOutputs" class="status"></div>

<table>
<thead>
<tr>
<th>Arquivo</th>
<th>Tamanho</th>
<th>Acao</th>
</tr>
</thead>

<tbody id="arquivos"></tbody>
</table>

</section>

<section id="agent" class="panel">

<h2>VeritasSec-Agent</h2>

<p class="small">
Estado operacional e capacidades do sistema.
</p>

<button class="action" onclick="carregarAgent()">
Atualizar estado
</button>

<pre id="estadoAgent">{}</pre>

</section>

</main>

<script>
const $ = id => document.getElementById(id);

document.querySelectorAll("[data-tab]").forEach(b => {
    b.addEventListener("click", () => {

        document
            .querySelectorAll("[data-tab]")
            .forEach(x => x.classList.remove("active"));

        document
            .querySelectorAll(".panel")
            .forEach(x => x.classList.remove("active"));

        b.classList.add("active");
        $(b.dataset.tab).classList.add("active");
    });
});

async function api(url, opt = {}) {

    const r = await fetch(url, opt);
    const txt = await r.text();

    let data;

    try {
        data = JSON.parse(txt);
    } catch {
        data = txt;
    }

    if (!r.ok) {
        throw new Error(
            typeof data === "string"
                ? data
                : JSON.stringify(data)
        );
    }

    return data;
}

function jsonBody(data) {
    return {
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    };
}


let MODELOS_DISPONIVEIS = {};


function atualizarModelos(
    modeloPreferido = null
) {

    const provedor =
        $("provedor").value;

    const modelos =
        MODELOS_DISPONIVEIS[
            provedor
        ] || [];

    const select =
        $("modelo");

    const anterior =
        modeloPreferido
        || select.value;

    select.innerHTML = "";

    for (
        const modelo
        of modelos
    ) {

        const option =
            document.createElement(
                "option"
            );

        option.value =
            modelo;

        option.textContent =
            modelo;

        select.appendChild(
            option
        );
    }

    if (
        anterior
        && modelos.includes(
            anterior
        )
    ) {
        select.value =
            anterior;
    }

    const local =
        provedor === "ollama";

    $("apiKey").disabled =
        local;

    if (local) {

        $("apiKey").value = "";

        $("apiKey").placeholder =
            "Ollama local nao utiliza API key";

    } else {

        $("apiKey").placeholder =
            "A chave nao sera exibida";
    }
}


async function carregarConfig() {

    try {

        const c = await api("/api/interface/config");

        MODELOS_DISPONIVEIS =
            c.modelos_disponiveis || {};

        $("provedor").value =
            c.provedor;

        atualizarModelos(
            c.modelo
        );
$("timeout").value = c.timeout;
        $("tokens").value = c.max_tokens;
        $("temperatura").value = c.temperatura;

        $("statusConfig").textContent =
            "API key configurada: " +
            (c.api_key_configurada ? "SIM" : "NAO");

    } catch (e) {
        $("statusConfig").textContent = e.message;
    }
}

async function salvarConfig() {

    try {

        const d = await api(
            "/api/interface/config",
            {
                method: "PUT",
                ...jsonBody({
                    provedor: $("provedor").value,
                    modelo: $("modelo").value,
timeout: Number($("timeout").value),
                    max_tokens: Number($("tokens").value),
                    temperatura: Number($("temperatura").value)
                })
            }
        );

        $("statusConfig").textContent =
            "Configuracao salva.\n" +
            JSON.stringify(d, null, 2);

    } catch (e) {
        $("statusConfig").textContent = e.message;
    }
}

async function salvarKey() {

    if (
        $("provedor").value
        === "ollama"
    ) {

        $("statusConfig").textContent =
            "Ollama local nao utiliza API key.";

        return;
    }

    try {

        const key = $("apiKey").value;

        if (!key) {
            throw new Error("Informe a API key.");
        }

        await api(
            "/api/interface/api-key",
            {
                method: "POST",
                ...jsonBody({
                    provedor: $("provedor").value,
                    api_key: key
                })
            }
        );

        $("apiKey").value = "";

        await carregarConfig();

    } catch (e) {
        $("statusConfig").textContent = e.message;
    }
}

async function removerKey() {

    try {

        await api(
            "/api/interface/api-key/" +
            encodeURIComponent($("provedor").value),
            {
                method: "DELETE"
            }
        );

        $("apiKey").value = "";

        await carregarConfig();

    } catch (e) {
        $("statusConfig").textContent = e.message;
    }
}

async function testarConexao() {

    try {

        const d = await api(
            "/api/interface/test-connection",
            {
                method: "POST"
            }
        );

        $("statusConfig").textContent =
            JSON.stringify(d, null, 2);

    } catch (e) {
        $("statusConfig").textContent = e.message;
    }
}

async function carregarInputs() {

    try {

        const d = await api("/api/interface/inputs");

        $("projeto").innerHTML = "";
        $("sarif").innerHTML = "";

        for (const p of d.projetos) {

            const o = document.createElement("option");

            o.value = p.caminho;
            o.textContent = p.nome;

            $("projeto").appendChild(o);
        }

        for (const s of d.sarifs) {

            const o = document.createElement("option");

            o.value = s.caminho;
            o.textContent = s.nome;

            $("sarif").appendChild(o);
        }

        $("statusAnalise").textContent =
            "Projetos: " +
            d.projetos.length +
            " | SARIF: " +
            d.sarifs.length;

    } catch (e) {
        $("statusAnalise").textContent = e.message;
    }
}

async function executarAnalise() {

    try {

        if (!$("#projeto").value) {
            throw new Error(
                "Nenhum projeto disponivel."
            );
        }

        if (!$("#sarif").value) {
            throw new Error(
                "Nenhum SARIF disponivel."
            );
        }

        $("#statusAnalise").textContent =
            "Iniciando analise...";

        $("#resultado").textContent =
            "{}";

        const inicioJob =
            await api(
                "/api/interface/analisar",
                {
                    method: "POST",
                    ...jsonBody({
                        projeto:
                            $("#projeto").value,

                        sarif:
                            $("#sarif").value,

                        subdiretorio_saida:
                            $("#saida").value,

                        assincrono: true
                    })
                }
            );

        if (!inicioJob.job_id) {
            throw new Error(
                "Backend nao retornou job_id."
            );
        }

        const jobId =
            inicioJob.job_id;

        const inicioMs =
            Date.now();

        while (true) {

            await new Promise(
                resolve =>
                    setTimeout(
                        resolve,
                        1500
                    )
            );

            const job =
                await api(
                    "/api/interface/analisar/status/"
                    + encodeURIComponent(
                        jobId
                    )
                );

            const segundos =
                Math.floor(
                    (
                        Date.now()
                        - inicioMs
                    )
                    / 1000
                );

            if (
                job.status
                === "CONCLUIDA"
            ) {

                const resultado =
                    job.resultado;

                $("#resultado").textContent =
                    JSON.stringify(
                        resultado,
                        null,
                        2
                    );

                $("#statusAnalise").textContent =
                    "Analise concluida. "
                    + "Tempo total: "
                    + segundos
                    + " s.";

                renderizarResumoAnalise(
                    resultado
                );

                break;
            }

            if (
                job.status
                === "FALHA"
            ) {

                throw new Error(
                    job.erro
                    || "Falha na analise."
                );
            }

            $("#statusAnalise").textContent =
                "Executando analise... "
                + segundos
                + " s | estado="
                + job.status;
        }

    } catch (e) {

        $("#statusAnalise").textContent =
            "Falha: "
            + e.message;
    }
}


function renderizarResumoAnalise(
    dados
) {

    try {

        const resultados =
            Array.isArray(
                dados
                && dados.resultados
            )
            ? dados.resultados
            : [];

        const total =
            dados
            && dados.total_processado
            !== undefined
            ? dados.total_processado
            : resultados.length;

        const trace =
            document.getElementById(
                "agent-trace"
            );

        if (trace) {

            trace.innerHTML = "";

            const resumo =
                document.createElement(
                    "div"
                );

            resumo.style.padding =
                "10px";

            resumo.style.border =
                "1px solid #ddd";

            resumo.textContent =
                "Achados processados: "
                + total
                + " | agentes por achado: 7";

            trace.appendChild(
                resumo
            );
        }

    } catch (_) {

        // Renderização auxiliar não interfere
        // no resultado científico.
    }
}


async function carregarOutputs() {

    try {

        const d = await api(
            "/api/interface/outputs?diretorio=" +
            encodeURIComponent($("saida").value)
        );

        $("arquivos").innerHTML = "";

        for (const a of d.arquivos) {

            const tr =
                document.createElement("tr");

            const nome =
                document.createElement("td");

            const tamanho =
                document.createElement("td");

            const acao =
                document.createElement("td");

            nome.textContent = a.nome;
            tamanho.textContent =
                a.tamanho_bytes;

            const link =
                document.createElement("a");

            link.textContent = "Baixar";

            link.href =
                "/api/interface/download/" +
                a.caminho
                    .split("/")
                    .map(encodeURIComponent)
                    .join("/");

            acao.appendChild(link);

            tr.append(
                nome,
                tamanho,
                acao
            );

            $("arquivos").appendChild(tr);
        }

        $("statusOutputs").textContent =
            "Arquivos: " +
            d.arquivos.length;

    } catch (e) {
        $("statusOutputs").textContent =
            e.message;
    }
}

async function carregarAgent() {

    try {

        const cap =
            await api("/api/v1/multiagente/capacidades");

        $("estadoAgent").textContent =
            JSON.stringify(
                {
                    capabilities: cap
                },
                null,
                2
            );

    } catch (e) {
        $("estadoAgent").textContent =
            e.message;
    }
}

carregarConfig();
carregarInputs();
carregarAgent();
</script>


<section id="agent-trace-panel"
         style="margin-top:24px;">
  <h2>Investigação Multiagente</h2>

  <div id="agent-summary">
    <p>
      Pipeline: VeritasSec-Agent —
      7 agentes especializados.
    </p>
  </div>

  <div id="agent-trace"></div>
</section>

<script>
(function () {
  const originalFetch = window.fetch;

  window.fetch = async function (...args) {
    const response = await originalFetch.apply(
      this,
      args
    );

    try {
      const requestUrl = String(args[0]);

      if (
        requestUrl.includes(
          "/api/interface/analisar"
        )
      ) {
        const clone = response.clone();
        const data = await clone.json();

        if (
          data &&
          data.resultado &&
          Array.isArray(
            data.resultado.trilha
          )
        ) {
          const container =
            document.getElementById(
              "agent-trace"
            );

          if (container) {
            container.innerHTML = "";

            data.resultado.trilha.forEach(
              function (passo, index) {
                const bloco =
                  document.createElement(
                    "div"
                  );

                bloco.style.margin =
                  "10px 0";

                bloco.style.padding =
                  "10px";

                bloco.style.border =
                  "1px solid #ddd";

                const agente =
                  passo.agente || "?";

                const decisao =
                  passo.decisao || "";

                const estado =
                  passo.estado || "";

                bloco.textContent =
                  (index + 1) +
                  ". " +
                  agente +
                  " — " +
                  estado +
                  " — " +
                  decisao;

                container.appendChild(
                  bloco
                );
              }
            );

            const final =
              document.createElement(
                "div"
              );

            final.style.marginTop =
              "16px";

            final.style.fontWeight =
              "bold";

            final.textContent =
              "Estado final: " +
              (
                data.resultado
                  .estado_final ||
                "INDEFINIDO"
              ) +
              " | Motivo: " +
              (
                data.resultado
                  .motivo_termino ||
                "N/A"
              );

            container.appendChild(final);
          }
        }
      }
    } catch (_) {
      // A renderização adicional nunca altera
      // o resultado da análise.
    }

    return response;
  };
})();
</script>


<section id="llm-proof-panel"
         style="margin-top:18px;">
  <h2>Execução Cognitiva</h2>

  <div id="llm-proof-status">
    Aguardando análise.
  </div>

  <div id="llm-proof-agents"></div>
</section>

<script>
(function () {
  const previousFetchM16 = window.fetch;

  window.fetch = async function (...args) {
    const response =
      await previousFetchM16.apply(
        this,
        args
      );

    try {
      const url = String(args[0]);

      if (
        url.includes(
          "/api/interface/analisar"
        )
      ) {
        const clone = response.clone();
        const data = await clone.json();

        const raciocinio =
          data &&
          data.resultado &&
          data.resultado.raciocinio;

        if (raciocinio) {
          const status =
            document.getElementById(
              "llm-proof-status"
            );

          const agents =
            document.getElementById(
              "llm-proof-agents"
            );

          if (status) {
            status.textContent =
              "Modo: " +
              raciocinio.modo +
              " | chamadas LLM reais: " +
              raciocinio.chamadas_llm_reais +
              "/7 | fallbacks: " +
              raciocinio.fallbacks_deterministicos +
              "/7";
          }

          if (
            agents &&
            Array.isArray(
              raciocinio.agentes
            )
          ) {
            agents.innerHTML = "";

            raciocinio.agentes.forEach(
              function (item) {
                const div =
                  document.createElement(
                    "div"
                  );

                div.style.margin =
                  "8px 0";

                div.style.padding =
                  "8px";

                div.style.border =
                  "1px solid #ddd";

                const decisao =
                  item.decisao || {};

                div.textContent =
                  item.agente +
                  " | " +
                  item.modo +
                  " | modelo=" +
                  (
                    item.modelo ||
                    "N/A"
                  ) +
                  " | confiança=" +
                  (
                    decisao.confianca ??
                    "N/A"
                  );

                agents.appendChild(
                  div
                );
              }
            );
          }
        }
      }
    } catch (_) {
      // UI auxiliar não altera a análise.
    }

    return response;
  };
})();
</script>


<div
    id="vsAgentOperationalResults"
></div>

<script>
/* VS_AGENT_M22C_RENDERER */

function vsEscape(v) {
    if (v === null || v === undefined) {
        return "";
    }

    return String(v)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

function vsJson(v) {
    try {
        return JSON.stringify(
            v ?? {},
            null,
            2
        );
    } catch (_) {
        return String(v ?? "");
    }
}

function vsArray(v) {
    return Array.isArray(v)
        ? v
        : [];
}

function vsEstado(resultado) {
    const v =
        resultado?.estado_final ??
        resultado?.veredito?.estado ??
        resultado?.veredito ??
        resultado?.decisao_final ??
        resultado?.status ??
        "INCONCLUSIVO";

    if (typeof v === "object") {
        return (
            v?.estado ??
            v?.status ??
            v?.classificacao ??
            "INCONCLUSIVO"
        );
    }

    return v;
}

function vsAgentes(resultado) {
    const trilha =
        vsArray(resultado?.trilha);

    if (!trilha.length) {
        return `
            <div class="vs-empty">
                Trilha multiagente não disponível.
            </div>
        `;
    }

    return `
        <div class="vs-agent-grid">
            ${
                trilha.map(
                    (evento, indice) => {
                        const agente =
                            evento?.agente ??
                            evento?.papel ??
                            (
                                "agente-"
                                + (indice + 1)
                            );

                        const conteudo =
                            evento?.decisao ??
                            evento?.resultado ??
                            evento?.raciocinio ??
                            evento;

                        return `
                            <div class="vs-agent-card">
                                <div class="vs-agent-title">
                                    ${vsEscape(agente)}
                                </div>
                                <pre>${vsEscape(
                                    vsJson(conteudo)
                                )}</pre>
                            </div>
                        `;
                    }
                ).join("")
            }
        </div>
    `;
}

function vsPlano(resultado) {
    const plano =
        resultado
            ?.plano_aquisicao_evidencia
        ?? {};

    const hipoteses =
        vsArray(plano?.hipoteses);

    const lacunas =
        vsArray(plano?.lacunas);

    return `
        <div class="vs-plan-grid">

            <div class="vs-plan-box">
                <strong>
                    Hipóteses
                </strong>

                ${
                    hipoteses.length
                    ? `
                        <ul>
                            ${
                                hipoteses.map(
                                    x =>
                                        `<li>${vsEscape(x)}</li>`
                                ).join("")
                            }
                        </ul>
                    `
                    : `
                        <div class="vs-empty">
                            Nenhuma hipótese registrada.
                        </div>
                    `
                }
            </div>

            <div class="vs-plan-box">
                <strong>
                    Lacunas de evidência
                </strong>

                ${
                    lacunas.length
                    ? `
                        <ul>
                            ${
                                lacunas.map(
                                    x =>
                                        `<li>${vsEscape(x)}</li>`
                                ).join("")
                            }
                        </ul>
                    `
                    : `
                        <div class="vs-empty">
                            Nenhuma lacuna registrada.
                        </div>
                    `
                }
            </div>

        </div>

        ${
            plano?.estrategia
            ? `
                <div class="vs-plan-box">
                    <strong>
                        Estratégia
                    </strong>
                    <pre>${vsEscape(
                        plano.estrategia
                    )}</pre>
                </div>
            `
            : ""
        }
    `;
}

function vsPolitica(resultado) {
    const plano =
        resultado
            ?.plano_aquisicao_evidencia
        ?? {};

    const decisoes =
        vsArray(
            plano?.decisoes_politica
        );

    if (!decisoes.length) {
        return `
            <div class="vs-empty">
                Nenhuma decisão de capacidade registrada.
            </div>
        `;
    }

    return decisoes.map(
        d => `
            <div class="vs-policy-row">
                <span>
                    ${vsEscape(
                        d?.agente ?? ""
                    )}
                </span>

                <strong>
                    ${vsEscape(
                        d?.capacidade ?? ""
                    )}
                </strong>

                <span class="${
                    d?.autorizada
                    ? "vs-ok"
                    : "vs-denied"
                }">
                    ${
                        d?.autorizada
                        ? "AUTORIZADA"
                        : "NEGADA"
                    }
                </span>

                <span>
                    ${vsEscape(
                        d?.motivo ?? ""
                    )}
                </span>
            </div>
        `
    ).join("");
}

function vsAquisicao(resultado) {
    const aq =
        resultado
            ?.aquisicao_evidencia
        ?? {};

    const orc =
        aq?.orcamento ?? {};

    const itens =
        vsArray(aq?.resultados);

    return `
        <div class="vs-budget">

            <span>
                Critério de parada:
                <strong>
                    ${vsEscape(
                        aq?.criterio_parada ??
                        "N/D"
                    )}
                </strong>
            </span>

            <span>
                Ações:
                <strong>
                    ${vsEscape(
                        orc?.acoes_executadas ?? 0
                    )}
                    /
                    ${vsEscape(
                        orc?.max_acoes ?? 0
                    )}
                </strong>
            </span>

            <span>
                Negadas:
                <strong>
                    ${vsEscape(
                        orc?.acoes_negadas ?? 0
                    )}
                </strong>
            </span>

            <span>
                Erros:
                <strong>
                    ${vsEscape(
                        orc?.erros ?? 0
                    )}
                </strong>
            </span>

        </div>

        ${
            itens.length
            ? itens.map(
                item => `
                    <div class="vs-evidence-row">

                        <strong>
                            ${vsEscape(
                                item?.capacidade ?? ""
                            )}
                        </strong>

                        <span class="${
                            item?.executada
                            ? "vs-ok"
                            : "vs-denied"
                        }">
                            ${
                                item?.executada
                                ? "EXECUTADA"
                                : "NÃO EXECUTADA"
                            }
                        </span>

                        <div>
                            ${vsEscape(
                                item?.motivo ?? ""
                            )}
                        </div>

                        ${
                            item?.sementes?.length
                            ? `
                                <div>
                                    Seeds:
                                    <code>
                                        ${vsEscape(
                                            item.sementes.join(
                                                " | "
                                            )
                                        )}
                                    </code>
                                </div>
                            `
                            : ""
                        }

                        ${
                            item?.resultado !== null &&
                            item?.resultado !== undefined
                            ? `
                                <pre>${vsEscape(
                                    vsJson(
                                        item.resultado
                                    )
                                )}</pre>
                            `
                            : ""
                        }

                    </div>
                `
            ).join("")
            : `
                <div class="vs-empty">
                    Nenhuma aquisição adicional executada.
                </div>
            `
        }
    `;
}

function vsFinding(
    item,
    indice,
    total
) {
    const achado =
        item?.achado ?? {};

    const resultado =
        item?.resultado ?? {};

    const regra =
        achado?.regra ??
        achado?.rule_id ??
        achado?.id ??
        (
            "Achado "
            + (indice + 1)
        );

    const arquivo =
        achado?.arquivo ??
        achado?.file ??
        "";

    const linha =
        achado?.linha ??
        achado?.line ??
        "";

    return `
        <section class="vs-finding">

            <div class="vs-finding-header">

                <div>
                    <span>
                        ${indice + 1}/${total}
                    </span>

                    <strong>
                        ${vsEscape(regra)}
                    </strong>
                </div>

                <span class="vs-verdict">
                    ${vsEscape(
                        vsEstado(resultado)
                    )}
                </span>

            </div>

            <div class="vs-location">
                ${vsEscape(arquivo)}
                ${
                    linha
                    ? ":" + vsEscape(linha)
                    : ""
                }
            </div>

            <details open>
                <summary>
                    Sete agentes
                </summary>
                ${vsAgentes(resultado)}
            </details>

            <details open>
                <summary>
                    Plano de aquisição de evidência
                </summary>
                ${vsPlano(resultado)}
            </details>

            <details open>
                <summary>
                    Política de capacidades
                </summary>
                ${vsPolitica(resultado)}
            </details>

            <details open>
                <summary>
                    Execução e evidências
                </summary>
                ${vsAquisicao(resultado)}
            </details>

            <details>
                <summary>
                    Resultado técnico completo
                </summary>

                <pre>${vsEscape(
                    vsJson(resultado)
                )}</pre>
            </details>

        </section>
    `;
}

function renderizarResultadoAgent(
    data
) {
    const root =
        document.getElementById(
            "vsAgentOperationalResults"
        );

    if (!root) {
        return;
    }

    let itens = [];

    if (
        (data?.processamento ?? data?.modo)
            === "multiachado"
        &&
        Array.isArray(
            data?.resultados
        )
    ) {
        itens = data.resultados;

    } else if (
        data?.resultado
    ) {
        itens = [{
            achado:
                data?.achado ?? {},
            resultado:
                data.resultado,
        }];
    }

    const total =
        itens.length;

    root.innerHTML = `
        <div class="vs-summary">

            <div>
                <strong>
                    ${vsEscape(
                        data?.total_achados_sarif
                        ?? total
                    )}
                </strong>
                <span>
                    achados SARIF
                </span>
            </div>

            <div>
                <strong>
                    ${vsEscape(
                        data?.total_processado
                        ?? total
                    )}
                </strong>
                <span>
                    processados
                </span>
            </div>

            <div>
                <strong>7</strong>
                <span>
                    papéis multiagente
                </span>
            </div>

            <div>
                <strong>
                    ${vsEscape(
                        data?.processamento
                        ?? "individual"
                    )}
                </strong>
                <span>
                    processamento
                </span>
            </div>

        </div>

        ${
            total
            ? itens.map(
                (item, indice) =>
                    vsFinding(
                        item,
                        indice,
                        total
                    )
            ).join("")
            : `
                <div class="vs-empty">
                    Nenhum resultado operacional retornado.
                </div>
            `
        }
    `;
}

/*
 * Observador da rota operacional.
 * A Response original não é consumida:
 * somente response.clone() é lido.
 */
(function instalarObservadorAgent() {

    if (
        window.__vsAgentFetchObserver
    ) {
        return;
    }

    window.__vsAgentFetchObserver =
        true;

    const fetchOriginal =
        window.fetch.bind(window);

    window.fetch =
        async function(
            input,
            init
        ) {
            const response =
                await fetchOriginal(
                    input,
                    init
                );

            try {
                const url =
                    typeof input === "string"
                    ? input
                    : (
                        input?.url ?? ""
                    );

                if (
                    url.includes(
                        "/api/interface/analisar"
                    )
                ) {
                    const clone =
                        response.clone();

                    clone.json()
                        .then(
                            data =>
                                renderizarResultadoAgent(
                                    data
                                )
                        )
                        .catch(
                            () => {}
                        );
                }

            } catch (_) {
                /*
                 * O painel jamais interrompe
                 * a análise principal.
                 */
            }

            return response;
        };
})();
</script>


<!-- VERITASSEC_ANALISE_CONTROLLER_V2 -->
<script>
(function () {
    "use strict";

    function elemento(id) {
        return document.getElementById(id);
    }

    function definirStatus(texto) {
        const el =
            elemento("statusAnalise");

        if (el) {
            el.textContent =
                texto;
        }
    }

    function definirResultado(dados) {
        const el =
            elemento("resultado");

        if (el) {
            el.textContent =
                JSON.stringify(
                    dados,
                    null,
                    2
                );
        }
    }

    async function chamarApi(
        url,
        opcoes = {}
    ) {
        const resposta =
            await fetch(
                url,
                opcoes
            );

        const texto =
            await resposta.text();

        let dados;

        try {
            dados =
                texto
                ? JSON.parse(texto)
                : {};
        } catch (_) {
            dados = texto;
        }

        if (!resposta.ok) {
            throw new Error(
                typeof dados === "string"
                    ? dados
                    : JSON.stringify(
                        dados
                    )
            );
        }

        return dados;
    }

    function corpoJson(dados) {
        return {
            headers: {
                "Content-Type":
                    "application/json"
            },
            body:
                JSON.stringify(
                    dados
                )
        };
    }

    async function executarAnaliseV2() {
        /* VERITASSEC_INTERFACE_ARTEFATOS_COMPLETOS_20261019 */

        const botao =
            elemento(
                "btnExecutarAnalise"
            );

        try {

            const projeto =
                elemento("projeto");

            const sarif =
                elemento("sarif");

            const saida =
                elemento("saida");

            if (
                !projeto
                || !projeto.value
            ) {
                throw new Error(
                    "Nenhum projeto selecionado."
                );
            }

            if (
                !sarif
                || !sarif.value
            ) {
                throw new Error(
                    "Nenhum arquivo SARIF selecionado."
                );
            }

            if (botao) {
                botao.disabled =
                    true;

                botao.textContent =
                    "Executando...";
            }

            definirResultado({});

            definirStatus(
                "Iniciando analise..."
            );

            // ---------------------------------------------
            // POST curto: apenas cria o job.
            // ---------------------------------------------

            const inicio =
                await chamarApi(
                    "/api/interface/analisar",
                    {
                        method: "POST",

                        ...corpoJson({
                            projeto:
                                projeto.value,

                            sarif:
                                sarif.value,

                            subdiretorio_saida:
                                (
                                    saida
                                    && saida.value
                                )
                                || "interface",

                            assincrono:
                                true
                        })
                    }
                );

            if (!inicio.job_id) {
                throw new Error(
                    "Backend nao retornou job_id."
                );
            }

            const jobId =
                inicio.job_id;

            const inicioTempo =
                Date.now();

            definirStatus(
                "Analise iniciada | job="
                + jobId
            );

            // ---------------------------------------------
            // Polling.
            // ---------------------------------------------

            while (true) {

                await new Promise(
                    resolve =>
                        setTimeout(
                            resolve,
                            1500
                        )
                );

                const job =
                    await chamarApi(
                        "/api/interface/analisar/status/"
                        + encodeURIComponent(
                            jobId
                        )
                    );

                const segundos =
                    Math.floor(
                        (
                            Date.now()
                            - inicioTempo
                        )
                        / 1000
                    );

                if (
                    job.status
                    === "CONCLUIDA"
                ) {

                    definirResultado(
                        job.resultado
                    );

                    definirStatus(
                        "Analise concluida"
                        + " | tempo="
                        + segundos
                        + " s"
                    );

                    // Compatibilidade com renderizador
                    // instalado anteriormente.
                    if (
                        typeof window
                            .renderizarResumoAnalise
                        === "function"
                    ) {
                        window
                            .renderizarResumoAnalise(
                                job.resultado
                            );
                    }

                    return;
                }

                if (
                    job.status
                    === "FALHA"
                ) {

                    throw new Error(
                        job.erro
                        || (
                            "Falha durante "
                            + "a analise."
                        )
                    );
                }

                definirStatus(
                    "Executando analise..."
                    + " "
                    + segundos
                    + " s"
                    + " | estado="
                    + job.status
                );
            }

        } catch (erro) {

            console.error(
                "VeritasSec executarAnalise:",
                erro
            );

            definirStatus(
                "Falha: "
                + (
                    erro
                    && erro.message
                    ? erro.message
                    : String(erro)
                )
            );

        } finally {

            if (botao) {
                botao.disabled =
                    false;

                botao.textContent =
                    "Executar analise";
            }
        }
    }

    // -----------------------------------------------------
    // Expõe função global apenas para compatibilidade.
    // -----------------------------------------------------

    window.executarAnalise =
        executarAnaliseV2;

    // -----------------------------------------------------
    // Listener explícito.
    // -----------------------------------------------------

    function instalar() {

        const botao =
            elemento(
                "btnExecutarAnalise"
            );

        if (!botao) {
            console.error(
                "Botao de analise nao encontrado."
            );
            return;
        }

        if (
            botao.dataset
                .veritassecBound
            === "1"
        ) {
            return;
        }

        botao.dataset
            .veritassecBound =
            "1";

        botao.addEventListener(
            "click",
            function (evento) {

                evento
                    .preventDefault();

                executarAnaliseV2();
            }
        );

        console.info(
            "VeritasSec: botao de analise conectado."
        );
    }

    if (
        document.readyState
        === "loading"
    ) {

        document.addEventListener(
            "DOMContentLoaded",
            instalar,
            {
                once: true
            }
        );

    } else {

        instalar();
    }

})();
</script>
<!-- /VERITASSEC_ANALISE_CONTROLLER_V2 -->


<!-- VERITASSEC_CONTADORES_REAIS_V1 -->
<script>
(function () {
    "use strict";

    function localizarOuCriarResumo() {
        let el =
            document.getElementById(
                "veritassecResumoExecucao"
            );

        if (el) {
            return el;
        }

        const resultado =
            document.getElementById(
                "resultado"
            );

        if (!resultado) {
            return null;
        }

        el =
            document.createElement(
                "div"
            );

        el.id =
            "veritassecResumoExecucao";

        el.style.marginTop =
            "12px";

        el.style.padding =
            "12px";

        el.style.border =
            "1px solid #d0d7de";

        el.style.borderRadius =
            "6px";

        el.style.whiteSpace =
            "pre-line";

        resultado.parentNode.insertBefore(
            el,
            resultado
        );

        return el;
    }

    window.renderizarContadoresReais =
        function (dados) {

            if (!dados) {
                return;
            }

            const totalSarif =
                Number(
                    dados.total_achados_sarif
                    ?? 0
                );

            const selecionados =
                Number(
                    dados.total_selecionado
                    ?? totalSarif
                );

            const processados =
                Number(
                    dados.total_processado
                    ?? 0
                );

            let agentesPorAchado = 0;

            if (
                Array.isArray(
                    dados.resultados
                )
                && dados.resultados.length
            ) {

                const primeiro =
                    dados.resultados[0];

                const resultado =
                    primeiro
                    && primeiro.resultado;

                if (
                    resultado
                    && Array.isArray(
                        resultado.agentes_executados
                    )
                ) {
                    agentesPorAchado =
                        resultado
                            .agentes_executados
                            .length;
                }
            }

            const el =
                localizarOuCriarResumo();

            if (!el) {
                return;
            }

            el.textContent =
                "Achados no SARIF: "
                + totalSarif
                + "\n"
                + "Achados selecionados: "
                + selecionados
                + "\n"
                + "Achados processados: "
                + processados
                + "\n"
                + "Agentes por achado: "
                + agentesPorAchado;
        };

    // --------------------------------------------------------
    // Integrar ao renderizador já existente.
    // --------------------------------------------------------

    const anterior =
        window.renderizarResumoAnalise;

    window.renderizarResumoAnalise =
        function (dados) {

            if (
                typeof anterior
                === "function"
            ) {
                anterior(dados);
            }

            window
                .renderizarContadoresReais(
                    dados
                );
        };
})();
</script>
<!-- /VERITASSEC_CONTADORES_REAIS_V1 -->

</body>

</html>"""

pagina_interface = _vs_historico_pagina_interface_1


# ============================================================
# VERITASSEC_PASSO3_INTERFACE_OPERACIONAL
# ============================================================

_pagina_interface_base_passo3 = pagina_interface


def _vs_historico_pagina_interface_2() -> str:

    html = _pagina_interface_base_passo3()

    if "veritassec-passo3-root" in html:
        return html

    bloco = r"""
<style id="veritassec-passo3-css">

#veritassec-passo3-root{
    margin-top:24px;
}

.vs3-card{
    background:#fff;
    border:1px solid #d6dbe1;
    border-radius:10px;
    padding:18px;
    margin-bottom:18px;
}

.vs3-grid{
    display:grid;
    grid-template-columns:
        repeat(auto-fit,minmax(190px,1fr));
    gap:12px;
}

.vs3-field label{
    display:block;
    font-weight:600;
    margin-bottom:6px;
}

.vs3-field input{
    width:100%;
    box-sizing:border-box;
    padding:9px 10px;
    border:1px solid #b9c1cb;
    border-radius:6px;
}

.vs3-actions{
    display:flex;
    flex-wrap:wrap;
    gap:8px;
    margin-top:14px;
}

.vs3-actions button{
    padding:9px 16px;
    border-radius:6px;
    border:1px solid #aab3bd;
    cursor:pointer;
}

.vs3-status-grid{
    display:grid;
    grid-template-columns:
        repeat(auto-fit,minmax(150px,1fr));
    gap:10px;
    margin-top:16px;
}

.vs3-kpi{
    border:1px solid #dce1e6;
    border-radius:8px;
    padding:10px;
}

.vs3-progress{
    height:18px;
    border-radius:9px;
    overflow:hidden;
    background:#e6e9ed;
    margin-top:14px;
}

.vs3-progress > div{
    height:100%;
    width:0%;
    background:#66717e;
}

.vs3-tabs{
    display:flex;
    flex-wrap:wrap;
    gap:6px;
    margin-bottom:12px;
}

.vs3-tab{
    padding:8px 14px;
    cursor:pointer;
}

.vs3-tab.ativo{
    font-weight:700;
}

.vs3-pane{
    display:none;
}

.vs3-pane.ativo{
    display:block;
}

.vs3-code{
    background:#111820;
    color:#e8edf2;
    padding:12px;
    border-radius:8px;
    overflow:auto;
    max-height:520px;
}

.vs3-table{
    width:100%;
    border-collapse:collapse;
}

.vs3-table th,
.vs3-table td{
    border-bottom:1px solid #e0e4e8;
    padding:8px;
    text-align:left;
}

.vs3-charts{
    display:grid;
    grid-template-columns:
        repeat(auto-fit,minmax(280px,1fr));
    gap:16px;
}

.vs3-chart{
    border:1px solid #dce1e6;
    border-radius:8px;
    padding:12px;
}

.vs3-badge{
    display:inline-block;
    border:1px solid #c8ced5;
    border-radius:999px;
    padding:3px 8px;
    margin:2px;
}

</style>


<section
    id="veritassec-passo3-root"
    class="vs3-card"
>

<h2>Operação da análise</h2>

<div class="vs3-grid">

<div class="vs3-field">
<label for="vs3Projeto">
Diretório do projeto
</label>
<input id="vs3Projeto" type="text">
</div>

<div class="vs3-field">
<label for="vs3Sarif">
Arquivo SARIF
</label>
<input id="vs3Sarif" type="text">
</div>

</div>

<div class="vs3-actions">

<button id="vs3Executar">
Executar
</button>

<button id="vs3Pausar" disabled>
Pausar
</button>

<button id="vs3Retomar" disabled>
Retomar
</button>

<button id="vs3Parar" disabled>
Parar
</button>

</div>

<div id="vs3Mensagem">
PRONTO
</div>

<div class="vs3-progress">
<div id="vs3Barra"></div>
</div>

<div class="vs3-status-grid">

<div class="vs3-kpi">
<strong>Estado</strong>
<div id="vs3Estado">PRONTO</div>
</div>

<div class="vs3-kpi">
<strong>Progresso</strong>
<div id="vs3Progresso">0 / 0</div>
</div>

<div class="vs3-kpi">
<strong>Achado atual</strong>
<div id="vs3Achado">—</div>
</div>

<div class="vs3-kpi">
<strong>Agente atual</strong>
<div id="vs3Agente">—</div>
</div>

<div class="vs3-kpi">
<strong>Provedor atual</strong>
<div id="vs3Provedor">—</div>
</div>

<div class="vs3-kpi">
<strong>Etapa atual</strong>
<div id="vs3Etapa">—</div>
</div>

</div>

</section>


<section class="vs3-card">

<div class="vs3-tabs">

<button
    class="vs3-tab ativo"
    data-vs3-tab="analise"
>
Análise
</button>

<button
    class="vs3-tab"
    data-vs3-tab="resultados"
>
Resultados
</button>

<button
    class="vs3-tab"
    data-vs3-tab="evidencias"
>
Evidências
</button>

<button
    class="vs3-tab"
    data-vs3-tab="graficos"
>
Gráficos
</button>

</div>


<div
    id="vs3-pane-analise"
    class="vs3-pane ativo"
>

<h3>Pipeline cognitivo</h3>

<span class="vs3-badge">
Orquestrador
</span>

<span class="vs3-badge">
Analista de Código
</span>

<span class="vs3-badge">
Superfície de Ataque
</span>

<span class="vs3-badge">
Hipóteses
</span>

<span class="vs3-badge">
Planejador
</span>

<span class="vs3-badge">
Validação
</span>

<span class="vs3-badge">
Crítico Adversarial
</span>

<h4>Provedores</h4>

<span class="vs3-badge">Local</span>
<span class="vs3-badge">GPT</span>
<span class="vs3-badge">Gemini</span>

<h4>Validação dinâmica</h4>

<span class="vs3-badge">
OWASP ZAP
</span>

<span class="vs3-badge">
Security Oracle
</span>

<pre
    id="vs3EstadoBruto"
    class="vs3-code"
>{}</pre>

</div>


<div
    id="vs3-pane-resultados"
    class="vs3-pane"
>

<table class="vs3-table">

<thead>
<tr>
<th>#</th>
<th>ID</th>
<th>Regra</th>
<th>CWE</th>
<th>Arquivo</th>
<th>Veredito</th>
</tr>
</thead>

<tbody id="vs3TabelaResultados">
</tbody>

</table>

</div>


<div
    id="vs3-pane-evidencias"
    class="vs3-pane"
>

<pre
    id="vs3Evidencias"
    class="vs3-code"
>Nenhuma evidência carregada.</pre>

</div>


<div
    id="vs3-pane-graficos"
    class="vs3-pane"
>

<div class="vs3-charts">

<div class="vs3-chart">
<canvas
    id="vs3GraficoVereditos"
    width="500"
    height="250"
></canvas>
</div>

<div class="vs3-chart">
<canvas
    id="vs3GraficoSeveridade"
    width="500"
    height="250"
></canvas>
</div>

<div class="vs3-chart">
<canvas
    id="vs3GraficoCwe"
    width="500"
    height="250"
></canvas>
</div>

<div class="vs3-chart">
<canvas
    id="vs3GraficoRegras"
    width="500"
    height="250"
></canvas>
</div>

<div class="vs3-chart">
<canvas
    id="vs3GraficoEvidencias"
    width="500"
    height="250"
></canvas>
</div>

<div class="vs3-chart">
<canvas
    id="vs3GraficoProvedores"
    width="500"
    height="250"
></canvas>
</div>

</div>

</div>

</section>


<script id="veritassec-passo3-js">
(function(){

"use strict";

let jobId = null;
let polling = null;
let resultadosAtuais = [];


function el(id){
    return document.getElementById(id);
}


async function request(url, options){

    const r = await fetch(
        url,
        options || {}
    );

    let d = {};

    try{
        d = await r.json();
    }catch(_){}

    if(!r.ok){
        throw new Error(
            d.detail
            || (
                "HTTP "
                + r.status
            )
        );
    }

    return d;
}


function setControles(estado){

    // CORRECAO_VERITASSEC_EXECUTAR_20261020
    // PRONTO permite iniciar uma nova analise.
    // Somente a execucao ativa ou pausada bloqueia
    // uma nova solicitacao.
    el("vs3Executar").disabled =
        [
            "EXECUTANDO",
            "PAUSADO"
        ].includes(estado);

    el("vs3Pausar").disabled =
        estado !== "EXECUTANDO";

    el("vs3Retomar").disabled =
        estado !== "PAUSADO";

    el("vs3Parar").disabled =
        ![
            "PRONTO",
            "EXECUTANDO",
            "PAUSADO"
        ].includes(estado);
}


function atualizar(job){

    const p =
        job.progresso
        || {};

    const processados =
        Number(
            p.processados
            ?? job.total_processado
            ?? 0
        );

    const total =
        Number(
            p.total
            ?? job.total_selecionado
            ?? 0
        );

    const percentual =
        Number(
            p.percentual
            ?? (
                total
                ? processados * 100 / total
                : 0
            )
        );

    el("vs3Estado").textContent =
        job.estado || "—";

    el("vs3Progresso").textContent =
        processados
        + " / "
        + total
        + " ("
        + percentual.toFixed(1)
        + "%)";

    el("vs3Barra").style.width =
        Math.max(
            0,
            Math.min(
                100,
                percentual
            )
        )
        + "%";

    el("vs3Achado").textContent =
        job.achado_atual || "—";

    el("vs3Agente").textContent =
        job.agente_atual || "—";

    el("vs3Provedor").textContent =
        job.provedor_atual || "—";

    el("vs3Etapa").textContent =
        job.etapa_atual || "—";

    el("vs3EstadoBruto").textContent =
        JSON.stringify(
            job,
            null,
            2
        );

    setControles(
        job.estado
    );
}


function veredito(r){

    return (
        r
        ?.fundamentacao_tecnica
        ?.veredito

        ?? r?.veredito_final

        ?? r?.estado_final

        ?? "INCONCLUSIVO"
    );
}


function renderResultados(){

    const tbody =
        el(
            "vs3TabelaResultados"
        );

    tbody.innerHTML = "";

    resultadosAtuais.forEach(
        (
            pacote,
            indice
        ) => {

            const achado =
                pacote.achado
                || {};

            const resultado =
                pacote.resultado
                || {};

            const tr =
                document.createElement(
                    "tr"
                );

            [
                indice + 1,
                achado.id || "—",
                achado.regra
                    || achado.ruleId
                    || "—",
                achado.cwe || "—",
                achado.arquivo || "—",
                veredito(resultado)
            ].forEach(
                valor => {

                    const td =
                        document.createElement(
                            "td"
                        );

                    td.textContent =
                        String(valor);

                    tr.appendChild(
                        td
                    );
                }
            );

            tbody.appendChild(
                tr
            );
        }
    );
}


function renderEvidencias(){

    el(
        "vs3Evidencias"
    ).textContent =
        JSON.stringify(
            resultadosAtuais,
            null,
            2
        );
}


function contar(lista, extrator){

    const m = {};

    lista.forEach(
        item => {

            const valor =
                String(
                    extrator(item)
                    ?? "N/A"
                );

            m[valor] =
                (
                    m[valor]
                    || 0
                )
                + 1;
        }
    );

    return m;
}


function barras(canvas, mapa){

    const ctx =
        canvas.getContext(
            "2d"
        );

    const itens =
        Object.entries(
            mapa
        )
        .sort(
            (a,b) => b[1] - a[1]
        )
        .slice(
            0,
            10
        );

    ctx.clearRect(
        0,
        0,
        canvas.width,
        canvas.height
    );

    if(!itens.length){
        ctx.fillText(
            "Sem dados",
            20,
            30
        );
        return;
    }

    const maximo =
        Math.max(
            ...itens.map(
                x => x[1]
            ),
            1
        );

    itens.forEach(
        (
            [nome, quantidade],
            indice
        ) => {

            const y =
                15
                + indice * 23;

            const largura =
                300
                * quantidade
                / maximo;

            ctx.fillRect(
                150,
                y,
                largura,
                16
            );

            ctx.fillText(
                nome.slice(0,20),
                5,
                y + 12
            );

            ctx.fillText(
                String(quantidade),
                155 + largura,
                y + 12
            );
        }
    );
}



// VERITASSEC_GRAFICOS_SETORIAIS_20261020
function setores(canvas, mapa, rosca){
    const ctx = canvas.getContext("2d");

    const itens = Object.entries(mapa)
        .filter(([nome, valor]) =>
            Number.isFinite(Number(valor))
            && Number(valor) > 0
        )
        .sort((a,b) => b[1] - a[1]);

    ctx.clearRect(
        0,0,canvas.width,canvas.height
    );

    if(!itens.length){
        ctx.fillStyle = "#526276";
        ctx.fillText("Sem dados",20,30);
        return;
    }

    const total = itens.reduce(
        (s, item) => s + Number(item[1]),0
    );

    const cx = 145;
    const cy = canvas.height / 2;
    const raio = Math.min(95,canvas.height * 0.38);

    const cores = [
        "#2563eb",
        "#0f766e",
        "#d97706",
        "#7c3aed",
        "#dc2626",
        "#64748b",
        "#0891b2",
        "#84cc16"
    ];

    let angulo = -Math.PI/2;

    itens.forEach(([nome, valor], indice)=>{
        const fracao = Number(valor)/total;
        const fim = angulo + fracao*2*Math.PI;

        ctx.beginPath();
        ctx.moveTo(cx,cy);
        ctx.arc(cx,cy,raio,angulo,fim);
        ctx.closePath();
        ctx.fillStyle = cores[indice%cores.length];
        ctx.fill();

        angulo = fim;
    });

    if(rosca){
        ctx.beginPath();
        ctx.arc(cx,cy,raio*0.53,0,2*Math.PI);
        ctx.fillStyle = "#ffffff";
        ctx.fill();

        ctx.fillStyle = "#17212e";
        ctx.font = "bold 18px sans-serif";
        ctx.textAlign = "center";
        ctx.fillText(String(total),cx,cy+6);
        ctx.textAlign = "start";
    }

    ctx.font = "12px sans-serif";

    itens.slice(0,8).forEach(
        ([nome,valor],indice)=>{
            const x = 265;
            const y = 22 + indice*26;

            ctx.fillStyle = cores[indice%cores.length];
            ctx.fillRect(x,y-9,11,11);

            ctx.fillStyle = "#17212e";

            const percentual = (
                Number(valor)/total*100
            ).toFixed(1);

            ctx.fillText(
                String(nome).slice(0,18)
                + " (" + percentual + "%)",
                x+17,
                y
            );
        }
    );
}

function renderGraficos(){

    setores(
        el("vs3GraficoVereditos"),
        contar(
            resultadosAtuais,
            x => veredito(
                x.resultado || {}
            )
        ),
        true
    );

    setores(
        el("vs3GraficoSeveridade"),
        contar(
            resultadosAtuais,
            x => (
                x.achado?.severidade
                ?? x.achado?.nivel
                ?? "N/A"
            )
        ),
        false
    );

    barras(
        el("vs3GraficoCwe"),
        contar(
            resultadosAtuais,
            x => x.achado?.cwe
        )
    );

    barras(
        el("vs3GraficoRegras"),
        contar(
            resultadosAtuais,
            x => (
                x.achado?.regra
                ?? x.achado?.ruleId
            )
        )
    );

    const evid = {
        "Estática":0,
        "Dinâmica":0,
        "Oracle":0,
        "ZAP":0
    };

    resultadosAtuais.forEach(
        x => {

            const r =
                x.resultado
                || {};

            if(r.scr){
                evid["Estática"]++;
            }

            if(r.evidencia_dinamica){
                evid["Dinâmica"]++;
            }

            if(r.evidencia_oraculo){
                evid["Oracle"]++;
            }

            const bruto =
                JSON.stringify(r);

            if(
                bruto.includes(
                    "OWASP_ZAP"
                )
                || bruto.includes(
                    "EVIDENCIA_DAST_ZAP"
                )
            ){
                evid["ZAP"]++;
            }
        }
    );

    barras(
        el("vs3GraficoEvidencias"),
        evid
    );

    const provedores = {
        "Local":0,
        "GPT":0,
        "Gemini":0
    };

    resultadosAtuais.forEach(
        x => {

            const bruto =
                JSON.stringify(
                    x.resultado || {}
                )
                .toLowerCase();

            if(bruto.includes('"local"')){
                provedores.Local++;
            }

            if(bruto.includes('"gpt"')){
                provedores.GPT++;
            }

            if(bruto.includes('"gemini"')){
                provedores.Gemini++;
            }
        }
    );

    barras(
        el("vs3GraficoProvedores"),
        provedores
    );
}


async function carregarResultados(){

    if(!jobId){
        return;
    }

    const d = await request(
        "/api/interface/execucao/"
        + encodeURIComponent(jobId)
        + "/resultados"
    );

    resultadosAtuais =
        Array.isArray(
            d.resultados
        )
        ? d.resultados
        : [];

    renderResultados();
    renderEvidencias();
    renderGraficos();
}


async function consultar(){

    if(!jobId){
        return;
    }

    // VERITASSEC_STATUS_404_20261022
    const resposta = await fetch(
        "/api/interface/analisar/status/"
        + encodeURIComponent(jobId),
        {cache:"no-store"}
    );

    if(resposta.status === 404){
        clearInterval(polling);
        polling = null;
        jobId = null;
        window.veritasSecJobId = null;

        el("vs3Estado").textContent =
            "EXECUCAO_INDISPONIVEL";

        el("vs3Agente").textContent = "—";
        el("vs3Provedor").textContent = "—";
        el("vs3Etapa").textContent =
            "Execução anterior não encontrada";

        setControles("ERRO");
        return;
    }

    if(!resposta.ok){
        throw new Error(
            "Falha ao consultar execução: HTTP "
            + resposta.status
        );
    }

    const job = await resposta.json();

    atualizar(job);

    await carregarResultados();

    if([
        "CONCLUIDO",
        "INTERROMPIDO",
        "ERRO"
    ].includes(job.estado)){

        clearInterval(
            polling
        );

        polling = null;
    }
}


async function executar(){

    const projeto =
        el(
            "vs3Projeto"
        ).value.trim();

    const sarif =
        el(
            "vs3Sarif"
        ).value.trim();

    if(!projeto || !sarif){
        el("vs3Mensagem").textContent =
            "Informe projeto e SARIF.";
        return;
    }

    // Bloqueio imediato durante o envio.
    setControles("EXECUTANDO");

    try{

        const criado = await request(
            "/api/interface/analisar",
            {
                method:"POST",
                headers:{
                    "Content-Type":
                        "application/json"
                },
                body:JSON.stringify({
                    // Execucao controlavel com acompanhamento.
                    operacional: true,
                    projeto_path:projeto,
                    sarif_path:sarif
                })
            }
        );

        jobId =
            criado.job_id;

        window.veritasSecJobId =
            jobId;

        atualizar(
            criado
        );

        polling =
            setInterval(
                consultar,
                750
            );

        await consultar();

    }catch(erro){

        setControles("PRONTO");

        el("vs3Mensagem").textContent =
            "Erro: "
            + erro.message;
    }
}


async function controlar(acao){

    if(!jobId){
        return;
    }

    try{

        const estado = await request(
            "/api/interface/execucao/"
            + encodeURIComponent(jobId)
            + "/"
            + acao,
            {
                method:"POST"
            }
        );

        atualizar(
            estado
        );

    }catch(erro){

        el("vs3Mensagem").textContent =
            "Erro: "
            + erro.message;
    }
}


function selecionarTab(nome){

    document
        .querySelectorAll(
            ".vs3-tab"
        )
        .forEach(
            b => b.classList.toggle(
                "ativo",
                b.dataset.vs3Tab
                    === nome
            )
        );

    document
        .querySelectorAll(
            ".vs3-pane"
        )
        .forEach(
            p => p.classList.toggle(
                "ativo",
                p.id
                    === "vs3-pane-" + nome
            )
        );

    if(nome === "graficos"){
        renderGraficos();
    }
}


function sincronizar(){

    const projeto =
        document.getElementById(
            "projeto"
        );

    const sarif =
        document.getElementById(
            "sarif"
        );

    if(projeto?.value){
        el("vs3Projeto").value =
            projeto.value;
    }

    if(sarif?.value){
        el("vs3Sarif").value =
            sarif.value;
    }
}


function iniciar(){

    sincronizar();

    el("vs3Executar")
        .addEventListener(
            "click",
            executar
        );

    el("vs3Pausar")
        .addEventListener(
            "click",
            () => controlar(
                "pausar"
            )
        );

    el("vs3Retomar")
        .addEventListener(
            "click",
            () => controlar(
                "retomar"
            )
        );

    el("vs3Parar")
        .addEventListener(
            "click",
            () => controlar(
                "parar"
            )
        );

    document
        .querySelectorAll(
            ".vs3-tab"
        )
        .forEach(
            b => b.addEventListener(
                "click",
                () => selecionarTab(
                    b.dataset.vs3Tab
                )
            )
        );

    setControles(
        "PRONTO"
    );
}


if(
    document.readyState
    === "loading"
){
    document.addEventListener(
        "DOMContentLoaded",
        iniciar
    );
}else{
    iniciar();
}

})();
</script>
"""

    if "</body>" in html:
        return html.replace(
            "</body>",
            bloco + "\n</body>",
            1,
        )

    return html + bloco

pagina_interface = _vs_historico_pagina_interface_2


# ============================================================
# VERITASSEC_PASSO4_136_UI_EXPORTACAO
# ============================================================

_pagina_interface_base_passo4_136 = pagina_interface


def _vs_historico_pagina_interface_3() -> str:

    html = _pagina_interface_base_passo4_136()

    if 'id="vs4ExportarFinal"' in html:
        return html

    bloco = r"""
<section class="vs3-card">
<h2>Exportação</h2>
<p>DOCX, CSV, gráficos e hashes da execução concluída.</p>

<!-- VERITASSEC_EXPORTACAO_SELETIVA -->
<div id="vs4Formatos" class="vs3-actions"
     style="gap:16px;flex-wrap:wrap;margin:16px 0">

<label>
<input type="checkbox" id="vs4SelecionarTodos">
Selecionar todos
</label>

<label>
<input type="checkbox" id="vs4FormatoDocx">
DOCX
</label>

<label>
<input type="checkbox" id="vs4FormatoCsv">
CSV
</label>

</div>

<div class="vs3-actions">
<button
    id="vs4ExportarFinal"
    type="button"
>
Exportar resultados
</button>
</div>

<div id="vs4Status">
Aguardando execução concluída.
</div>

<pre
    id="vs4Manifesto"
    class="vs3-code"
>{}</pre>
</section>

<script id="veritassec-passo4-136-js">
(function(){
"use strict";

async function exportar(){
    const status =
        document.getElementById(
            "vs4Status"
        );

    const manifesto =
        document.getElementById(
            "vs4Manifesto"
        );

    const jobId =
        window.veritasSecJobId;

    if(!jobId){
        status.textContent =
            "Nenhuma execução selecionada.";
        return;
    }

    const docx = document.getElementById(
        "vs4FormatoDocx"
    );

    const csv = document.getElementById(
        "vs4FormatoCsv"
    );

    const formatos = [];

    if (docx?.checked) formatos.push("DOCX");
    if (csv?.checked) formatos.push("CSV");

    if (!formatos.length) {
        status.textContent =
            "Selecione DOCX, CSV ou ambos.";
        return;
    }

    status.textContent =
        "Gerando artefatos...";

    try{
        const resposta =
            await fetch(
                "/api/interface/execucao/"
                + encodeURIComponent(jobId)
                + "/exportar",
                {
                    method:"POST",
                    headers:{
                        "Content-Type":"application/json"
                    },
                    body:JSON.stringify({formatos:formatos})
                }
            );

        const dados =
            await resposta.json();

        if(!resposta.ok){
            throw new Error(
                dados?.detail
                || ("HTTP " + resposta.status)
            );
        }

        status.textContent =
            "Artefatos gerados em: "
            + dados.diretorio;

        manifesto.textContent =
            JSON.stringify(
                dados.manifesto,
                null,
                2
            );

    }catch(erro){
        status.textContent =
            "Erro: " + erro.message;
    }
}

function iniciar(){
    const botao =
        document.getElementById(
            "vs4ExportarFinal"
        );

    if(botao){
        botao.addEventListener(
            "click",
            exportar
        );
    }

    const todos =
        document.getElementById("vs4SelecionarTodos");

    const docx =
        document.getElementById("vs4FormatoDocx");

    const csv =
        document.getElementById("vs4FormatoCsv");

    if (todos && docx && csv) {

        todos.addEventListener("change", function(){
            docx.checked = todos.checked;
            csv.checked = todos.checked;
        });

        function sincronizar(){
            todos.checked =
                docx.checked && csv.checked;

            todos.indeterminate =
                docx.checked !== csv.checked;
        }

        docx.addEventListener("change", sincronizar);
        csv.addEventListener("change", sincronizar);
    }
}

if(document.readyState === "loading"){
    document.addEventListener(
        "DOMContentLoaded",
        iniciar
    );
}else{
    iniciar();
}
})();
</script>
"""

    if "</body>" in html:
        return html.replace(
            "</body>",
            bloco + "\n</body>",
            1,
        )

    return html + bloco

pagina_interface = _vs_historico_pagina_interface_3


# ============================================================
# VERITASSEC_CORRECAO_INTERFACE_UI_FS_MULTIMODELO
# ============================================================

_pagina_interface_base_fs_mm = pagina_interface


def _vs_historico_pagina_interface_4() -> str:

    html = _pagina_interface_base_fs_mm()

    html = html.replace(
        '<select id="projeto"></select>',
        r"""
<div style="display:grid;grid-template-columns:1fr auto;gap:8px;">
<input
    id="projetoPicker"
    type="text"
    readonly
    placeholder="Selecione o diretório do projeto"
>
<button id="btnSelecionarProjeto" type="button">
Selecionar diretório
</button>
</div>
<select id="projeto" style="display:none"></select>
""",
        1,
    )

    html = html.replace(
        '<select id="sarif"></select>',
        r"""
<div style="display:grid;grid-template-columns:1fr auto;gap:8px;">
<input
    id="sarifPicker"
    type="text"
    readonly
    placeholder="Selecione o arquivo SARIF"
>
<button id="btnSelecionarSarif" type="button">
Selecionar SARIF
</button>
</div>
<select id="sarif" style="display:none"></select>
""",
        1,
    )

    bloco = r"""
<style id="veritassec-fs-mm-style">
#vsFsModal{
    position:fixed;
    inset:0;
    z-index:99999;
    display:none;
    align-items:center;
    justify-content:center;
    background:rgba(0,0,0,.55);
}
#vsFsModal.ativo{display:flex;}
#vsFsPainel{
    width:min(900px,92vw);
    max-height:82vh;
    overflow:hidden;
    background:#fff;
    border:1px solid #cbd5e1;
    border-radius:10px;
    box-shadow:0 20px 60px rgba(0,0,0,.3);
}
#vsFsTopo{
    display:flex;
    gap:8px;
    align-items:center;
    padding:12px;
    border-bottom:1px solid #d7dde5;
}
#vsFsCaminho{
    flex:1;
    font-family:monospace;
    font-size:12px;
}
#vsFsLista{
    padding:8px;
    max-height:58vh;
    overflow:auto;
}
.vsFsItem{
    display:flex;
    align-items:center;
    width:100%;
    padding:8px 10px;
    margin:2px 0;
    border:0;
    border-radius:5px;
    background:#f8fafc;
    text-align:left;
    cursor:pointer;
}
.vsFsItem:hover{background:#e8eef8;}
#vsFsRodape{
    display:flex;
    justify-content:flex-end;
    gap:8px;
    padding:12px;
    border-top:1px solid #d7dde5;
}
#vsMmConfig{
    margin-top:14px;
    padding:14px;
    border:1px solid #d7dde5;
    border-radius:6px;
    background:#fbfcfe;
}
.vsMmLinha{
    display:grid;
    grid-template-columns:140px minmax(220px,1fr) minmax(220px,1fr);
    gap:8px;
    align-items:center;
    margin:8px 0;
}
.vsMmLinha input[type="text"],
.vsMmLinha input[type="password"]{width:100%;}
@media(max-width:900px){
    .vsMmLinha{grid-template-columns:1fr;}
}
</style>

<div id="vsFsModal">
    <div id="vsFsPainel">
        <div id="vsFsTopo">
            <button id="vsFsSubir" type="button">↑ Subir</button>
            <input id="vsFsCaminho" type="text" readonly>
            <button id="vsFsFecharTopo" type="button">Fechar</button>
        </div>

        <div id="vsFsLista"></div>

        <div id="vsFsRodape">
            <button id="vsFsSelecionarAtual" type="button">
                Selecionar diretório atual
            </button>
            <button id="vsFsCancelar" type="button">Cancelar</button>
        </div>
    </div>
</div>

<script id="veritassec-fs-mm-js">
(function(){
"use strict";

const $vs = (id) => document.getElementById(id);

let vsFsTipo = "diretorio";
let vsFsAtual = null;
let vsFsPai = null;

function vsSetSelect(id, valor, texto){
    const el = $vs(id);
    if(!el){ return; }

    el.innerHTML = "";

    const option = document.createElement("option");
    option.value = valor;
    option.textContent = texto || valor;
    option.selected = true;

    el.appendChild(option);
    el.value = valor;
}

async function vsApi(url, opt={}){
    const r = await fetch(url, opt);

    let dados = {};
    try{
        dados = await r.json();
    }catch(_){
        dados = {};
    }

    if(!r.ok){
        throw new Error(
            dados?.detail
            || ("HTTP " + r.status)
        );
    }

    return dados;
}

async function vsAbrirFs(tipo, caminho=null){
    vsFsTipo = tipo;

    const q = new URLSearchParams();
    q.set("tipo", tipo);

    if(caminho){
        q.set("path", caminho);
    }

    const dados = await vsApi(
        "/api/interface/fs?"
        + q.toString()
    );

    vsFsAtual = dados.atual;
    vsFsPai = dados.pai;

    $vs("vsFsCaminho").value = dados.atual;

    const lista = $vs("vsFsLista");
    lista.innerHTML = "";

    for(const item of dados.itens){
        const botao = document.createElement("button");

        botao.type = "button";
        botao.className = "vsFsItem";

        botao.textContent =
            (
                item.tipo === "diretorio"
                ? "📁 "
                : "📄 "
            )
            + item.nome;

        botao.onclick = async () => {
            if(item.tipo === "diretorio"){
                await vsAbrirFs(
                    tipo,
                    item.caminho
                );
                return;
            }

            if(tipo === "sarif"){
                $vs("sarifPicker").value = item.caminho;

                vsSetSelect(
                    "sarif",
                    item.caminho,
                    item.nome
                );

                vsFecharFs();
            }
        };

        lista.appendChild(botao);
    }

    $vs("vsFsSelecionarAtual").style.display =
        (
            tipo === "diretorio"
            ? ""
            : "none"
        );

    $vs("vsFsModal").classList.add("ativo");
}

function vsFecharFs(){
    $vs("vsFsModal").classList.remove("ativo");
}

async function vsCarregarMm(){
    try{
        const c = await vsApi(
            "/api/interface/config-multimodelo"
        );

        $vs("mmLocal").checked = !!c.usar_local;
        $vs("mmModeloLocal").value = c.modelo_local || "";

        $vs("mmGpt").checked = !!c.usar_gpt;
        $vs("mmModeloGpt").value = c.modelo_gpt || "";

        $vs("mmGemini").checked = !!c.usar_gemini;
        $vs("mmModeloGemini").value = c.modelo_gemini || "";

        $vs("mmStatus").textContent =
            (
                "GPT key: "
                + (
                    c.api_key_gpt_configurada
                    ? "SIM"
                    : "NAO"
                )
                + " | Gemini key: "
                + (
                    c.api_key_gemini_configurada
                    ? "SIM"
                    : "NAO"
                )
            );

    }catch(e){
        $vs("mmStatus").textContent = e.message;
    }
}

async function vsSalvarMm(){
    const payload = {
        usar_local: $vs("mmLocal").checked,
        modelo_local: $vs("mmModeloLocal").value.trim(),

        usar_gpt: $vs("mmGpt").checked,
        modelo_gpt: $vs("mmModeloGpt").value.trim(),

        usar_gemini: $vs("mmGemini").checked,
        modelo_gemini: $vs("mmModeloGemini").value.trim()
    };

    try{
        const keyGpt = $vs("mmGptKey").value.trim();
        const keyGemini = $vs("mmGeminiKey").value.trim();

        if(payload.usar_gpt && keyGpt){
            await vsApi(
                "/api/interface/api-key",
                {
                    method:"POST",
                    headers:{
                        "Content-Type":"application/json"
                    },
                    body:JSON.stringify({
                        provedor:"openai",
                        api_key:keyGpt
                    })
                }
            );

            $vs("mmGptKey").value = "";
        }

        if(payload.usar_gemini && keyGemini){
            await vsApi(
                "/api/interface/api-key",
                {
                    method:"POST",
                    headers:{
                        "Content-Type":"application/json"
                    },
                    body:JSON.stringify({
                        provedor:"gemini",
                        api_key:keyGemini
                    })
                }
            );

            $vs("mmGeminiKey").value = "";
        }

        const salvo = await vsApi(
            "/api/interface/config-multimodelo",
            {
                method:"POST",
                headers:{
                    "Content-Type":"application/json"
                },
                body:JSON.stringify(payload)
            }
        );

        $vs("mmStatus").textContent =
            (
                "Configuração salva. Provedores ativos: "
                + (
                    salvo.provedores_ativos
                    || []
                ).join(", ")
                + " | Multimodelo: "
                + (
                    salvo.multimodelo_ativo
                    ? "SIM"
                    : "NAO"
                )
            );

    }catch(e){
        $vs("mmStatus").textContent =
            "Erro: " + e.message;
    }
}

function vsInstalarMm(){
    const status = $vs("statusConfig");

    if(status && !$vs("vsMmConfig")){
        const card = document.createElement("div");

        card.id = "vsMmConfig";

        card.innerHTML = `
<h3>Configuração multimodelo dos agentes</h3>

<p>
Selecione um ou mais provedores. Local, GPT e Gemini
são provedores de raciocínio dos mesmos 7 agentes;
não criam agentes adicionais.
</p>

<div class="vsMmLinha">
    <label>
        <input id="mmLocal" type="checkbox">
        Local
    </label>

    <input
        id="mmModeloLocal"
        type="text"
        placeholder="Modelo local"
    >

    <span>Não requer API key externa</span>
</div>

<div class="vsMmLinha">
    <label>
        <input id="mmGpt" type="checkbox">
        GPT / OpenAI
    </label>

    <input
        id="mmModeloGpt"
        type="text"
        placeholder="Modelo GPT"
    >

    <input
        id="mmGptKey"
        type="password"
        autocomplete="off"
        placeholder="API key GPT (opcional se já carregada)"
    >
</div>

<div class="vsMmLinha">
    <label>
        <input id="mmGemini" type="checkbox">
        Gemini
    </label>

    <input
        id="mmModeloGemini"
        type="text"
        placeholder="Modelo Gemini"
    >

    <input
        id="mmGeminiKey"
        type="password"
        autocomplete="off"
        placeholder="API key Gemini (opcional se já carregada)"
    >
</div>

<button id="mmSalvar" type="button">
Salvar configuração multimodelo
</button>

<div
    id="mmStatus"
    class="status"
    style="margin-top:8px"
></div>
`;

        status.parentNode.insertBefore(
            card,
            status
        );

        $vs("mmSalvar").addEventListener(
            "click",
            vsSalvarMm
        );

        vsCarregarMm();
    }
}

function vsInstalarFs(){
    const bp = $vs("btnSelecionarProjeto");
    const bs = $vs("btnSelecionarSarif");

    if(bp){
        bp.addEventListener(
            "click",
            () => vsAbrirFs("diretorio")
        );
    }

    if(bs){
        bs.addEventListener(
            "click",
            () => vsAbrirFs("sarif")
        );
    }

    $vs("vsFsCancelar")?.addEventListener(
        "click",
        vsFecharFs
    );

    $vs("vsFsFecharTopo")?.addEventListener(
        "click",
        vsFecharFs
    );

    $vs("vsFsSubir")?.addEventListener(
        "click",
        async () => {
            if(vsFsPai){
                await vsAbrirFs(
                    vsFsTipo,
                    vsFsPai
                );
            }
        }
    );

    $vs("vsFsSelecionarAtual")?.addEventListener(
        "click",
        () => {
            if(
                vsFsTipo !== "diretorio"
                || !vsFsAtual
            ){
                return;
            }

            $vs("projetoPicker").value = vsFsAtual;

            vsSetSelect(
                "projeto",
                vsFsAtual,
                vsFsAtual
            );

            vsFecharFs();
        }
    );
}

function vsSincronizarLegados(){
    const projeto = $vs("projeto");
    const sarif = $vs("sarif");

    if(
        projeto
        && projeto.value
        && !$vs("projetoPicker").value
    ){
        $vs("projetoPicker").value = projeto.value;
    }

    if(
        sarif
        && sarif.value
        && !$vs("sarifPicker").value
    ){
        $vs("sarifPicker").value = sarif.value;
    }
}

function vsInicializar(){
    vsInstalarFs();
    vsInstalarMm();

    setTimeout(
        vsSincronizarLegados,
        400
    );

    setTimeout(
        vsSincronizarLegados,
        1200
    );
}

if(document.readyState === "loading"){
    document.addEventListener(
        "DOMContentLoaded",
        vsInicializar
    );
}else{
    vsInicializar();
}

})();
</script>
"""

    if "</body>" in html:
        return html.replace(
            "</body>",
            bloco + "\n</body>",
            1,
        )

    return html + bloco

pagina_interface = _vs_historico_pagina_interface_4


# ============================================================
# VERITASSEC_INTERFACE_TELAS_REAIS_20261019
# ============================================================

_pagina_interface_antes_telas_reais = pagina_interface


def _vs_historico_pagina_interface_5() -> str:

    html = _pagina_interface_antes_telas_reais()

    extensao = r"""

<!-- VERITASSEC_INTERFACE_TELAS_REAIS_20261019 -->


<style id="vsTelasReaisStyle">

/* =========================================================
   NAVEGAÇÃO PRINCIPAL
   ========================================================= */

.vs-nav-principal {
    display:flex !important;
    flex-wrap:wrap;
    gap:5px;
    margin-bottom:16px;
    border-bottom:1px solid #d7dde5;
}

.vs-nav-principal .vs-tab-principal {
    border:1px solid #bcc5cf;
    border-bottom:0;
    padding:11px 17px;
    background:#e7ebf0;
    color:#26313c;
    border-radius:6px 6px 0 0;
    cursor:pointer;
}

.vs-nav-principal .vs-tab-principal.ativo {
    background:#ffffff;
    color:#174ea6;
    font-weight:bold;
}


/* =========================================================
   TELAS
   ========================================================= */

.vs-tela-principal {
    display:none !important;
}

.vs-tela-principal.ativa {
    display:block !important;
}


/* =========================================================
   CONFIGURAÇÃO
   ========================================================= */

/*
 * Configuração antiga monomodelo:
 * Provedor / Modelo / API Key / timeout / tokens /
 * temperatura deixam de ser exibidos.
 */
#config > .grid,
#config > .actions,
#statusConfig {
    display:none !important;
}


/*
 * Mantém apenas a configuração multimodelo.
 */
#vsMmConfig {
    display:block !important;
    margin-top:10px;
}

#vsMmConfig h3 {
    margin-top:0;
}


/* =========================================================
   PROJETO / SARIF
   ========================================================= */

#projetoPicker,
#sarifPicker {
    cursor:pointer !important;
    background:#ffffff !important;
}

#projetoPicker:hover,
#sarifPicker:hover {
    border-color:#174ea6 !important;
}


/* =========================================================
   NAVEGAÇÃO INTERNA ANTIGA
   ========================================================= */

/*
 * Os antigos botões:
 * Análise / Resultados / Evidências / Gráficos
 * deixam de aparecer no conteúdo.
 *
 * Continuam existindo internamente somente para preservar
 * os renderizadores já implementados.
 */
.vs-nav-interna-legada {
    display:none !important;
}


/* =========================================================
   NOVAS TELAS
   ========================================================= */

#vsTelaEvidencias,
#vsTelaGraficos {
    background:#ffffff;
    border:1px solid #d7dde5;
    border-radius:7px;
    padding:22px;
    min-height:300px;
}

#vsTelaEvidencias > h2,
#vsTelaGraficos > h2 {
    margin-top:0;
}


/* =========================================================
   WORKSPACE COMPARTILHADO
   ========================================================= */

#vsWorkspaceMultiagente {
    margin-top:15px;
}


/* =========================================================
   RESPONSIVIDADE
   ========================================================= */

@media(max-width:760px) {

    .vs-nav-principal {
        flex-direction:column;
    }

    .vs-nav-principal .vs-tab-principal {
        border-bottom:1px solid #bcc5cf;
        border-radius:5px;
    }
}

</style>


<script id="vsTelasReaisScript">

(function(){

"use strict";


const $vs = (id) =>
    document.getElementById(id);


const normalizarTexto = (valor) =>
    String(valor || "")
        .trim()
        .toLowerCase()
        .normalize("NFD")
        .replace(
            /[\u0300-\u036f]/g,
            ""
        );


/* =========================================================
   1. SELEÇÃO PROJETO/SARIF
   ========================================================= */

function configurarSeletores(){

    const projeto =
        $vs(
            "projetoPicker"
        );

    const sarif =
        $vs(
            "sarifPicker"
        );

    const btnProjeto =
        $vs(
            "btnSelecionarProjeto"
        );

    const btnSarif =
        $vs(
            "btnSelecionarSarif"
        );


    if (
        projeto
        && btnProjeto
    ) {

        projeto.readOnly =
            true;

        projeto.placeholder =
            "Clique para escolher o diretório do projeto";

        projeto.title =
            "Clique para selecionar o diretório do projeto";

        projeto.onclick =
            function(){

                btnProjeto.click();
            };

        btnProjeto.style.display =
            "none";
    }


    if (
        sarif
        && btnSarif
    ) {

        sarif.readOnly =
            true;

        sarif.placeholder =
            "Clique para escolher o arquivo .sarif";

        sarif.title =
            "Clique para selecionar o arquivo SARIF";

        sarif.onclick =
            function(){

                btnSarif.click();
            };

        btnSarif.style.display =
            "none";
    }
}


/* =========================================================
   2. CONFIGURAÇÃO MULTIMODELO ÚNICA
   ========================================================= */

function configurarMultimodelo(){

    const card =
        $vs(
            "vsMmConfig"
        );


    if (!card) {

        return;
    }


    const titulo =
        card.querySelector(
            "h3"
        );


    if (titulo) {

        titulo.textContent =
            "Modelos utilizados pelos 7 agentes";
    }


    const descricao =
        card.querySelector(
            "p"
        );


    if (descricao) {

        descricao.textContent =
            (
                "Selecione Local, GPT e/ou Gemini. "
                + "Os modelos selecionados são motores "
                + "de raciocínio utilizados pelos mesmos "
                + "sete agentes especializados."
            );
    }
}


/* =========================================================
   3. LOCALIZA NAVEGAÇÃO INTERNA ANTIGA
   ========================================================= */

function localizarBotoesInternos(){

    const nomes =
        new Set([
            "analise",
            "resultados",
            "evidencias",
            "graficos"
        ]);


    return Array
        .from(
            document.querySelectorAll(
                "button"
            )
        )
        .filter(
            (botao) => {

                /*
                 * Não captura as abas principais antigas.
                 */
                if (
                    botao.closest(
                        ".tabs"
                    )
                ) {

                    return false;
                }


                if (
                    botao.classList.contains(
                        "vs-tab-principal"
                    )
                ) {

                    return false;
                }


                return nomes.has(
                    normalizarTexto(
                        botao.textContent
                    )
                );
            }
        );
}


/* =========================================================
   4. WORKSPACE MULTIAGENTE
   ========================================================= */

function localizarWorkspace(){

    const botoes =
        localizarBotoesInternos();


    if (
        botoes.length < 4
    ) {

        return {
            workspace:null,
            botoes:[]
        };
    }


    const nav =
        botoes[0]
            .parentElement;


    if (
        !nav
        || !botoes.every(
            b =>
                b.parentElement
                === nav
        )
    ) {

        return {
            workspace:null,
            botoes:botoes
        };
    }


    nav.classList.add(
        "vs-nav-interna-legada"
    );


    /*
     * O conteúdo multiagente está no contêiner imediatamente
     * acima da navegação interna.
     */
    let workspace =
        nav.parentElement;


    /*
     * Segurança: nunca mover BODY, HTML ou MAIN inteiro.
     */
    if (
        !workspace
        || workspace === document.body
        || workspace === document.documentElement
        || workspace.tagName === "MAIN"
    ) {

        /*
         * Cria um wrapper apenas para os elementos que seguem
         * a navegação interna, sem movimentar a página inteira.
         */
        workspace =
            document.createElement(
                "div"
            );

        workspace.id =
            "vsWorkspaceMultiagente";


        const pai =
            nav.parentElement;


        if (pai) {

            pai.insertBefore(
                workspace,
                nav
            );


            workspace.appendChild(
                nav
            );


            let candidato =
                workspace.nextSibling;


            while (
                candidato
                && candidato.nodeType
                    === Node.TEXT_NODE
            ) {

                candidato =
                    candidato.nextSibling;
            }
        }

    } else {

        workspace.id =
            "vsWorkspaceMultiagente";
    }


    return {
        workspace:
            workspace,

        botoes:
            botoes
    };
}


/* =========================================================
   5. CRIA AS TELAS QUE AINDA NÃO EXISTEM
   ========================================================= */

function criarTela(
    id,
    titulo
){

    let tela =
        $vs(id);


    if (tela) {

        return tela;
    }


    tela =
        document.createElement(
            "section"
        );


    tela.id =
        id;

    tela.className =
        "panel vs-tela-principal";


    const h2 =
        document.createElement(
            "h2"
        );


    h2.textContent =
        titulo;


    tela.appendChild(
        h2
    );


    const main =
        document.querySelector(
            "main"
        );


    if (main) {

        main.appendChild(
            tela
        );

    } else {

        document.body.appendChild(
            tela
        );
    }


    return tela;
}


/* =========================================================
   6. EXPORTAÇÃO VAI PARA RESULTADOS
   ========================================================= */

function moverExportacaoParaResultados(){

    const resultados =
        $vs(
            "resultados"
        );


    if (!resultados) {

        return;
    }


    const candidatos =
        Array.from(
            document.querySelectorAll(
                "section, div"
            )
        );


    for (
        const candidato
        of candidatos
    ) {

        const h2 =
            candidato.querySelector(
                ":scope > h2"
            );


        if (
            h2
            && normalizarTexto(
                h2.textContent
            ) === "exportacao"
            && candidato !== resultados
            && !resultados.contains(
                candidato
            )
        ) {

            resultados.appendChild(
                candidato
            );

            break;
        }
    }
}


/* =========================================================
   7. NAVEGAÇÃO PRINCIPAL REAL
   ========================================================= */

function construirNavegacao(){

    const navAntiga =
        document.querySelector(
            "main > .tabs"
        )
        || document.querySelector(
            ".tabs"
        );


    if (!navAntiga) {

        return null;
    }


    /*
     * Evita manter os quatro botões internos como navegação.
     */
    const nav =
        document.createElement(
            "div"
        );


    nav.id =
        "vsNavegacaoPrincipal";

    nav.className =
        "vs-nav-principal";


    const telas = [
        [
            "config",
            "Configuração"
        ],
        [
            "analise",
            "Análise"
        ],
        [
            "resultados",
            "Resultados"
        ],
        [
            "vsTelaEvidencias",
            "Evidências"
        ],
        [
            "vsTelaGraficos",
            "Gráficos"
        ],
        [
            "agent",
            "VeritasSec-Agent"
        ]
    ];


    for (
        const [id, rotulo]
        of telas
    ) {

        const botao =
            document.createElement(
                "button"
            );


        botao.type =
            "button";

        botao.className =
            "vs-tab-principal";

        botao.dataset.tela =
            id;

        botao.textContent =
            rotulo;


        nav.appendChild(
            botao
        );
    }


    navAntiga.replaceWith(
        nav
    );


    return nav;
}


/* =========================================================
   8. CONTROLE DAS TELAS
   ========================================================= */

function prepararTelas(){

    const ids = [
        "config",
        "analise",
        "resultados",
        "vsTelaEvidencias",
        "vsTelaGraficos",
        "agent"
    ];


    for (
        const id
        of ids
    ) {

        const tela =
            $vs(id);


        if (!tela) {

            continue;
        }


        tela.classList.remove(
            "active"
        );

        tela.classList.add(
            "vs-tela-principal"
        );
    }
}


/* =========================================================
   9. ACIONA O RENDERIZADOR INTERNO LEGADO
   ========================================================= */

function clicarModoInterno(
    botoes,
    nome
){

    const alvo =
        botoes.find(
            botao =>
                normalizarTexto(
                    botao.textContent
                ) === nome
        );


    if (alvo) {

        alvo.click();
    }
}


/* =========================================================
   10. TROCA DE TELA
   ========================================================= */

function instalarNavegacao(
    nav,
    workspace,
    botoesInternos
){

    if (!nav) {

        return;
    }


    const telas = {
        config:
            $vs(
                "config"
            ),

        analise:
            $vs(
                "analise"
            ),

        resultados:
            $vs(
                "resultados"
            ),

        vsTelaEvidencias:
            $vs(
                "vsTelaEvidencias"
            ),

        vsTelaGraficos:
            $vs(
                "vsTelaGraficos"
            ),

        agent:
            $vs(
                "agent"
            )
    };


    function ativar(
        id
    ){

        for (
            const elemento
            of Object.values(
                telas
            )
        ) {

            if (elemento) {

                elemento.classList.remove(
                    "ativa"
                );
            }
        }


        for (
            const botao
            of nav.querySelectorAll(
                ".vs-tab-principal"
            )
        ) {

            botao.classList.toggle(
                "ativo",
                botao.dataset.tela
                    === id
            );
        }


        const tela =
            telas[id];


        if (tela) {

            tela.classList.add(
                "ativa"
            );
        }


        /*
         * O workspace é único.
         * Ele é fisicamente movido para a tela selecionada.
         * Portanto Resultados/Evidências/Gráficos deixam de ser
         * meros botões no mesmo painel.
         */
        if (
            workspace
            && tela
        ) {

            if (
                id === "analise"
            ) {

                tela.appendChild(
                    workspace
                );

                clicarModoInterno(
                    botoesInternos,
                    "analise"
                );
            }


            if (
                id === "resultados"
            ) {

                tela.appendChild(
                    workspace
                );

                clicarModoInterno(
                    botoesInternos,
                    "resultados"
                );
            }


            if (
                id === "vsTelaEvidencias"
            ) {

                tela.appendChild(
                    workspace
                );

                clicarModoInterno(
                    botoesInternos,
                    "evidencias"
                );
            }


            if (
                id === "vsTelaGraficos"
            ) {

                tela.appendChild(
                    workspace
                );

                clicarModoInterno(
                    botoesInternos,
                    "graficos"
                );
            }
        }


        try {

            sessionStorage.setItem(
                "veritassec-tela",
                id
            );

        } catch (_) {

            /* sem impacto */
        }
    }


    for (
        const botao
        of nav.querySelectorAll(
            ".vs-tab-principal"
        )
    ) {

        botao.addEventListener(
            "click",
            () => {

                ativar(
                    botao.dataset.tela
                );
            }
        );
    }


    let inicial =
        "config";


    try {

        const salva =
            sessionStorage.getItem(
                "veritassec-tela"
            );


        if (
            salva
            && Object.prototype.hasOwnProperty.call(
                telas,
                salva
            )
        ) {

            inicial =
                salva;
        }

    } catch (_) {

        /* sem impacto */
    }


    ativar(
        inicial
    );
}


/* =========================================================
   11. REMOVE BOTÕES INTERNOS DA APRESENTAÇÃO
   ========================================================= */

function ocultarNavegacaoInterna(
    botoes
){

    if (!botoes.length) {

        return;
    }


    const pai =
        botoes[0]
            .parentElement;


    if (
        pai
        && botoes.every(
            b =>
                b.parentElement
                === pai
        )
    ) {

        pai.classList.add(
            "vs-nav-interna-legada"
        );

        pai.setAttribute(
            "aria-hidden",
            "true"
        );
    }
}


/* =========================================================
   12. INICIALIZAÇÃO
   ========================================================= */

function inicializarTelasReais(){

    /*
     * Aguarda as extensões anteriores criarem:
     * - projetoPicker
     * - sarifPicker
     * - vsMmConfig
     * - workspace multiagente
     */
    setTimeout(
        () => {

            configurarSeletores();

            configurarMultimodelo();


            const evidencias =
                criarTela(
                    "vsTelaEvidencias",
                    "Evidências"
                );


            const graficos =
                criarTela(
                    "vsTelaGraficos",
                    "Gráficos"
                );


            /*
             * IDs explícitos para os testes e para acessibilidade.
             */
            evidencias.dataset.telaReal =
                "evidencias";

            graficos.dataset.telaReal =
                "graficos";


            const localizado =
                localizarWorkspace();


            ocultarNavegacaoInterna(
                localizado.botoes
            );


            moverExportacaoParaResultados();


            prepararTelas();


            const nav =
                construirNavegacao();


            instalarNavegacao(
                nav,
                localizado.workspace,
                localizado.botoes
            );

        },
        350
    );
}


if (
    document.readyState
    === "loading"
) {

    document.addEventListener(
        "DOMContentLoaded",
        inicializarTelasReais
    );

} else {

    inicializarTelasReais();
}

})();
</script>

"""

    if "</body>" in html:

        return html.replace(
            "</body>",
            extensao + "\n</body>",
            1,
        )

    return html + extensao

pagina_interface = _vs_historico_pagina_interface_5


# ============================================================
# VERITASSEC_SELETOR_FS_DIRETO_20261019
# ============================================================

_pagina_interface_antes_fs_direto = pagina_interface


def _vs_historico_pagina_interface_6() -> str:

    html = _pagina_interface_antes_fs_direto()

    extensao = r"""

<!-- VERITASSEC_SELETOR_FS_DIRETO_20261019 -->


<style id="vsFsDiretoStyle">

#projetoPicker,
#sarifPicker {

    cursor:pointer !important;

    background-color:#ffffff !important;

    background-repeat:no-repeat !important;

    background-position:
        right 10px center !important;

    padding-right:42px !important;
}


#projetoPicker:hover,
#sarifPicker:hover {

    border-color:#174ea6 !important;

    box-shadow:
        0 0 0 1px
        rgba(23,78,166,.20);
}


/*
 * Modal real de seleção.
 */

#vsFsDiretoModal {

    position:fixed;

    inset:0;

    z-index:1000000;

    display:none;

    align-items:center;
    justify-content:center;

    background:
        rgba(0,0,0,.62);
}


#vsFsDiretoModal.aberto {

    display:flex;
}


#vsFsDiretoPainel {

    width:
        min(
            1000px,
            94vw
        );

    max-height:
        88vh;

    display:flex;
    flex-direction:column;

    background:#fff;

    border:
        1px solid
        #b9c2cc;

    border-radius:
        10px;

    box-shadow:
        0 24px 70px
        rgba(0,0,0,.38);
}


#vsFsDiretoCabecalho {

    display:grid;

    grid-template-columns:
        auto
        1fr
        auto;

    gap:8px;

    align-items:center;

    padding:12px;

    border-bottom:
        1px solid
        #d7dde5;
}


#vsFsDiretoTitulo {

    grid-column:
        1 / -1;

    margin:
        0 0 4px 0;

    font-size:
        16px;
}


#vsFsDiretoCaminho {

    width:100%;

    font-family:
        monospace;

    font-size:
        12px;
}


#vsFsDiretoLista {

    min-height:
        330px;

    max-height:
        58vh;

    overflow:auto;

    padding:
        8px;
}


.vs-fs-direto-item {

    display:flex;

    align-items:center;

    width:100%;

    margin:
        2px 0;

    padding:
        10px 12px;

    border:0;

    border-radius:
        5px;

    background:
        #f7f9fc;

    text-align:left;

    cursor:pointer;
}


.vs-fs-direto-item:hover {

    background:
        #e8eef8;
}


.vs-fs-direto-tipo {

    display:inline-block;

    width:
        28px;

    margin-right:
        8px;
}


#vsFsDiretoRodape {

    display:flex;

    justify-content:
        flex-end;

    gap:
        8px;

    padding:
        12px;

    border-top:
        1px solid
        #d7dde5;
}


#vsFsDiretoRodape button,
#vsFsDiretoCabecalho button {

    cursor:pointer;

    padding:
        8px 13px;
}


#vsFsDiretoMensagem {

    padding:
        8px 12px;

    color:
        #5b6670;

    font-size:
        12px;
}

</style>


<div id="vsFsDiretoModal">

    <div id="vsFsDiretoPainel">

        <div id="vsFsDiretoCabecalho">

            <h3 id="vsFsDiretoTitulo">
                Selecionar
            </h3>


            <button
                id="vsFsDiretoSubir"
                type="button"
            >
                ↑ Subir
            </button>


            <input
                id="vsFsDiretoCaminho"
                type="text"
                readonly
            >


            <button
                id="vsFsDiretoFechar"
                type="button"
            >
                Fechar
            </button>

        </div>


        <div id="vsFsDiretoMensagem"></div>


        <div id="vsFsDiretoLista"></div>


        <div id="vsFsDiretoRodape">

            <button
                id="vsFsDiretoSelecionarPasta"
                type="button"
            >
                Selecionar esta pasta
            </button>


            <button
                id="vsFsDiretoCancelar"
                type="button"
            >
                Cancelar
            </button>

        </div>

    </div>

</div>


<script id="vsFsDiretoScript">

(function(){

"use strict";


const vsEl = (id) =>
    document.getElementById(
        id
    );


let vsTipoSelecao =
    null;


let vsDiretorioAtual =
    null;


let vsDiretorioPai =
    null;


/* =========================================================
   API
   ========================================================= */

async function vsFsApi(
    url
){

    const resposta =
        await fetch(
            url,
            {
                method:
                    "GET",

                cache:
                    "no-store"
            }
        );


    let dados =
        null;


    try {

        dados =
            await resposta.json();

    } catch (_) {

        dados =
            null;
    }


    if (
        !resposta.ok
    ) {

        throw new Error(
            dados?.detail
            || (
                "Erro HTTP "
                + resposta.status
            )
        );
    }


    return dados;
}


/* =========================================================
   SELECT INTERNO
   ========================================================= */

function vsDefinirValor(
    selectId,
    campoId,
    valor
){

    const select =
        vsEl(
            selectId
        );


    const campo =
        vsEl(
            campoId
        );


    if (
        !select
        || !campo
    ) {

        throw new Error(
            "Campo interno não localizado."
        );
    }


    select.innerHTML =
        "";


    const option =
        document.createElement(
            "option"
        );


    option.value =
        valor;


    option.textContent =
        valor;


    option.selected =
        true;


    select.appendChild(
        option
    );


    select.value =
        valor;


    campo.value =
        valor;


    /*
     * Dispara eventos para qualquer lógica existente.
     */

    select.dispatchEvent(
        new Event(
            "change",
            {
                bubbles:
                    true
            }
        )
    );


    campo.dispatchEvent(
        new Event(
            "change",
            {
                bubbles:
                    true
            }
        )
    );
}


/* =========================================================
   MODAL
   ========================================================= */

function vsFecharFs(){

    vsEl(
        "vsFsDiretoModal"
    ).classList.remove(
        "aberto"
    );
}


/* =========================================================
   CARREGA PASTA
   ========================================================= */

async function vsCarregarPasta(
    caminho=null
){

    const params =
        new URLSearchParams();


    params.set(
        "tipo",
        (
            vsTipoSelecao
            === "sarif"
            ? "sarif"
            : "diretorio"
        )
    );


    if (
        caminho
    ) {

        params.set(
            "path",
            caminho
        );
    }


    const dados =
        await vsFsApi(
            "/api/interface/fs?"
            + params.toString()
        );


    vsDiretorioAtual =
        dados.atual;


    vsDiretorioPai =
        dados.pai;


    vsEl(
        "vsFsDiretoCaminho"
    ).value =
        dados.atual;


    const titulo =
        vsEl(
            "vsFsDiretoTitulo"
        );


    const mensagem =
        vsEl(
            "vsFsDiretoMensagem"
        );


    const btnSelecionar =
        vsEl(
            "vsFsDiretoSelecionarPasta"
        );


    if (
        vsTipoSelecao
        === "projeto"
    ) {

        titulo.textContent =
            "Selecionar diretório do projeto";


        mensagem.textContent =
            (
                "Navegue pelas pastas e clique em "
                + "\"Selecionar esta pasta\" "
                + "quando estiver no diretório desejado."
            );


        btnSelecionar.style.display =
            "";

    } else {

        titulo.textContent =
            "Selecionar arquivo SARIF";


        mensagem.textContent =
            (
                "Navegue pelas pastas e clique "
                + "diretamente no arquivo .sarif desejado."
            );


        btnSelecionar.style.display =
            "none";
    }


    const lista =
        vsEl(
            "vsFsDiretoLista"
        );


    lista.innerHTML =
        "";


    if (
        !dados.itens
        || dados.itens.length
        === 0
    ) {

        const vazio =
            document.createElement(
                "div"
            );


        vazio.style.padding =
            "20px";


        vazio.textContent =
            (
                vsTipoSelecao
                === "sarif"
                ? "Nenhuma pasta ou arquivo SARIF encontrado."
                : "Diretório vazio."
            );


        lista.appendChild(
            vazio
        );


        return;
    }


    for (
        const item
        of dados.itens
    ) {

        const botao =
            document.createElement(
                "button"
            );


        botao.type =
            "button";


        botao.className =
            "vs-fs-direto-item";


        const icone =
            (
                item.tipo
                === "diretorio"
                ? "📁"
                : "📄"
            );


        botao.innerHTML =
            (
                '<span class="vs-fs-direto-tipo">'
                + icone
                + "</span>"
                + "<span>"
                + String(
                    item.nome
                )
                + "</span>"
            );


        botao.addEventListener(
            "click",
            async () => {

                if (
                    item.tipo
                    === "diretorio"
                ) {

                    await vsCarregarPasta(
                        item.caminho
                    );


                    return;
                }


                if (
                    vsTipoSelecao
                    === "sarif"
                ) {

                    vsDefinirValor(
                        "sarif",
                        "sarifPicker",
                        item.caminho
                    );


                    vsFecharFs();
                }
            }
        );


        lista.appendChild(
            botao
        );
    }
}


/* =========================================================
   ABRIR
   ========================================================= */

async function vsAbrirFs(
    tipo
){

    vsTipoSelecao =
        tipo;


    try {

        await vsCarregarPasta();


        vsEl(
            "vsFsDiretoModal"
        ).classList.add(
            "aberto"
        );

    } catch (erro) {

        alert(
            "Não foi possível abrir o navegador de arquivos: "
            + erro.message
        );
    }
}


/* =========================================================
   EVENTOS
   ========================================================= */

function vsInstalarSeletores(){

    const projeto =
        vsEl(
            "projetoPicker"
        );


    const sarif =
        vsEl(
            "sarifPicker"
        );


    if (
        !projeto
        || !sarif
    ) {

        return;
    }


    /*
     * Remove comportamento herdado.
     */
    projeto.onclick =
        null;


    sarif.onclick =
        null;


    projeto.readOnly =
        true;


    sarif.readOnly =
        true;


    projeto.placeholder =
        "Clique aqui para escolher o diretório do projeto";


    sarif.placeholder =
        "Clique aqui para escolher o arquivo SARIF";


    projeto.title =
        "Selecionar diretório do projeto";


    sarif.title =
        "Selecionar arquivo SARIF";


    /*
     * Clique DIRETO no input.
     */
    projeto.addEventListener(
        "click",
        function(evento){

            evento.preventDefault();

            evento.stopPropagation();

            vsAbrirFs(
                "projeto"
            );
        },
        true
    );


    sarif.addEventListener(
        "click",
        function(evento){

            evento.preventDefault();

            evento.stopPropagation();

            vsAbrirFs(
                "sarif"
            );
        },
        true
    );


    /*
     * Também abre por teclado.
     */
    projeto.addEventListener(
        "keydown",
        function(evento){

            if (
                evento.key
                === "Enter"
                || evento.key
                === " "
            ) {

                evento.preventDefault();

                vsAbrirFs(
                    "projeto"
                );
            }
        }
    );


    sarif.addEventListener(
        "keydown",
        function(evento){

            if (
                evento.key
                === "Enter"
                || evento.key
                === " "
            ) {

                evento.preventDefault();

                vsAbrirFs(
                    "sarif"
                );
            }
        }
    );


    /*
     * Botões antigos não são mais necessários.
     */
    const antigoProjeto =
        vsEl(
            "btnSelecionarProjeto"
        );


    const antigoSarif =
        vsEl(
            "btnSelecionarSarif"
        );


    if (
        antigoProjeto
    ) {

        antigoProjeto.style.display =
            "none";
    }


    if (
        antigoSarif
    ) {

        antigoSarif.style.display =
            "none";
    }


    vsEl(
        "vsFsDiretoFechar"
    ).onclick =
        vsFecharFs;


    vsEl(
        "vsFsDiretoCancelar"
    ).onclick =
        vsFecharFs;


    vsEl(
        "vsFsDiretoSubir"
    ).onclick =
        async function(){

            if (
                vsDiretorioPai
            ) {

                await vsCarregarPasta(
                    vsDiretorioPai
                );
            }
        };


    vsEl(
        "vsFsDiretoSelecionarPasta"
    ).onclick =
        function(){

            if (
                vsTipoSelecao
                !== "projeto"
                || !vsDiretorioAtual
            ) {

                return;
            }


            vsDefinirValor(
                "projeto",
                "projetoPicker",
                vsDiretorioAtual
            );


            vsFecharFs();
        };


    /*
     * Clique no fundo fecha.
     */
    vsEl(
        "vsFsDiretoModal"
    ).addEventListener(
        "click",
        function(evento){

            if (
                evento.target
                === this
            ) {

                vsFecharFs();
            }
        }
    );
}


/*
 * Executa depois das extensões anteriores.
 */
function vsInicializarFsDireto(){

    setTimeout(
        vsInstalarSeletores,
        500
    );


    setTimeout(
        vsInstalarSeletores,
        1200
    );
}


if (
    document.readyState
    === "loading"
) {

    document.addEventListener(
        "DOMContentLoaded",
        vsInicializarFsDireto
    );

} else {

    vsInicializarFsDireto();
}

})();
</script>

"""

    if "</body>" in html:

        return html.replace(
            "</body>",
            extensao + "\n</body>",
            1,
        )

    return html + extensao

pagina_interface = _vs_historico_pagina_interface_6


# ============================================================
# VERITASSEC_FS_DEFINITIVO_20261019
# ============================================================

_pagina_interface_antes_fs_definitivo = pagina_interface


def _vs_historico_pagina_interface_7() -> str:

    html = _pagina_interface_antes_fs_definitivo()

    extensao = r"""

<!-- VERITASSEC_FS_DEFINITIVO_20261019 -->


<style id="vsFsDefStyle">

#projetoPicker,
#sarifPicker {

    cursor:pointer !important;

    background:
        #ffffff !important;

    caret-color:
        transparent !important;
}


#projetoPicker:hover,
#sarifPicker:hover {

    border-color:
        #174ea6 !important;

    box-shadow:
        0 0 0 1px
        rgba(23,78,166,.25);
}


#vsFsDefModal {

    position:fixed;

    inset:0;

    z-index:2147483647;

    display:none;

    align-items:center;

    justify-content:center;

    background:
        rgba(0,0,0,.65);
}


#vsFsDefModal.aberto {

    display:flex !important;
}


#vsFsDefJanela {

    width:
        min(
            1000px,
            94vw
        );

    height:
        min(
            720px,
            86vh
        );

    display:flex;

    flex-direction:column;

    background:#fff;

    border-radius:
        10px;

    box-shadow:
        0 25px 80px
        rgba(0,0,0,.40);

    overflow:hidden;
}


#vsFsDefCabecalho {

    padding:
        14px;

    border-bottom:
        1px solid
        #d7dde5;
}


#vsFsDefCabecalho h2 {

    margin:
        0 0 10px 0;
}


#vsFsDefBarra {

    display:grid;

    grid-template-columns:
        auto
        1fr
        auto;

    gap:
        8px;
}


#vsFsDefPath {

    width:
        100%;

    font-family:
        monospace;

    font-size:
        12px;
}


#vsFsDefAjuda {

    padding:
        9px 14px;

    background:
        #f8fafc;

    border-bottom:
        1px solid
        #e1e6ec;

    font-size:
        12px;
}


#vsFsDefLista {

    flex:
        1;

    overflow:
        auto;

    padding:
        8px;
}


.vsFsDefItem {

    display:flex;

    align-items:center;

    width:
        100%;

    border:
        0;

    border-radius:
        5px;

    margin:
        2px 0;

    padding:
        10px 12px;

    background:
        #f7f9fc;

    text-align:
        left;

    cursor:
        pointer;
}


.vsFsDefItem:hover {

    background:
        #e5edf8;
}


.vsFsDefIcone {

    display:inline-block;

    width:
        32px;
}


#vsFsDefRodape {

    display:flex;

    justify-content:
        flex-end;

    gap:
        8px;

    padding:
        12px;

    border-top:
        1px solid
        #d7dde5;
}


#vsFsDefRodape button,
#vsFsDefBarra button {

    cursor:pointer;

    padding:
        8px 13px;
}

</style>


<div id="vsFsDefModal">

    <div id="vsFsDefJanela">

        <div id="vsFsDefCabecalho">

            <h2 id="vsFsDefTitulo">
                Selecionar
            </h2>


            <div id="vsFsDefBarra">

                <button
                    id="vsFsDefSubir"
                    type="button"
                >
                    ↑ Subir
                </button>


                <input
                    id="vsFsDefPath"
                    type="text"
                    readonly
                >


                <button
                    id="vsFsDefFechar"
                    type="button"
                >
                    Fechar
                </button>

            </div>

        </div>


        <div id="vsFsDefAjuda"></div>


        <div id="vsFsDefLista"></div>


        <div id="vsFsDefRodape">

            <button
                id="vsFsDefEscolherPasta"
                type="button"
            >
                Selecionar esta pasta
            </button>


            <button
                id="vsFsDefCancelar"
                type="button"
            >
                Cancelar
            </button>

        </div>

    </div>

</div>


<script id="vsFsDefScript">

(function(){

"use strict";


const byId =
    function(id){

        return document.getElementById(
            id
        );
    };


let tipoAtual =
    null;


let pastaAtual =
    null;


let pastaPai =
    null;


/* ============================================================
   PREENCHE CAMPO + SELECT INTERNO
   ============================================================ */

function definirSelecao(
    tipo,
    caminho
){

    const campoId =
        (
            tipo === "projeto"
            ? "projetoPicker"
            : "sarifPicker"
        );


    const selectId =
        (
            tipo === "projeto"
            ? "projeto"
            : "sarif"
        );


    const campo =
        byId(
            campoId
        );


    const select =
        byId(
            selectId
        );


    if (
        !campo
        || !select
    ) {

        throw new Error(
            "Campos internos de seleção não encontrados."
        );
    }


    campo.value =
        caminho;


    select.innerHTML =
        "";


    const option =
        document.createElement(
            "option"
        );


    option.value =
        caminho;


    option.textContent =
        caminho;


    option.selected =
        true;


    select.appendChild(
        option
    );


    select.value =
        caminho;


    campo.dispatchEvent(
        new Event(
            "change",
            {
                bubbles:true
            }
        )
    );


    select.dispatchEvent(
        new Event(
            "change",
            {
                bubbles:true
            }
        )
    );
}


/* ============================================================
   FECHAR
   ============================================================ */

function fechar(){

    byId(
        "vsFsDefModal"
    ).classList.remove(
        "aberto"
    );
}


/* ============================================================
   API
   ============================================================ */

async function consultar(
    caminho
){

    const params =
        new URLSearchParams();


    params.set(
        "tipo",
        (
            tipoAtual === "sarif"
            ? "sarif"
            : "diretorio"
        )
    );


    if (
        caminho
    ) {

        params.set(
            "path",
            caminho
        );
    }


    const resposta =
        await fetch(
            (
                "/api/interface/fs?"
                + params.toString()
            ),
            {
                method:"GET",
                cache:"no-store"
            }
        );


    let dados =
        null;


    try {

        dados =
            await resposta.json();

    } catch (_) {

        dados =
            null;
    }


    if (
        !resposta.ok
    ) {

        throw new Error(
            dados?.detail
            || (
                "HTTP "
                + resposta.status
            )
        );
    }


    return dados;
}


/* ============================================================
   RENDERIZA DIRETÓRIO
   ============================================================ */

async function carregar(
    caminho=null
){

    const dados =
        await consultar(
            caminho
        );


    pastaAtual =
        dados.atual;


    pastaPai =
        dados.pai;


    byId(
        "vsFsDefPath"
    ).value =
        pastaAtual;


    const lista =
        byId(
            "vsFsDefLista"
        );


    lista.innerHTML =
        "";


    const escolherPasta =
        byId(
            "vsFsDefEscolherPasta"
        );


    if (
        tipoAtual === "projeto"
    ) {

        byId(
            "vsFsDefTitulo"
        ).textContent =
            "Selecionar diretório do projeto";


        byId(
            "vsFsDefAjuda"
        ).textContent =
            (
                "Entre nas pastas e, quando chegar ao "
                + "diretório desejado, clique em "
                + "\"Selecionar esta pasta\"."
            );


        escolherPasta.style.display =
            "";

    } else {

        byId(
            "vsFsDefTitulo"
        ).textContent =
            "Selecionar arquivo SARIF";


        byId(
            "vsFsDefAjuda"
        ).textContent =
            (
                "Entre nas pastas e clique diretamente "
                + "no arquivo .sarif desejado."
            );


        escolherPasta.style.display =
            "none";
    }


    for (
        const item
        of dados.itens
    ) {

        const botao =
            document.createElement(
                "button"
            );


        botao.type =
            "button";


        botao.className =
            "vsFsDefItem";


        const icone =
            (
                item.tipo === "diretorio"
                ? "📁"
                : "📄"
            );


        botao.innerHTML =
            (
                '<span class="vsFsDefIcone">'
                + icone
                + "</span>"
                + "<span>"
                + item.nome
                + "</span>"
            );


        botao.onclick =
            async function(){

                if (
                    item.tipo
                    === "diretorio"
                ) {

                    await carregar(
                        item.caminho
                    );


                    return;
                }


                if (
                    tipoAtual
                    === "sarif"
                ) {

                    definirSelecao(
                        "sarif",
                        item.caminho
                    );


                    fechar();
                }
            };


        lista.appendChild(
            botao
        );
    }


    if (
        dados.itens.length === 0
    ) {

        const vazio =
            document.createElement(
                "div"
            );


        vazio.style.padding =
            "20px";


        vazio.textContent =
            (
                tipoAtual === "sarif"
                ? "Nenhuma pasta ou arquivo SARIF nesta localização."
                : "Diretório vazio."
            );


        lista.appendChild(
            vazio
        );
    }
}


/* ============================================================
   FUNÇÃO GLOBAL DIRETA
   ============================================================ */

window.veritasSecAbrirSeletor =
    async function(tipo){

        tipoAtual =
            tipo;


        try {

            await carregar(
                null
            );


            byId(
                "vsFsDefModal"
            ).classList.add(
                "aberto"
            );

        } catch (erro) {

            window.alert(
                (
                    "Erro ao abrir diretórios: "
                    + erro.message
                )
            );
        }
    };


/* ============================================================
   REMOVE TODOS OS HANDLERS ANTIGOS
   ============================================================ */

function recriarInput(
    id,
    tipo
){

    const antigo =
        byId(
            id
        );


    if (
        !antigo
    ) {

        return null;
    }


    /*
     * cloneNode remove os listeners registrados
     * anteriormente por addEventListener.
     */
    const novo =
        antigo.cloneNode(
            true
        );


    antigo.replaceWith(
        novo
    );


    novo.readOnly =
        true;


    novo.removeAttribute(
        "onclick"
    );


    novo.style.cursor =
        "pointer";


    novo.setAttribute(
        "role",
        "button"
    );


    novo.setAttribute(
        "tabindex",
        "0"
    );


    if (
        tipo === "projeto"
    ) {

        novo.placeholder =
            "Clique para escolher o diretório do projeto";


        novo.title =
            "Escolher diretório do projeto";

    } else {

        novo.placeholder =
            "Clique para escolher o arquivo SARIF";


        novo.title =
            "Escolher arquivo SARIF";
    }


    /*
     * HANDLER DIRETO.
     */
    novo.onclick =
        function(evento){

            evento.preventDefault();

            evento.stopImmediatePropagation();


            window.veritasSecAbrirSeletor(
                tipo
            );
        };


    novo.onkeydown =
        function(evento){

            if (
                evento.key === "Enter"
                || evento.key === " "
            ) {

                evento.preventDefault();


                window.veritasSecAbrirSeletor(
                    tipo
                );
            }
        };


    return novo;
}


/* ============================================================
   INICIALIZAÇÃO IMEDIATA
   ============================================================ */

function instalar(){

    const projeto =
        recriarInput(
            "projetoPicker",
            "projeto"
        );


    const sarif =
        recriarInput(
            "sarifPicker",
            "sarif"
        );


    if (
        !projeto
        || !sarif
    ) {

        return;
    }


    const btnProjeto =
        byId(
            "btnSelecionarProjeto"
        );


    const btnSarif =
        byId(
            "btnSelecionarSarif"
        );


    if (
        btnProjeto
    ) {

        btnProjeto.style.display =
            "none";
    }


    if (
        btnSarif
    ) {

        btnSarif.style.display =
            "none";
    }


    byId(
        "vsFsDefFechar"
    ).onclick =
        fechar;


    byId(
        "vsFsDefCancelar"
    ).onclick =
        fechar;


    byId(
        "vsFsDefSubir"
    ).onclick =
        async function(){

            if (
                pastaPai
            ) {

                await carregar(
                    pastaPai
                );
            }
        };


    byId(
        "vsFsDefEscolherPasta"
    ).onclick =
        function(){

            if (
                tipoAtual !== "projeto"
                || !pastaAtual
            ) {

                return;
            }


            definirSelecao(
                "projeto",
                pastaAtual
            );


            fechar();
        };


    byId(
        "vsFsDefModal"
    ).onclick =
        function(evento){

            if (
                evento.target === this
            ) {

                fechar();
            }
        };
}


/*
 * Este script está no final do BODY.
 * Os inputs já existem neste momento.
 */
instalar();


/*
 * Caso alguma extensão anterior substitua novamente
 * os inputs após a carga, fazemos uma única reinstalação.
 */
window.addEventListener(
    "load",
    function(){

        setTimeout(
            instalar,
            1000
        );
    },
    {
        once:true
    }
);

})();
</script>

"""

    if "</body>" in html:

        return html.replace(
            "</body>",
            extensao + "\n</body>",
            1,
        )

    return html + extensao

pagina_interface = _vs_historico_pagina_interface_7


# ============================================================
# VERITASSEC_FS_EXTERNOS_HTML_20261019
# ============================================================

_pagina_interface_antes_assets_fs = pagina_interface


def _vs_historico_pagina_interface_8() -> str:

    html = _pagina_interface_antes_assets_fs()

    css = "<link " 'rel="stylesheet" ' 'href="/interface-assets/fs.css?v=20261019">'

    js = "<script " 'src="/interface-assets/fs.js?v=20261019" ' "defer></script>"

    if "/interface-assets/fs.css" not in html:

        if "</head>" in html:

            html = html.replace(
                "</head>",
                css + "\n</head>",
                1,
            )

        else:

            html = css + "\n" + html

    if "/interface-assets/fs.js" not in html:

        if "</body>" in html:

            html = html.replace(
                "</body>",
                js + "\n</body>",
                1,
            )

        else:

            html = html + "\n" + js

    return html

pagina_interface = _vs_historico_pagina_interface_8


# ============================================================
# VERITASSEC_BOTOES_SELECAO_FINAL_20261019
# ============================================================

_pagina_interface_antes_botoes_selecao = pagina_interface


def _vs_historico_pagina_interface_9() -> str:

    import re

    html = _pagina_interface_antes_botoes_selecao()

    # --------------------------------------------------------
    # PROJETO
    # --------------------------------------------------------

    if 'id="vsSelecionarDiretorioFinal"' not in html:

        html = re.sub(
            r'(<input\b[^>]*\bid="projetoPicker"[^>]*>)',
            r"""
<div class="vs-seletor-final">
\1

<button
    id="vsSelecionarDiretorioFinal"
    type="button"
    class="vs-botao-selecao-final"
>
    Selecionar Projeto
</button>

</div>
""",
            html,
            count=1,
            flags=re.IGNORECASE,
        )

    # --------------------------------------------------------
    # SARIF
    # --------------------------------------------------------

    if 'id="vsSelecionarSarifFinal"' not in html:

        html = re.sub(
            r'(<input\b[^>]*\bid="sarifPicker"[^>]*>)',
            r"""
<div class="vs-seletor-final">
\1

<button
    id="vsSelecionarSarifFinal"
    type="button"
    class="vs-botao-selecao-final"
>
    Selecionar SARIF
</button>

</div>
""",
            html,
            count=1,
            flags=re.IGNORECASE,
        )

    estilo = r"""

<style id="vsBotoesSelecaoFinalStyle">

.vs-seletor-final {

    display:grid;

    grid-template-columns:
        minmax(0, 1fr)
        auto;

    gap:
        8px;

    align-items:center;

    width:100%;
}


.vs-seletor-final input {

    width:100%;

    box-sizing:
        border-box;
}


.vs-botao-selecao-final {

    min-width:
        160px;

    height:
        32px;

    padding:
        0 14px;

    border:
        1px solid
        #9aa7b4;

    border-radius:
        4px;

    background:
        #f3f5f7;

    color:
        #202a33;

    cursor:
        pointer;

    white-space:
        nowrap;
}


.vs-botao-selecao-final:hover {

    background:
        #e6ebf0;

    border-color:
        #174ea6;
}


/*
 * Campos passam a ser somente apresentação do caminho.
 */
#projetoPicker,
#sarifPicker {

    cursor:
        default !important;

    caret-color:
        transparent !important;

    background:
        #ffffff !important;
}


/*
 * Oculta definitivamente os botões antigos.
 */
#btnSelecionarProjeto,
#btnSelecionarSarif {

    display:
        none !important;
}


@media(max-width:800px) {

    .vs-seletor-final {

        grid-template-columns:
            1fr;
    }


    .vs-botao-selecao-final {

        width:
            100%;
    }
}

</style>

"""

    if "vsBotoesSelecaoFinalStyle" not in html:

        if "</head>" in html:

            html = html.replace(
                "</head>",
                estilo + "\n</head>",
                1,
            )

        else:

            html = estilo + html

    return html

pagina_interface = _vs_historico_pagina_interface_9


# ============================================================
# VERITASSEC_SELETOR_INLINE_20261019
# ============================================================

_pagina_interface_antes_seletor_inline = pagina_interface


def _vs_historico_pagina_interface_10() -> str:

    import re

    from aplicacao.ui.interface_fs_assets import (
        _CSS,
        _JS,
    )

    html = _pagina_interface_antes_seletor_inline()

    # Remove a dependência dos assets externos.
    html = re.sub(
        r'<script\s+src="/interface-assets/fs\.js' r'[^"]*"[^>]*>\s*</script>',
        "",
        html,
        flags=re.IGNORECASE,
    )

    html = re.sub(
        r'<link\s+rel="stylesheet"\s+'
        r'href="/interface-assets/fs\.css'
        r'[^"]*"[^>]*>',
        "",
        html,
        flags=re.IGNORECASE,
    )

    css_inline = "\n<style " 'id="vsFsInlineCss">\n' + _CSS + "\n</style>\n"

    if 'id="vsFsInlineCss"' not in html:

        if "</head>" not in html:

            raise RuntimeError("tag </head> ausente")

        html = html.replace(
            "</head>",
            css_inline + "</head>",
            1,
        )

    js_inline = "\n<script " 'id="vsFsInlineScript">\n' + _JS + "\n</script>\n"

    if 'id="vsFsInlineScript"' not in html:

        if "</body>" not in html:

            raise RuntimeError("tag </body> ausente")

        html = html.replace(
            "</body>",
            js_inline + "</body>",
            1,
        )

    return html

pagina_interface = _vs_historico_pagina_interface_10


# ============================================================
# VERITASSEC_BOTOES_DIRETO_HTML_20261019
#
# Botões inseridos diretamente no HTML FINAL retornado pela
# página. Não são criados dinamicamente por JavaScript.
#
# Os inputs visíveis são identificados pelo respectivo label.
# ============================================================

_pagina_interface_antes_botoes_direto_html = pagina_interface


def _vs_historico_pagina_interface_11() -> str:

    import re

    html = _pagina_interface_antes_botoes_direto_html()

    if "VERITASSEC_BOTOES_DIRETO_HTML_RENDER_20261019" in html:

        return html

    # ========================================================
    # DIRETÓRIO DO PROJETO
    # ========================================================

    padrao_projeto = re.compile(
        r"("
        r"<label\b[^>]*>\s*"
        r"Diretório do projeto"
        r"\s*</label>\s*"
        r")"
        r"("
        r"<input\b[^>]*>"
        r")",
        re.IGNORECASE,
    )

    def substituir_projeto(match):

        label = match.group(1)
        campo = match.group(2)

        return (
            label
            + """
<div
    class="vs-html-seletor"
    data-vs-tipo="projeto"
>
"""
            + campo
            + """
    <button
        type="button"
        class="vs-html-seletor-botao"
        data-vs-acao="projeto"
        onclick="
            if (
                typeof window.veritasSecAbrirProjeto
                === 'function'
            ) {
                window.veritasSecAbrirProjeto();
            }
        "
    >
        Selecionar Projeto
    </button>
</div>
"""
        )

    html, qtd_projeto = padrao_projeto.subn(
        substituir_projeto,
        html,
    )

    # ========================================================
    # ARQUIVO SARIF
    # ========================================================

    padrao_sarif = re.compile(
        r"("
        r"<label\b[^>]*>\s*"
        r"Arquivo SARIF"
        r"\s*</label>\s*"
        r")"
        r"("
        r"<input\b[^>]*>"
        r")",
        re.IGNORECASE,
    )

    def substituir_sarif(match):

        label = match.group(1)
        campo = match.group(2)

        return (
            label
            + """
<div
    class="vs-html-seletor"
    data-vs-tipo="sarif"
>
"""
            + campo
            + """
    <button
        type="button"
        class="vs-html-seletor-botao"
        data-vs-acao="sarif"
        onclick="
            if (
                typeof window.veritasSecAbrirSarif
                === 'function'
            ) {
                window.veritasSecAbrirSarif();
            }
        "
    >
        Selecionar SARIF
    </button>
</div>
"""
        )

    html, qtd_sarif = padrao_sarif.subn(
        substituir_sarif,
        html,
    )

    if qtd_projeto < 1:

        raise RuntimeError("input visível do projeto não localizado")

    if qtd_sarif < 1:

        raise RuntimeError("input visível do SARIF não localizado")

    # ========================================================
    # CSS
    #
    # O grupo inteiro terá no máximo 720 px.
    # O botão ocupa 165 px.
    # O restante fica reservado para o input.
    # ========================================================

    estilo = r"""

<!-- VERITASSEC_BOTOES_DIRETO_HTML_RENDER_20261019 -->

<style id="vsBotoesDiretoHtmlCss">

.vs-html-seletor {

    display:
        grid !important;

    grid-template-columns:
        minmax(260px, 1fr)
        165px !important;

    column-gap:
        8px !important;

    align-items:
        center !important;

    width:
        100% !important;

    max-width:
        720px !important;

    min-width:
        0 !important;

    margin:
        0 !important;

    padding:
        0 !important;

    box-sizing:
        border-box !important;
}


.vs-html-seletor > input {

    display:
        block !important;

    width:
        100% !important;

    max-width:
        100% !important;

    min-width:
        0 !important;

    height:
        30px !important;

    margin:
        0 !important;

    box-sizing:
        border-box !important;
}


.vs-html-seletor-botao {

    display:
        flex !important;

    visibility:
        visible !important;

    opacity:
        1 !important;

    position:
        static !important;

    width:
        165px !important;

    min-width:
        165px !important;

    max-width:
        165px !important;

    height:
        30px !important;

    margin:
        0 !important;

    padding:
        0 10px !important;

    align-items:
        center !important;

    justify-content:
        center !important;

    border:
        1px solid #8d99a6 !important;

    border-radius:
        4px !important;

    background:
        #eef1f4 !important;

    color:
        #17212b !important;

    cursor:
        pointer !important;

    white-space:
        nowrap !important;

    box-sizing:
        border-box !important;
}


.vs-html-seletor-botao:hover {

    background:
        #dfe6ed !important;

    border-color:
        #174ea6 !important;
}


/*
 * Os botões experimentais anteriores não participam mais
 * da interface.
 */
#vsPersistSelecionarDiretorio,
#vsPersistSelecionarSarif,
#vsSelecionarDiretorioFinal,
#vsSelecionarSarifFinal,
#vsBaseSelecionarDiretorio,
#vsBaseSelecionarSarif,
#btnSelecionarProjeto,
#btnSelecionarSarif {

    display:
        none !important;
}


@media(max-width:800px) {

    .vs-html-seletor {

        max-width:
            100% !important;

        grid-template-columns:
            1fr !important;

        row-gap:
            6px !important;
    }


    .vs-html-seletor-botao {

        width:
            100% !important;

        min-width:
            0 !important;

        max-width:
            none !important;
    }
}

</style>

"""

    if "</head>" not in html:

        raise RuntimeError("tag </head> não localizada")

    html = html.replace(
        "</head>",
        estilo + "\n</head>",
        1,
    )

    # ========================================================
    # SINCRONIZA SOMENTE O VALOR DOS INPUTS VISÍVEIS.
    #
    # OS BOTÕES JÁ ESTÃO NO HTML.
    # ========================================================

    sincronizacao = r"""

<script id="vsBotoesDiretoHtmlSync">

(() => {

"use strict";


function sincronizar(
    tipo
) {

    const origem =
        document.getElementById(
            tipo === "projeto"
            ? "projetoPicker"
            : "sarifPicker"
        )
        ||
        document.getElementById(
            tipo === "projeto"
            ? "projeto"
            : "sarif"
        );


    if (
        !origem
        || !origem.value
    ) {

        return;
    }


    const wrappers =
        document.querySelectorAll(
            '.vs-html-seletor'
            + '[data-vs-tipo="'
            + tipo
            + '"]'
        );


    for (
        const wrapper
        of wrappers
    ) {

        const r =
            wrapper.getBoundingClientRect();


        /*
         * Só sincroniza a cópia realmente visível.
         */
        if (
            r.width <= 0
            || r.height <= 0
        ) {

            continue;
        }


        const input =
            wrapper.querySelector(
                "input"
            );


        if (
            input
            && input.value
                !== origem.value
        ) {

            input.value =
                origem.value;
        }
    }
}


setInterval(
    () => {

        sincronizar(
            "projeto"
        );

        sincronizar(
            "sarif"
        );
    },
    250
);


})();

</script>

"""

    if "</body>" not in html:

        raise RuntimeError("tag </body> não localizada")

    html = html.replace(
        "</body>",
        sincronizacao + "\n</body>",
        1,
    )

    # VERITASSEC_LAYOUT_CONSOLIDADO_20261019
    if '</head>' not in html:
        raise RuntimeError('HTML_HEAD_AUSENTE')
    html = html.replace('</head>', '<style id="vsLayoutConsolidado20261019">\n\n/* Ajustes de espaçamento e responsividade */\n\n.vs-base-seletor,\n.vs-html-seletor {\n    display: grid !important;\n    grid-template-columns:\n        minmax(0, 1fr)\n        minmax(155px, 180px) !important;\n    column-gap: 16px !important;\n    row-gap: 10px !important;\n    align-items: center !important;\n    width: 100% !important;\n    max-width: 100% !important;\n    min-width: 0 !important;\n    box-sizing: border-box !important;\n}\n\n.vs-base-seletor > input,\n.vs-html-seletor > input,\n.vs-base-seletor > select,\n.vs-html-seletor > select {\n    grid-column: 1 !important;\n    min-width: 0 !important;\n    width: 100% !important;\n    position: static !important;\n    margin: 0 !important;\n}\n\n.vs-base-seletor > button,\n.vs-html-seletor > button,\n.vs-base-botao-seletor,\n.vs-html-seletor-botao {\n    grid-column: 2 !important;\n    position: static !important;\n    width: 100% !important;\n    min-width: 0 !important;\n    margin: 0 !important;\n    transform: none !important;\n    white-space: normal !important;\n    box-sizing: border-box !important;\n}\n\ninput,\nselect,\ntextarea {\n    max-width: 100%;\n    min-width: 0;\n}\n\n.actions {\n    display: flex;\n    flex-wrap: wrap;\n    gap: 12px;\n}\n\ntable {\n    max-width: 100%;\n}\n\nth,\ntd {\n    overflow-wrap: anywhere;\n}\n\npre {\n    max-width: 100%;\n    overflow-x: auto;\n}\n\nimg,\ncanvas,\nsvg {\n    max-width: 100%;\n}\n\n@media (max-width: 760px) {\n    .vs-base-seletor,\n    .vs-html-seletor {\n        grid-template-columns: minmax(0, 1fr) !important;\n    }\n\n    .vs-base-seletor > input,\n    .vs-html-seletor > input,\n    .vs-base-seletor > select,\n    .vs-html-seletor > select,\n    .vs-base-seletor > button,\n    .vs-html-seletor > button,\n    .vs-base-botao-seletor,\n    .vs-html-seletor-botao {\n        grid-column: 1 !important;\n    }\n\n    .actions {\n        flex-direction: column;\n        align-items: stretch;\n    }\n}\n\n</style>\n' + '\n</head>', 1)
    # VERITASSEC_UX_ABAS_CORRECAO_20261020
    if '</head>' not in html or '</body>' not in html:
        raise RuntimeError('ESTRUTURA_HTML_INVALIDA')
    html = html.replace('</head>', '<style id="vsUxAbasCorrecao20261020">\n\n/*\n * VERITASSEC — CORRECAO DE ABAS\n *\n * O painel operacional sera movido para\n * a secao #analise pelo JavaScript.\n *\n * Os elementos originais continuam no DOM,\n * preservando os contratos existentes.\n */\n\n/* ==================================================\n   FORMULARIO ORIGINAL DUPLICADO\n   ================================================== */\n\n/*\n * O formulario operacional possui executar,\n * pausar, retomar e parar.\n *\n * O formulario basico permanece no DOM para\n * compatibilidade com o JavaScript existente.\n */\n\n#analise > .grid,\n#analise > .actions,\n#analise > #statusAnalise,\n#analise > #resultado {\n    display: none !important;\n}\n\n/*\n * Oculta somente o titulo do resultado basico\n * quando ele antecede o antigo bloco de saida.\n */\n\n#analise > h3:has(+ #resultado) {\n    display: none !important;\n}\n\n/* ==================================================\n   PAINEL OPERACIONAL\n   ================================================== */\n\n#analise {\n    min-width: 0;\n    width: 100%;\n    box-sizing: border-box;\n}\n\n#analise #veritassec-passo3-root {\n    display: block;\n    width: 100%;\n    max-width: 100%;\n    min-width: 0;\n    margin-top: 18px;\n    box-sizing: border-box;\n}\n\n#analise #veritassec-passo3-root .vs3-card {\n    width: 100%;\n    max-width: 100%;\n    min-width: 0;\n    box-sizing: border-box;\n}\n\n#analise #veritassec-passo3-root .vs3-grid {\n    display: grid;\n    grid-template-columns:\n        repeat(2, minmax(0, 1fr));\n    gap: 20px;\n    align-items: start;\n}\n\n#analise #veritassec-passo3-root .vs3-field {\n    min-width: 0;\n    width: 100%;\n}\n\n/* ==================================================\n   CAMPOS E BOTOES DE SELECAO\n   ================================================== */\n\n/*\n * O CSS anterior possuia regras conflitantes\n * para os seletores.\n *\n * Agora o campo ocupa o espaco flexivel\n * e o botao possui coluna independente.\n */\n\n#analise .vs-html-seletor,\n#analise .vs-base-seletor,\n#analise .vs-seletor-final {\n\n    display: grid !important;\n\n    grid-template-columns:\n        minmax(0, 1fr)\n        minmax(150px, 175px) !important;\n\n    column-gap: 18px !important;\n    row-gap: 10px !important;\n\n    align-items: center !important;\n\n    width: 100% !important;\n    max-width: 100% !important;\n    min-width: 0 !important;\n\n    padding: 0 !important;\n    margin: 6px 0 12px 0 !important;\n\n    box-sizing: border-box !important;\n}\n\n/* Inputs */\n\n#analise .vs-html-seletor > input,\n#analise .vs-html-seletor > select,\n#analise .vs-base-seletor > input,\n#analise .vs-base-seletor > select,\n#analise .vs-seletor-final > input,\n#analise .vs-seletor-final > select {\n\n    grid-column: 1 !important;\n    grid-row: 1 !important;\n\n    display: block !important;\n\n    position: static !important;\n\n    width: 100% !important;\n    max-width: 100% !important;\n    min-width: 0 !important;\n\n    height: 40px !important;\n    min-height: 40px !important;\n\n    margin: 0 !important;\n    padding: 8px 10px !important;\n\n    transform: none !important;\n\n    box-sizing: border-box !important;\n}\n\n/* Botoes */\n\n#analise .vs-html-seletor > button,\n#analise .vs-base-seletor > button,\n#analise .vs-seletor-final > button {\n\n    grid-column: 2 !important;\n    grid-row: 1 !important;\n\n    display: block !important;\n\n    position: static !important;\n\n    width: 100% !important;\n    max-width: 100% !important;\n    min-width: 0 !important;\n\n    height: 40px !important;\n    min-height: 40px !important;\n\n    margin: 0 !important;\n    padding: 7px 10px !important;\n\n    transform: none !important;\n\n    white-space: normal !important;\n\n    line-height: 1.25 !important;\n\n    box-sizing: border-box !important;\n}\n\n/* Botoes de execucao */\n\n#analise .vs3-actions {\n    display: flex;\n    flex-wrap: wrap;\n    gap: 12px;\n    margin-top: 14px;\n}\n\n#analise .vs3-actions button {\n    min-height: 40px;\n    padding: 8px 16px;\n}\n\n/* ==================================================\n   INVESTIGACAO MULTIAGENTE\n   ================================================== */\n\n#analise #agent-trace-panel {\n    width: 100%;\n    max-width: 100%;\n    min-width: 0;\n\n    margin-top: 20px;\n\n    box-sizing: border-box;\n}\n\n/* ==================================================\n   RESPONSIVIDADE\n   ================================================== */\n\n@media (max-width: 1000px) {\n\n    #analise #veritassec-passo3-root .vs3-grid {\n        grid-template-columns:\n            minmax(0, 1fr);\n    }\n\n}\n\n@media (max-width: 650px) {\n\n    #analise .vs-html-seletor,\n    #analise .vs-base-seletor,\n    #analise .vs-seletor-final {\n\n        grid-template-columns:\n            minmax(0, 1fr) !important;\n\n        row-gap: 10px !important;\n    }\n\n    #analise .vs-html-seletor > input,\n    #analise .vs-html-seletor > select,\n    #analise .vs-base-seletor > input,\n    #analise .vs-base-seletor > select,\n    #analise .vs-seletor-final > input,\n    #analise .vs-seletor-final > select {\n\n        grid-column: 1 !important;\n        grid-row: 1 !important;\n    }\n\n    #analise .vs-html-seletor > button,\n    #analise .vs-base-seletor > button,\n    #analise .vs-seletor-final > button {\n\n        grid-column: 1 !important;\n        grid-row: 2 !important;\n    }\n\n    #analise .vs3-actions {\n        flex-direction: column;\n        align-items: stretch;\n    }\n\n    #analise .vs3-actions button {\n        width: 100%;\n    }\n\n}\n\n</style>\n' + '\n</head>', 1)
    html = html.replace('</body>', '<script id="vsUxAbasScript20261020">\n\n(function () {\n\n    "use strict";\n\n    /*\n     * O painel operacional atualmente e inserido\n     * fora das secoes controladas pelas abas.\n     *\n     * Movemos o elemento original.\n     *\n     * Nao clonamos componentes.\n     * Nao recriamos botoes.\n     * Nao substituimos eventos existentes.\n     */\n\n    function corrigirEstrutura() {\n\n        const analise =\n            document.getElementById("analise");\n\n        const operacional =\n            document.getElementById(\n                "veritassec-passo3-root"\n            );\n\n        const investigacao =\n            document.getElementById(\n                "agent-trace-panel"\n            );\n\n        if (!analise || !operacional) {\n\n            console.error(\n                "VeritasSec: painel de analise ausente."\n            );\n\n            return;\n        }\n\n        /*\n         * Operacao da analise pertence somente\n         * a aba Analise.\n         */\n\n        if (operacional.parentElement !== analise) {\n\n            analise.appendChild(operacional);\n        }\n\n        /*\n         * Investigacao multiagente tambem pertence\n         * ao contexto da analise.\n         */\n\n        if (\n            investigacao\n            && investigacao.parentElement !== analise\n        ) {\n\n            analise.appendChild(investigacao);\n        }\n\n        /*\n         * Verificacao da estrutura apos o ajuste.\n         */\n\n        const operacaoCorreta =\n            analise.contains(operacional);\n\n        const investigacaoCorreta =\n            !investigacao\n            || analise.contains(investigacao);\n\n        if (\n            !operacaoCorreta\n            || !investigacaoCorreta\n        ) {\n\n            console.error(\n                "VeritasSec: estrutura das abas invalida."\n            );\n\n            return;\n        }\n\n        document.documentElement.setAttribute(\n            "data-vs-ux-abas",\n            "corrigidas"\n        );\n\n        console.info(\n            "VeritasSec: operacao restrita a aba Analise."\n        );\n    }\n\n    if (document.readyState === "loading") {\n\n        document.addEventListener(\n            "DOMContentLoaded",\n            corrigirEstrutura,\n            { once: true }\n        );\n\n    } else {\n\n        corrigirEstrutura();\n    }\n\n})();\n\n</script>\n' + '\n</body>', 1)
    # VERITASSEC_EXPORTACAO_DESTINO_UI_20261020
    if 'id="vs4ExportarFinal"' not in html:
        raise RuntimeError('EXPORTADOR_AUSENTE')
    html = html.replace('<div class="vs3-actions">\n<button\n    id="vs4ExportarFinal"', '<div\n    id="vsExportacaoDestino20261020"\n    style="margin:18px 0;padding:16px;border:1px solid #d5deea;border-radius:9px"\n>\n    <div style="font-weight:600;margin-bottom:10px">\n        Destino dos documentos\n    </div>\n\n    <div\n        style="display:grid;grid-template-columns:minmax(0,1fr) 180px;gap:12px"\n    >\n        <input\n            id="vsExportacaoPasta"\n            type="text"\n            placeholder="Selecione uma pasta dentro do diretório pessoal"\n            readonly\n            style="width:100%;min-width:0;padding:10px"\n        >\n\n        <button\n            id="vsExportacaoEscolherPasta"\n            type="button"\n        >\n            Escolher diretório\n        </button>\n    </div>\n\n    <p style="font-size:12px;color:#526276;margin:10px 0 0">\n        Salvar na pasta selecionada ou baixar um pacote ZIP.\n    </p>\n</div>\n\n<div\n    id="vsExportacaoSeletorPasta"\n    hidden\n    style="padding:16px;border:1px solid #d5deea;border-radius:9px;margin:12px 0"\n>\n    <strong>Selecionar diretório</strong>\n\n    <div\n        id="vsExportacaoPastaAtual"\n        style="margin:10px 0;overflow-wrap:anywhere"\n    ></div>\n\n    <button\n        id="vsExportacaoVoltarPasta"\n        type="button"\n    >\n        Pasta anterior\n    </button>\n\n    <div\n        id="vsExportacaoListaPastas"\n        style="display:grid;gap:6px;margin:12px 0"\n    ></div>\n\n    <button\n        id="vsExportacaoConfirmarPasta"\n        type="button"\n    >\n        Usar esta pasta\n    </button>\n\n    <button\n        id="vsExportacaoCancelarPasta"\n        type="button"\n    >\n        Cancelar\n    </button>\n</div>\n\n<div style="display:flex;flex-wrap:wrap;gap:12px;margin:12px 0">\n    <button id="vsExportacaoSalvarPasta" type="button">\n        Salvar na pasta selecionada\n    </button>\n\n    <button id="vsExportacaoBaixarZip" type="button">\n        Baixar ZIP\n    </button>\n</div>\n' + '\n<div class="vs3-actions">\n<button\n    id="vs4ExportarFinal"', 1)
    html = html.replace('</body>', '<script id="vsExportacaoDestinoScript20261020">\n(function(){\n"use strict";\n\nconst el = id => document.getElementById(id);\n\nlet pastaAtual = null;\nlet pastaPai = null;\n\nfunction formatosSelecionados(){\n    const lista = [];\n\n    if(el("vs4FormatoDocx")?.checked){\n        lista.push("DOCX");\n    }\n\n    if(el("vs4FormatoCsv")?.checked){\n        lista.push("CSV");\n    }\n\n    return lista;\n}\n\nfunction exigirFormatos(){\n    const lista = formatosSelecionados();\n\n    if(!lista.length){\n        throw new Error(\n            "Selecione DOCX, CSV ou ambos."\n        );\n    }\n\n    return lista;\n}\n\nfunction exigirExecucao(){\n    const id = window.veritasSecJobId;\n\n    if(!id){\n        throw new Error(\n            "Nenhuma execução selecionada."\n        );\n    }\n\n    return String(id);\n}\n\nasync function respostaJson(resposta){\n    const dados = await resposta.json();\n\n    if(!resposta.ok){\n        throw new Error(\n            dados?.detail || ("HTTP " + resposta.status)\n        );\n    }\n\n    return dados;\n}\n\nfunction mensagem(texto){\n    const status = el("vs4Status");\n\n    if(status){\n        status.textContent = texto;\n    }\n}\n\nasync function listarPasta(caminho){\n    const url = new URL(\n        "/api/interface/fs",\n        window.location.origin\n    );\n\n    url.searchParams.set("tipo", "diretorio");\n\n    if(caminho){\n        url.searchParams.set("path", caminho);\n    }\n\n    const resposta = await fetch(\n        url.toString(),\n        {cache:"no-store"}\n    );\n\n    const dados = await respostaJson(resposta);\n\n    pastaAtual = dados.atual;\n    pastaPai = dados.pai;\n\n    el("vsExportacaoPastaAtual").textContent =\n        pastaAtual;\n\n    const lista = el("vsExportacaoListaPastas");\n\n    lista.replaceChildren();\n\n    for(const item of dados.itens || []){\n        if(item.tipo !== "diretorio"){\n            continue;\n        }\n\n        const botao = document.createElement("button");\n\n        botao.type = "button";\n        botao.textContent = "📁 " + item.nome;\n        botao.style.textAlign = "left";\n        botao.style.padding = "9px";\n\n        botao.addEventListener("click", ()=>{\n            listarPasta(item.caminho).catch(\n                erro => mensagem("Erro: " + erro.message)\n            );\n        });\n\n        lista.appendChild(botao);\n    }\n\n    el("vsExportacaoVoltarPasta").disabled =\n        !pastaPai;\n}\n\nasync function salvarNaPasta(){\n    try{\n        const formatos = exigirFormatos();\n        const jobId = exigirExecucao();\n        const destino = el("vsExportacaoPasta").value.trim();\n\n        if(!destino){\n            throw new Error(\n                "Escolha primeiro o diretório de destino."\n            );\n        }\n\n        mensagem("Gerando documentos...");\n\n        const resposta = await fetch(\n            "/api/interface/execucao/"\n            + encodeURIComponent(jobId)\n            + "/exportar",\n            {\n                method:"POST",\n                headers:{\n                    "Content-Type":"application/json"\n                },\n                body:JSON.stringify({\n                    formatos,\n                    destino_pasta:destino\n                })\n            }\n        );\n\n        const dados = await respostaJson(resposta);\n\n        mensagem(\n            "Documentos salvos em: " + dados.diretorio\n        );\n\n        el("vs4Manifesto").textContent =\n            JSON.stringify(dados.manifesto,null,2);\n\n    }catch(erro){\n        mensagem("Erro: " + erro.message);\n    }\n}\n\nasync function baixarZip(){\n    try{\n        const formatos = exigirFormatos();\n        const jobId = exigirExecucao();\n\n        mensagem("Preparando pacote ZIP...");\n\n        const resposta = await fetch(\n            "/api/interface/execucao/"\n            + encodeURIComponent(jobId)\n            + "/exportar-zip",\n            {\n                method:"POST",\n                headers:{\n                    "Content-Type":"application/json"\n                },\n                body:JSON.stringify({formatos})\n            }\n        );\n\n        if(!resposta.ok){\n            await respostaJson(resposta);\n        }\n\n        const arquivo = await resposta.blob();\n\n        const url = URL.createObjectURL(arquivo);\n        const link = document.createElement("a");\n\n        link.href = url;\n        link.download =\n            "veritassec-resultados-"\n            + jobId.slice(0,16)\n            + ".zip";\n\n        document.body.appendChild(link);\n        link.click();\n        link.remove();\n\n        setTimeout(\n            ()=>URL.revokeObjectURL(url),\n            60000\n        );\n\n        mensagem(\n            "Download ZIP solicitado ao navegador."\n        );\n\n    }catch(erro){\n        mensagem("Erro: " + erro.message);\n    }\n}\n\nfunction iniciar(){\n    const escolher = el("vsExportacaoEscolherPasta");\n    const seletor = el("vsExportacaoSeletorPasta");\n\n    if(!escolher || !seletor){\n        return;\n    }\n\n    // O botão anterior fica oculto, mas preservado\n    // para compatibilidade com eventos existentes.\n    const anterior = el("vs4ExportarFinal");\n\n    if(anterior){\n        anterior.hidden = true;\n        anterior.style.display = "none";\n    }\n\n    escolher.addEventListener("click", async ()=>{\n        seletor.hidden = false;\n\n        try{\n            await listarPasta(\n                el("vsExportacaoPasta").value || null\n            );\n        }catch(erro){\n            mensagem("Erro: " + erro.message);\n        }\n    });\n\n    el("vsExportacaoVoltarPasta").addEventListener(\n        "click",\n        ()=>{\n            if(pastaPai){\n                listarPasta(pastaPai).catch(\n                    erro => mensagem(\n                        "Erro: " + erro.message\n                    )\n                );\n            }\n        }\n    );\n\n    el("vsExportacaoConfirmarPasta").addEventListener(\n        "click",\n        ()=>{\n            if(!pastaAtual){\n                return;\n            }\n\n            el("vsExportacaoPasta").value = pastaAtual;\n            seletor.hidden = true;\n        }\n    );\n\n    el("vsExportacaoCancelarPasta").addEventListener(\n        "click",\n        ()=>{\n            seletor.hidden = true;\n        }\n    );\n\n    el("vsExportacaoSalvarPasta").addEventListener(\n        "click",\n        salvarNaPasta\n    );\n\n    el("vsExportacaoBaixarZip").addEventListener(\n        "click",\n        baixarZip\n    );\n}\n\nif(document.readyState === "loading"){\n    document.addEventListener(\n        "DOMContentLoaded",\n        iniciar,\n        {once:true}\n    );\n}else{\n    iniciar();\n}\n})();\n</script>\n' + '\n</body>', 1)
    return html

pagina_interface = _vs_historico_pagina_interface_11


# VERITASSEC_STATUS_RESPONSIVO_20261023
_pagina_interface_antes_status_responsivo = pagina_interface


def pagina_interface() -> str:
    html = _pagina_interface_antes_status_responsivo()

    if "vsStatusResponsivo20261023" in html:
        return html

    if "</head>" not in html:
        raise RuntimeError("HTML_HEAD_AUSENTE")

    css = """
<style id="vsStatusResponsivo20261023">

/* Seis indicadores, sem sobreposicao */

#veritassec-passo3-root .vs3-status-grid {
    display: grid !important;
    grid-template-columns:
        repeat(3, minmax(0, 1fr)) !important;
    gap: 12px !important;
    width: 100% !important;
    min-width: 0 !important;
}

/* Cada cartao respeita seu proprio limite */

#veritassec-passo3-root .vs3-kpi {
    min-width: 0 !important;
    max-width: 100% !important;
    width: auto !important;
    overflow: hidden !important;
    box-sizing: border-box !important;
    padding: 12px !important;
}

/* Textos longos nao invadem o cartao seguinte */

#veritassec-passo3-root .vs3-kpi > div {
    display: block !important;
    min-width: 0 !important;
    max-width: 100% !important;
    white-space: normal !important;
    overflow-wrap: anywhere !important;
    word-break: break-word !important;
    line-height: 1.35 !important;
}

/* Identificador completo preservado */

#vs3Achado {
    overflow-wrap: anywhere !important;
    word-break: break-all !important;
    font-size: 0.92rem !important;
}

/* Monitor grande */

@media (min-width: 1600px) {
    #veritassec-passo3-root .vs3-status-grid {
        grid-template-columns:
            repeat(6, minmax(0, 1fr)) !important;
    }
}

/* Tablet */

@media (max-width: 850px) {
    #veritassec-passo3-root .vs3-status-grid {
        grid-template-columns:
            repeat(2, minmax(0, 1fr)) !important;
    }
}

/* Celular */

@media (max-width: 480px) {
    #veritassec-passo3-root .vs3-status-grid {
        grid-template-columns:
            minmax(0, 1fr) !important;
    }
}

</style>
"""

    return html.replace(
        "</head>",
        css + "</head>",
        1,
    )


# VERITASSEC_DAST_UI_INTEGRACAO_20261101
_vs_interface_anterior_dast = pagina_interface

def _vs_pagina_interface_dast() -> str:
    html = _vs_interface_anterior_dast()
    if 'id="vsDastUrlBase"' in html:
        return html
    if '</body>' not in html:
        raise RuntimeError('HTML_BODY_AUSENTE')
    trecho = r"""
<section id="vsDastConfig" style="margin:16px 0;padding:16px;border:1px solid #b7c7d9;border-radius:8px">
 <h3>Validação dinâmica (DAST)</h3>
 <label for="vsDastUrlBase" style="display:block;margin-top:12px">URL base da aplicação em execução</label>
 <input type="url" id="vsDastUrlBase" placeholder="http://127.0.0.1:3000" style="width:100%;box-sizing:border-box;padding:10px">
</section>
<script id="vsDastScript">
(function(){
 const fetchOriginal = window.fetch.bind(window);
 window.fetch = function(input, init){
   const path = typeof input === 'string' ? input : (input && input.url || '');
   if (path.includes('/api/interface/analisar') && !path.includes('/status/') && init && String(init.method||'GET').toUpperCase()==='POST' && typeof init.body==='string') {
     try {
       const dados=JSON.parse(init.body);
       if(dados && typeof dados==='object' && !Array.isArray(dados)) {
         const habilitado=true;
         dados.dast_habilitado=habilitado;
         dados.dast_url_base=document.getElementById('vsDastUrlBase')?.value.trim() || null;
         dados.dast={
           habilitado: habilitado,
           url_base: dados.dast_url_base
         };
         init={...init,body:JSON.stringify(dados)};
       }
     } catch(_) {}
   }
   return fetchOriginal(input,init);
 };
})();
</script>
"""
    return html.replace('</body>', trecho+'\n</body>', 1)

# Alias publico preservado apos consolidacao da composicao DAST.
pagina_interface = _vs_pagina_interface_dast
