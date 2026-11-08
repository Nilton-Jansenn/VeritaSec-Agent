from __future__ import annotations

import hashlib
import json

from typing import Any


def normalizar_alerta_zap(
    alerta: dict[str, Any],
) -> dict[str, Any]:

    dados = {
        "plugin_id":
            alerta.get("pluginId"),

        "alerta":
            alerta.get("alert"),

        "risco":
            alerta.get("risk"),

        "confianca":
            alerta.get("confidence"),

        "url":
            alerta.get("url"),

        "metodo":
            alerta.get("method"),

        "parametro":
            alerta.get("param"),

        "ataque":
            alerta.get("attack"),

        "evidencia":
            alerta.get("evidence"),

        "descricao":
            alerta.get("description"),

        "solucao":
            alerta.get("solution"),

        "referencia":
            alerta.get("reference"),
    }

    bruto = json.dumps(
        dados,
        ensure_ascii=False,
        sort_keys=True,
        default=str,
    )

    return {
        "tipo":
            "EVIDENCIA_DAST_ZAP",

        "fonte":
            "OWASP_ZAP",

        "hash_sha256":
            hashlib.sha256(
                bruto.encode("utf-8")
            ).hexdigest(),

        "dados":
            dados,

        "autoridade_decisoria":
            False,

        "regra":
            (
                "alerta_zap_e_evidencia;"
                "nao_e_veredito"
            ),
    }
