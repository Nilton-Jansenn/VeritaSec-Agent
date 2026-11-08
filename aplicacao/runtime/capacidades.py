from __future__ import annotations

from .configuracao import (
    carregar_configuracao_runtime,
)


def obter_capacidades() -> dict:
    cfg = carregar_configuracao_runtime()

    return {
        "modo": cfg.modo,
        "pipeline": {
            "sarif": True,
            "investigacao": True,
            "selecao_automatica": True,
            "path_traversal": True,
            "autorizacao_http": True,
            "busca_evolucionaria": True,
            "persistencia": True,
            "pacote_veredito": True,
            "relatorio": True,
        },
        "llm": {
            "habilitada": cfg.ia_habilitada,
            "provedor_configurado": (
                cfg.provedor_llm is not None
            ),
            "modelo_configurado": (
                cfg.modelo_llm is not None
            ),
        },
        "zap": {
            "habilitado": cfg.zap_habilitado,
            "url": cfg.zap_url,
            "active_scan_automatico": False,
        },
        "rede": {
            "publica": cfg.permitir_rede_publica,
            "privada": cfg.permitir_rede_privada,
            "loopback": True,
        },
        "metodologia": {
            "llm_sozinha_confirma": False,
            "sast_sozinho_confirma": False,
            "confirmacao_exige_dinamica": True,
            "confirmacao_exige_oraculo": True,
            "ground_truth_inventado": False,
        },
    }
