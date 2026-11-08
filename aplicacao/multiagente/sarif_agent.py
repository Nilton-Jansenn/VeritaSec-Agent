from __future__ import annotations

from .perfil_runtime_local import (
    obter_perfil_runtime_local,
)


import hashlib
import json
from pathlib import Path
from typing import Any


def _texto_mensagem(
    resultado: dict[str, Any],
) -> str:
    mensagem = resultado.get(
        "message",
        {},
    )

    if isinstance(mensagem, dict):
        return str(
            mensagem.get(
                "text",
                "",
            )
        )

    return str(mensagem or "")


def _carregar_achados_sarif_base_integral(
    sarif_path: str,
    projeto_path: str,
) -> list[dict[str, Any]]:
    """
    Converte resultados SARIF em achados canônicos
    consumíveis pelo pipeline multiagente.

    Não inventa CWE nem localização.
    """
    sarif = Path(
        sarif_path
    ).expanduser().resolve()

    projeto = Path(
        projeto_path
    ).expanduser().resolve()


    perfil_runtime = (
        obter_perfil_runtime_local(
            str(projeto)
        )
    )

    if not sarif.is_file():
        raise FileNotFoundError(
            f"SARIF inexistente: {sarif}"
        )

    if not projeto.is_dir():
        raise NotADirectoryError(
            f"Projeto inexistente: {projeto}"
        )

    documento = json.loads(
        sarif.read_text(
            encoding="utf-8",
        )
    )

    achados: list[
        dict[str, Any]
    ] = []

    for run_idx, run in enumerate(
        documento.get(
            "runs",
            [],
        )
    ):
        for idx, resultado in enumerate(
            run.get(
                "results",
                [],
            )
        ):
            locations = resultado.get(
                "locations",
                [],
            )

            if not locations:
                continue

            physical = (
                locations[0]
                .get(
                    "physicalLocation",
                    {},
                )
            )

            artifact = physical.get(
                "artifactLocation",
                {},
            )

            uri = str(
                artifact.get(
                    "uri",
                    "",
                )
            )

            region = physical.get(
                "region",
                {},
            )

            linha = region.get(
                "startLine"
            )

            if not uri:
                continue

            # SARIF usa caminhos relativos ao projeto.
            arquivo = (
                projeto
                / uri
            ).resolve()

            try:
                arquivo.relative_to(
                    projeto
                )
            except ValueError:
                # Fail closed contra traversal vindo do SARIF.
                continue

            regra = str(
                resultado.get(
                    "ruleId",
                    ""
                )
            )

            mensagem = _texto_mensagem(
                resultado
            )

            material = (
                f"{run_idx}|{idx}|"
                f"{regra}|{uri}|{linha}|"
                f"{mensagem}"
            ).encode(
                "utf-8",
                errors="replace",
            )

            fingerprint = hashlib.sha256(
                material
            ).hexdigest()

            achados.append({
                "id": (
                    "sarif:"
                    + fingerprint[:20]
                ),
                "regra": regra,
                "arquivo": str(
                    arquivo
                ),
                "linha": linha,
                "mensagem": mensagem,
                "fingerprint": fingerprint,
                "uri_sarif": uri,
                "run_index": run_idx,
                "result_index": idx,
                "execucao_dinamica_permitida":
                    bool(
                        perfil_runtime.habilitado
                    ),
                "base_url_http":
                    perfil_runtime.base_url,
                "caminho_http": None,
                "marcador_recurso": None,
                "metadados": {
                    "origem": "sarif",
                    "runtime_local_autorizado":
                        bool(
                            perfil_runtime.habilitado
                        ),
                    "runtime_local_base_url":
                        perfil_runtime.base_url,
                    "runtime_local_motivo":
                        perfil_runtime.motivo,
                    "sarif": str(sarif),
                    "projeto": str(projeto),
                    "fingerprint": fingerprint,
                    "uri_sarif": uri,
                    "run_index": run_idx,
                    "result_index": idx,
                },
            })

    return achados


def selecionar_achado(
    achados: list[dict[str, Any]],
    *,
    indice: int | None = None,
    achado_id: str | None = None,
) -> dict[str, Any]:

    if achado_id:
        for achado in achados:
            if achado["id"] == achado_id:
                return achado

        raise KeyError(
            f"achado não encontrado: {achado_id}"
        )

    if indice is None:
        indice = 0

    if indice < 0 or indice >= len(
        achados
    ):
        raise IndexError(
            f"índice inválido: {indice}"
        )

    return achados[indice]


from .resolvedor_endpoints import (
    enriquecer_achado_endpoint,
)


def carregar_achados_sarif(
    sarif_path: str,
    projeto_path: str,
):
    achados = (
        _carregar_achados_sarif_base_integral(
            sarif_path,
            projeto_path,
        )
    )

    return [
        enriquecer_achado_endpoint(
            achado,
            projeto=projeto_path,
        )
        for achado in achados
    ]
