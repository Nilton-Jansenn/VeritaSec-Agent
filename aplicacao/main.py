from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from aplicacao.api.interface_agent import (
    baixar_output,
    carregar_chave,
    executar_analise,
    interface_html,
    listar_inputs,
    listar_outputs,
    obter_config,
    obter_status_ia_seguro,
    remover_chave,
    salvar_config,
    testar_conexao,
)
from aplicacao.multiagente.api import roteador_multiagente
from aplicacao.nucleo.registro_logs import configurar_logs


configurar_logs()

app = FastAPI(
    title="VeritasSec-Agent",
    version="1.0.0",
    description=(
        "Sistema multiagente para investigação controlada "
        "de achados de segurança orientada a evidências."
    ),
)


@app.get("/")
def inicio() -> dict[str, str]:
    return {
        "aplicacao": "VeritasSec-Agent",
        "arquitetura": "multiagente",
        "status": "ativo",
        "interface": "/interface",
        "documentacao": "/docs",
    }


app.include_router(roteador_multiagente)

app.add_api_route(
    "/interface",
    interface_html,
    methods=["GET"],
    response_class=HTMLResponse,
    tags=["interface"],
)

app.add_api_route(
    "/api/interface/config",
    obter_config,
    methods=["GET"],
    tags=["interface"],
)

app.add_api_route(
    "/api/interface/config",
    salvar_config,
    methods=["PUT"],
    tags=["interface"],
)

app.add_api_route(
    "/api/interface/api-key",
    carregar_chave,
    methods=["POST"],
    tags=["interface"],
)

app.add_api_route(
    "/api/interface/api-key/{provedor}",
    remover_chave,
    methods=["DELETE"],
    tags=["interface"],
)

app.add_api_route(
    "/api/interface/test-connection",
    testar_conexao,
    methods=["POST"],
    tags=["interface"],
)

app.add_api_route(
    "/api/interface/inputs",
    listar_inputs,
    methods=["GET"],
    tags=["interface"],
)

app.add_api_route(
    "/api/interface/analisar",
    executar_analise,
    methods=["POST"],
    tags=["interface"],
)

app.add_api_route(
    "/api/interface/outputs",
    listar_outputs,
    methods=["GET"],
    tags=["interface"],
)

app.add_api_route(
    "/api/interface/download/{caminho:path}",
    baixar_output,
    methods=["GET"],
    tags=["interface"],
)

app.add_api_route(
    "/api/interface/status-ia",
    obter_status_ia_seguro,
    methods=["GET"],
    tags=["interface"],
)


# VERITASSEC_INTERFACE_JOB_STATUS
from aplicacao.api.interface_agent import (
    obter_status_analise,
)

app.add_api_route(
    "/api/interface/analisar/status/{job_id}",
    obter_status_analise,
    methods=["GET"],
    tags=["interface"],
)


# ============================================================
# VERITASSEC_PASSO2_ROTAS_CONTROLE
#
# Não existe uma segunda rota de análise.
# Estas rotas apenas controlam uma execução iniciada por:
#
# POST /api/interface/analisar
# ============================================================

from aplicacao.api.interface_agent import (
    pausar_analise,
    parar_analise,
    retomar_analise,
)


app.add_api_route(
    "/api/interface/execucao/{job_id}/pausar",
    pausar_analise,
    methods=["POST"],
    tags=["interface"],
)


app.add_api_route(
    "/api/interface/execucao/{job_id}/retomar",
    retomar_analise,
    methods=["POST"],
    tags=["interface"],
)


app.add_api_route(
    "/api/interface/execucao/{job_id}/parar",
    parar_analise,
    methods=["POST"],
    tags=["interface"],
)


# ============================================================
# VERITASSEC_PASSO3_ROTA_RESULTADOS
# ============================================================

from aplicacao.api.interface_agent import (
    obter_resultados_operacionais,
)


app.add_api_route(
    "/api/interface/execucao/{job_id}/resultados",
    obter_resultados_operacionais,
    methods=["GET"],
    tags=["interface"],
)


# ============================================================
# VERITASSEC_PASSO4_136_ROTA_EXPORTACAO
# ============================================================

from aplicacao.api.interface_agent import (
    exportar_execucao_final_136,
)

app.add_api_route(
    "/api/interface/execucao/{job_id}/exportar",
    exportar_execucao_final_136,
    methods=["POST"],
    tags=["interface"],
)


# ============================================================
# VERITASSEC_CORRECAO_INTERFACE_ROTAS_FS_MULTIMODELO
# ============================================================

from aplicacao.api.interface_agent import (
    listar_sistema_arquivos,
    obter_config_multimodelo,
    salvar_config_multimodelo,
)


app.add_api_route(
    "/api/interface/fs",
    listar_sistema_arquivos,
    methods=["GET"],
    tags=["interface"],
)


app.add_api_route(
    "/api/interface/config-multimodelo",
    obter_config_multimodelo,
    methods=["GET"],
    tags=["interface"],
)


app.add_api_route(
    "/api/interface/config-multimodelo",
    salvar_config_multimodelo,
    methods=["POST"],
    tags=["interface"],
)


# ============================================================
# VERITASSEC_FS_ASSETS_EXTERNOS_20261019
# ============================================================

from aplicacao.ui.interface_fs_assets import (
    interface_fs_css,
    interface_fs_javascript,
)


app.add_api_route(
    "/interface-assets/fs.js",
    interface_fs_javascript,
    methods=["GET"],
    include_in_schema=False,
)


app.add_api_route(
    "/interface-assets/fs.css",
    interface_fs_css,
    methods=["GET"],
    include_in_schema=False,
)


# ============================================================
# VERITASSEC_BROWSER_PROBE_20261019
# Diagnóstico temporário do JavaScript da interface.
# ============================================================

from aplicacao.ui.interface_browser_probe import (
    limpar_browser_probe,
    ler_browser_probe,
    registrar_browser_probe,
)


app.add_api_route(
    "/api/interface/browser-probe",
    registrar_browser_probe,
    methods=["GET"],
    include_in_schema=False,
)


app.add_api_route(
    "/api/interface/browser-probe/log",
    ler_browser_probe,
    methods=["GET"],
    include_in_schema=False,
)


app.add_api_route(
    "/api/interface/browser-probe/limpar",
    limpar_browser_probe,
    methods=["POST"],
    include_in_schema=False,
)


# VERITASSEC_EXPORTACAO_ZIP_ROTA_20261020
from aplicacao.api.interface_agent import (
    baixar_exportacao_zip_20261020,
)

app.add_api_route(
    "/api/interface/execucao/{job_id}/exportar-zip",
    baixar_exportacao_zip_20261020,
    methods=["POST"],
    tags=["interface"],
)
