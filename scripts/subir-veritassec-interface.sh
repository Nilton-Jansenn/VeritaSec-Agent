#!/usr/bin/env bash
set -Eeuo pipefail

PROJ="$HOME/Documentos/Projetos/VeritasSec-Agent"

cd "$PROJ"

source .venv/bin/activate

if [[ -f "$PROJ/.veritassec-runtime-local.env" ]]; then
    set -a
    source "$PROJ/.veritassec-runtime-local.env"
    set +a
fi

echo "============================================================"
echo "VERITASSEC-AGENT"
echo "RUNTIME_LOCAL=${VERITASSEC_RUNTIME_LOCAL:-false}"
echo "RUNTIME_TARGET=${VERITASSEC_RUNTIME_LOCAL_BASE_URL:-ausente}"
echo "OWASP_ZAP=${VERITASSEC_ZAP_HABILITADO:-false}"
echo "OWASP_ZAP_URL=${VERITASSEC_ZAP_URL:-ausente}"
echo "============================================================"

if [[ -f "$PROJ/.veritassec-zap-key.env" ]]; then
    set -a
    source "$PROJ/.veritassec-zap-key.env"
    set +a
fi
# Gerenciamento opt-in do ZAP existente; sem criar ou reconfigurar contêiner.
if [[ "${VERITASSEC_ZAP_HABILITADO:-false}" == "true" ]] && command -v docker >/dev/null 2>&1; then
    if docker container inspect veritassec-zap-local >/dev/null 2>&1; then
        if [[ "$(docker inspect -f '{{.State.Running}}' veritassec-zap-local 2>/dev/null)" != "true" ]]; then
            if ! docker start veritassec-zap-local; then
                echo 'AVISO=ZAP_NAO_INICIADO_DAST_INDISPONIVEL' >&2
            fi
        fi
    else
        echo 'AVISO=CONTAINER_ZAP_NAO_ENCONTRADO' >&2
    fi
fi
exec python -m uvicorn \
    aplicacao.main:app \
    --host 127.0.0.1 \
    --port 8083
