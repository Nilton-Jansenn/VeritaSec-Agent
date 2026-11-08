from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import json
import os
from pathlib import Path
from threading import Condition, RLock, Thread
from typing import Any
from uuid import uuid4

from .pipeline_agent import (
    executar_pipeline_agent,
)

from .sarif_agent import (
    carregar_achados_sarif,
    selecionar_achado,
)

from .telemetria_execucao import (
    registrar_emissor,
    vincular_execucao,
    vincular_achado,
)


ESTADOS_FINAIS = {
    "CONCLUIDO",
    "INTERROMPIDO",
    "ERRO",
}


_lock = RLock()
_cond = Condition(_lock)

_jobs: dict[
    str,
    dict[str, Any],
] = {}


def agora() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


def _raiz_execucoes() -> Path:

    configurada = os.getenv(
        "VERITASSEC_SAIDAS_DIR",
        "",
    ).strip()

    if configurada:
        raiz = (
            Path(configurada)
            .expanduser()
            .resolve()
        )
    else:
        raiz = (
            Path.home()
            / "Documentos"
            / "Projetos"
            / "VeritasSec-Agent-Saidas"
        ).resolve()

    destino = (
        raiz
        / "execucoes-operacionais"
    )

    destino.mkdir(
        parents=True,
        exist_ok=True,
    )

    return destino


def _validar_projeto(
    valor: Any,
) -> Path:

    if not isinstance(
        valor,
        str,
    ):
        raise ValueError(
            "projeto_path deve ser texto"
        )

    valor = valor.strip()

    if (
        not valor
        or "\x00" in valor
    ):
        raise ValueError(
            "projeto_path invalido"
        )

    projeto = (
        Path(valor)
        .expanduser()
        .resolve()
    )

    if not projeto.is_dir():
        raise ValueError(
            "Diretorio de projeto inexistente"
        )

    return projeto


def _validar_sarif(
    valor: Any,
) -> Path:

    if not isinstance(
        valor,
        str,
    ):
        raise ValueError(
            "sarif_path deve ser texto"
        )

    valor = valor.strip()

    if (
        not valor
        or "\x00" in valor
    ):
        raise ValueError(
            "sarif_path invalido"
        )

    sarif = (
        Path(valor)
        .expanduser()
        .resolve()
    )

    if not sarif.is_file():
        raise ValueError(
            "Arquivo SARIF inexistente"
        )

    if sarif.suffix.lower() != ".sarif":
        raise ValueError(
            "Arquivo deve possuir extensao .sarif"
        )

    try:
        documento = json.loads(
            sarif.read_text(
                encoding="utf-8",
            )
        )
    except Exception as exc:
        raise ValueError(
            "SARIF nao e JSON valido"
        ) from exc

    if not isinstance(
        documento,
        dict,
    ):
        raise ValueError(
            "Raiz SARIF deve ser objeto JSON"
        )

    if not isinstance(
        documento.get(
            "runs"
        ),
        list,
    ):
        raise ValueError(
            "SARIF sem vetor runs"
        )

    return sarif


def validar_entrada_operacional(
    payload: dict[str, Any],
) -> dict[str, Any]:

    if not isinstance(
        payload,
        dict,
    ):
        raise ValueError(
            "Payload invalido"
        )

    projeto = _validar_projeto(
        payload.get(
            "projeto_path"
        )
    )

    sarif = _validar_sarif(
        payload.get(
            "sarif_path"
        )
    )

    indice = payload.get(
        "indice"
    )

    if indice is not None:
        if (
            isinstance(
                indice,
                bool,
            )
            or not isinstance(
                indice,
                int,
            )
            or indice < 0
        ):
            raise ValueError(
                "indice deve ser inteiro >= 0"
            )

    achado_id = payload.get(
        "achado_id"
    )

    if (
        achado_id is not None
        and (
            not isinstance(
                achado_id,
                str,
            )
            or not achado_id.strip()
        )
    ):
        raise ValueError(
            "achado_id invalido"
        )

    limite = payload.get(
        "limite"
    )

    if limite is not None:
        if (
            isinstance(
                limite,
                bool,
            )
            or not isinstance(
                limite,
                int,
            )
            or limite <= 0
        ):
            raise ValueError(
                "limite deve ser inteiro > 0"
            )

    return {
        "projeto_path":
            str(projeto),

        "sarif_path":
            str(sarif),

        "indice":
            indice,

        "achado_id":
            (
                achado_id.strip()
                if isinstance(
                    achado_id,
                    str,
                )
                else None
            ),

        "limite":
            limite,
    }


def _arquivo_estado(
    job: dict[str, Any],
) -> Path:

    return (
        Path(
            job["diretorio_execucao"]
        )
        / "estado.json"
    )


def _estado_publico(
    job: dict[str, Any],
) -> dict[str, Any]:

    chaves = (
        "job_id",
        "estado",
        "criado_em",
        "iniciado_em",
        "atualizado_em",
        "finalizado_em",
        "projeto_path",
        "sarif_path",
        "total_achados",
        "total_selecionado",
        "total_processado",
        "indice_atual",
        "achado_atual",
        "agente_atual",
        "provedor_atual",
        "etapa_atual",
        "detalhe_atual",
        "pausa_solicitada",
        "parada_solicitada",
        "erro",
        "motivo_termino",
        "diretorio_execucao",
        "resultados",
    )

    resultado = {
        chave:
            deepcopy(
                job.get(chave)
            )
        for chave in chaves
    }

    total = int(
        job.get(
            "total_selecionado",
            0,
        )
        or 0
    )

    processado = int(
        job.get(
            "total_processado",
            0,
        )
        or 0
    )

    resultado["progresso"] = {
        "processados":
            processado,

        "total":
            total,

        "percentual":
            (
                round(
                    processado
                    * 100.0
                    / total,
                    2,
                )
                if total
                else 0.0
            ),
    }

    return resultado


def _persistir(
    job: dict[str, Any],
) -> None:

    destino = _arquivo_estado(
        job
    )

    temporario = (
        destino
        .with_suffix(
            ".json.tmp"
        )
    )

    dados = _estado_publico(
        job
    )

    temporario.write_text(
        json.dumps(
            dados,
            ensure_ascii=False,
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )

    temporario.replace(
        destino
    )


def _atualizar(
    job_id: str,
    dados: dict[str, Any],
) -> None:

    with _cond:

        job = _jobs.get(
            job_id
        )

        if job is None:
            return

        # VERITASSEC_FILTRO_EVENTOS_20261022
        dados = dict(dados)

        identificador = dados.pop(
            "_achado_telemetria",
            None,
        )

        if identificador is not None:
            atual = job.get("achado_atual")

            if (
                atual is not None
                and str(atual) != str(identificador)
            ):
                return

        # Evita sobrescrever evento de agente
        # com um inicio_achado atrasado.
        if (
            dados.get("etapa_atual") == "inicio_achado"
            and str(job.get("achado_atual")) ==
                str(dados.get("achado_atual"))
            and job.get("agente_atual")
        ):
            dados.pop("agente_atual", None)
            dados.pop("provedor_atual", None)
            dados.pop("etapa_atual", None)

        job.update(
            dados
        )

        job["atualizado_em"] = (
            agora()
        )

        _persistir(
            job
        )


registrar_emissor(
    _atualizar
)


def _selecionar(
    *,
    achados: list[Any],
    indice: int | None,
    achado_id: str | None,
    limite: int | None,
) -> list[Any]:

    if (
        indice is not None
        or achado_id is not None
    ):
        return [
            selecionar_achado(
                achados,
                indice=indice,
                achado_id=achado_id,
            )
        ]

    if limite is not None:
        return achados[
            :limite
        ]

    return achados


def _esperar_se_pausado(
    job_id: str,
) -> bool:
    """
    Retorna False quando parada foi solicitada.
    """

    with _cond:

        job = _jobs[
            job_id
        ]

        if job[
            "parada_solicitada"
        ]:
            return False

        if job[
            "pausa_solicitada"
        ]:

            job["estado"] = "PAUSADO"
            job["atualizado_em"] = agora()

            _persistir(
                job
            )

        while (
            job["pausa_solicitada"]
            and not job[
                "parada_solicitada"
            ]
        ):
            _cond.wait(
                timeout=1.0
            )

        if job[
            "parada_solicitada"
        ]:
            return False

        if job["estado"] == "PAUSADO":
            job["estado"] = "EXECUTANDO"
            job["atualizado_em"] = agora()

            _persistir(
                job
            )

        return True


def _salvar_resultado(
    *,
    job: dict[str, Any],
    indice: int,
    achado: Any,
    resultado: Any,
) -> str:

    raiz = (
        Path(
            job[
                "diretorio_execucao"
            ]
        )
        / "resultados"
    )

    raiz.mkdir(
        parents=True,
        exist_ok=True,
    )

    destino = (
        raiz
        / f"{indice:04d}.json"
    )

    pacote = {
        "indice":
            indice,

        "achado":
            (
                achado.model_dump(
                    mode="json"
                )
                if hasattr(
                    achado,
                    "model_dump",
                )
                else achado
            ),

        "resultado":
            resultado,
    }

    destino.write_text(
        json.dumps(
            pacote,
            ensure_ascii=False,
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )

    return str(
        destino
    )


def _worker(
    job_id: str,
) -> None:

    vincular_execucao(
        job_id
    )

    try:

        with _cond:
            job = _jobs[
                job_id
            ]

            job["estado"] = (
                "EXECUTANDO"
            )

            job["iniciado_em"] = (
                agora()
            )

            job["atualizado_em"] = (
                agora()
            )

            _persistir(
                job
            )

        achados = (
            carregar_achados_sarif(
                job["sarif_path"],
                job["projeto_path"],
            )
        )

        # VERITASSEC_ETAPA03_DESCOBERTA_OPCIONAL
        # Opt-in explicito. Nao altera a execucao
        # tradicional baseada em SARIF.
        import os as _vs_os

        if (
            _vs_os.environ.get(
                "VERITASSEC_DESCOBERTA_AUTONOMA",
                "0",
            ).strip()
            == "1"
        ):
            from .descoberta_autonoma import (
                descobrir_candidatos,
            )

            _candidatos_autonomos = descobrir_candidatos(
                job["projeto_path"],
            )

            _ids_existentes = {
                str(getattr(item, "id", ""))
                for item in achados
            }

            achados = list(achados)

            for _candidato in _candidatos_autonomos:
                if _candidato.id in _ids_existentes:
                    continue

                achados.append(_candidato)
                _ids_existentes.add(_candidato.id)

        selecionados = _selecionar(
            achados=achados,
            indice=job["indice"],
            achado_id=job["achado_id"],
            limite=job["limite"],
        )

        with _cond:
            job = _jobs[
                job_id
            ]

            job[
                "total_achados"
            ] = len(
                achados
            )

            job[
                "total_selecionado"
            ] = len(
                selecionados
            )

            job[
                "atualizado_em"
            ] = agora()

            _persistir(
                job
            )

        # VERITASSEC_INTEGRACAO_COLETA_DAST_JOB_V1
        # Coleta somente alertas já existentes; erros ficam registrados sem
        # transformar ausência de evidência em falso positivo.
        _dast_cfg = job.get("configuracao_dast") or {}
        if _dast_cfg.get("habilitado") is True:
            import asyncio as _vs_asyncio
            import os as _vs_os
            from .coleta_incremental_dast import (
                coletar_alertas_existentes as _vs_coletar,
                correlacionar_e_registrar as _vs_registrar,
            )
            from aplicacao.integracoes.zap.cliente import ClienteZap as _vs_ClienteZap
            try:
                _vs_cliente = _vs_ClienteZap(
                    zap_url=_vs_os.environ.get("VERITASSEC_ZAP_URL", "http://127.0.0.1:8081")
                )
                _vs_alertas = _vs_asyncio.run(_vs_coletar(
                    _vs_cliente,
                    _dast_cfg["url_base"],
                    _dast_cfg["autorizado"],
                ))
                _vs_achados = [
                    a.model_dump(mode="json") if hasattr(a, "model_dump")
                    else a if isinstance(a, dict) else vars(a)
                    for a in selecionados
                ]
                _vs_resumo = _vs_registrar(
                    __import__("pathlib").Path(job["diretorio_execucao"]) / "dast-correlacao.json",
                    _vs_achados,
                    _vs_alertas,
                )
                with _cond:
                    job["dast_coleta"] = {"estado": "COLETADO", **_vs_resumo}
                    _persistir(job)
            except Exception as _vs_exc:
                with _cond:
                    job["dast_coleta"] = {
                        "estado": "INCONCLUSIVO",
                        "motivo": type(_vs_exc).__name__,
                        "justificativa": "Coleta DAST não concluída; nenhuma vulnerabilidade foi confirmada ou descartada.",
                    }
                    _persistir(job)

        # ============================================================
        # VERITASSEC_ACHADOS_PARALELOS_20261019
        #
        # Os achados são independentes e passam pelo MESMO pipeline.
        # Apenas a execução entre achados é concorrente.
        #
        # - 7 agentes preservados por achado
        # - política determinística preservada
        # - Local/GPT/Gemini preservados
        # - ordem final preservada
        # - teto de concorrência explícito
        # ============================================================
        from concurrent.futures import ThreadPoolExecutor
        
        _workers_achados = min(
            2,
            max(
                1,
                len(selecionados),
            ),
        )
        
        _timeout_achado = 60.0

        # VERITASSEC_LIMITES_LOCAL_COMPATIVEIS_V2
        _workers_achados, _timeout_achado = (
            _vs_limites_execucao_local(
                total=len(selecionados),
                workers_originais=_workers_achados,
                timeout_original=_timeout_achado,
            )
        )

        
        # VERITASSEC_CORRECAO_CONTEXTO_ACHADO
        #
        # threading.local() nao e herdado pelas
        # threads do ThreadPoolExecutor.
        #
        # Vincular o job antes de executar o
        # pipeline e liberar no finally.


        # VERITASSEC_DAST_CONTEXTO_PRE_PIPELINE_V2
        _vs_contextos_dast = {}
        _vs_estado_dast = job.get("dast_coleta") or {}
        _vs_arquivo_dast = (
            Path(job["diretorio_execucao"]) / "dast-correlacao.json"
        )

        if (
            _vs_estado_dast.get("estado") == "COLETADO"
            and _vs_arquivo_dast.is_file()
        ):
            try:
                _vs_documento_dast = json.loads(
                    _vs_arquivo_dast.read_text(encoding="utf-8")
                )
                _vs_correlacoes = _vs_documento_dast.get(
                    "correlacoes", []
                )
                _vs_alertas = _vs_documento_dast.get(
                    "alertas", []
                )

                if not isinstance(_vs_correlacoes, list):
                    raise ValueError("CORRELACOES_INVALIDAS")
                if not isinstance(_vs_alertas, list):
                    raise ValueError("ALERTAS_INVALIDOS")

                # VERITASSEC_DAST_CONTEXTUAL_PIPELINE_V1
                # Associacao contextual nao e correlacao confirmatoria.
                from .correlacao_dast import (
                    associar_contexto_endpoint as _vs_associar_contexto,
                )

                for _vs_item in selecionados:
                    _vs_dados = (
                        _vs_item.model_dump(mode="json")
                        if hasattr(_vs_item, "model_dump")
                        else (
                            dict(_vs_item)
                            if isinstance(_vs_item, dict)
                            else vars(_vs_item)
                        )
                    )

                    _vs_id = str(_vs_dados.get("id") or "")

                    if not _vs_id:
                        continue

                    _vs_corr = [
                        c for c in _vs_correlacoes
                        if isinstance(c, dict)
                        and str(c.get("id_sast", "")) == _vs_id
                    ]

                    _vs_associacoes = []
                    _vs_alertas_item = []

                    for _vs_alerta in _vs_alertas:
                        if not isinstance(_vs_alerta, dict):
                            continue

                        _vs_associacao = _vs_associar_contexto(
                            _vs_dados,
                            _vs_alerta,
                        )

                        if _vs_associacao.get(
                            "associacao_contextual"
                        ) is True:
                            _vs_associacoes.append(
                                _vs_associacao
                            )
                            _vs_alertas_item.append(
                                _vs_alerta
                            )

                    if not _vs_corr and not _vs_associacoes:
                        continue

                    _vs_contextos_dast[_vs_id] = {
                        "origem": "OWASP ZAP",
                        "arquivo": str(_vs_arquivo_dast),
                        "correlacoes": _vs_corr,
                        "associacoes_contextuais": _vs_associacoes,
                        "alertas": _vs_alertas_item,
                        "classificacao_dast": "inconclusivo",
                        "investigacao_adicional_necessaria": True,
                        "propriedade_seguranca_comprovada": False,
                    }

            except (OSError, ValueError, TypeError) as exc:
                with _cond:
                    job["dast_contexto"] = {
                        "estado": "INCONCLUSIVO",
                        "motivo": type(exc).__name__,
                    }
                    _persistir(job)

        def _executar_achado_com_telemetria(
            _achado,
        ):
            identificador = str(
                getattr(_achado, "id", None)
                or (
                    _achado.get("id")
                    if isinstance(_achado, dict)
                    else ""
                )
            )

            vincular_execucao(job_id)
            vincular_achado(identificador)

            try:

                _vs_evidencia = _vs_contextos_dast.get(
                    identificador
                )

                if _vs_evidencia is not None:
                    if isinstance(_achado, dict):
                        _vs_achado_pipeline = dict(_achado)
                        _vs_achado_pipeline[
                            "evidencias_dast_correlacionadas"
                        ] = _vs_evidencia
                    elif hasattr(_achado, "model_copy"):
                        _vs_achado_pipeline = _achado.model_copy(
                            update={
                                "evidencias_dast_correlacionadas":
                                    _vs_evidencia
                            }
                        )
                    else:
                        _vs_achado_pipeline = _achado
                else:
                    _vs_achado_pipeline = _achado

                return executar_pipeline_agent(
                    _vs_achado_pipeline
                )

            finally:
                vincular_achado(None)
                vincular_execucao(None)

        _pool_achados = ThreadPoolExecutor(
            max_workers=_workers_achados,
            thread_name_prefix="veritassec-achado",
        )
        try:
        
            _futuros = [
                _pool_achados.submit(
                    _executar_achado_com_telemetria,
                    _achado,
                )
                for _achado in selecionados
            ]
        
            for posicao, achado in enumerate(
                selecionados
            ):

                if not _esperar_se_pausado(
                    job_id
                ):
                    break

                achado_id = str(
                    getattr(
                        achado,
                        "id",
                        None,
                    )
                    or (
                        achado.get("id")
                        if isinstance(
                            achado,
                            dict,
                        )
                        else ""
                    )
                    or posicao
                )

                _atualizar(
                    job_id,
                    {
                        "indice_atual":
                            posicao,

                        "achado_atual":
                            achado_id,

                        "agente_atual":
                            None,

                        "provedor_atual":
                            None,

                        "etapa_atual":
                            "inicio_achado",

                        "detalhe_atual":
                            (
                                f"Achado "
                                f"{posicao + 1}/"
                                f"{len(selecionados)}"
                            ),
                    },
                )

                resultado = _futuros[posicao].result(timeout=_timeout_achado)

                # VERITASSEC_DAST_ESTADO_GLOBAL_V7
                # Coleta passiva no nível da aplicação não equivale
                # a aquisição dinâmica individual nem a confirmação
                # da vulnerabilidade descrita no SARIF.
                if isinstance(resultado, dict):
                    _vs_estado_global = job.get("dast_coleta") or {}
                    _vs_config_global = job.get("configuracao_dast") or {}

                    resultado["dast_execucao_aplicacao"] = {
                        "habilitado": (
                            _vs_config_global.get("habilitado") is True
                        ),
                        "estado": _vs_estado_global.get(
                            "estado", "NAO_EXECUTADO"
                        ),
                        "motivo": _vs_estado_global.get("motivo"),
                        "coleta_independente_endpoint_sarif": True,
                        "confirmacao_vulnerabilidade": False,
                    }

                    _vs_orquestracao = resultado.get(
                        "orquestracao_zap"
                    )

                    if isinstance(_vs_orquestracao, dict):
                        _vs_orquestracao[
                            "estado_coleta_aplicacao"
                        ] = _vs_estado_global.get(
                            "estado", "NAO_EXECUTADO"
                        )
                        _vs_orquestracao[
                            "elegibilidade_restrita_ao_achado"
                        ] = True

                # VERITASSEC_EVIDENCIAS_DAST_POR_ACHADO_V1
                # Evidencia DAST e metadados da correlacao seguem anexados ao
                # resultado, sem sobrescrever classificacoes dos agentes.
                _vs_dast_coleta = job.get("dast_coleta") or {}
                _vs_dast_caminho = (
                    __import__("pathlib").Path(job["diretorio_execucao"])
                    / "dast-correlacao.json"
                )
                if (
                    isinstance(resultado, dict)
                    and _vs_dast_coleta.get("estado") == "COLETADO"
                    and _vs_dast_caminho.is_file()
                ):
                    try:
                        import json as _vs_json
                        _vs_dast_documento = _vs_json.loads(
                            _vs_dast_caminho.read_text(encoding="utf-8")
                        )
                        _vs_correlacoes = [
                            c for c in _vs_dast_documento.get("correlacoes", [])
                            if str(c.get("id_sast", "")) == achado_id
                        ]
                        _vs_alertas = _vs_dast_documento.get("alertas", [])
                        _vs_regras = {
                            str(c.get("regra_dast", ""))
                            for c in _vs_correlacoes
                        }
                        _vs_evidencias = [
                            a for a in _vs_alertas
                            if str(a.get("regra", "")) in _vs_regras
                        ]
                        # VERITASSEC_PRESERVACAO_DAST_CONTEXTUAL_V1
                        _vs_contexto_anterior = resultado.get('evidencias_dast_correlacionadas')
                        if not isinstance(_vs_contexto_anterior, dict):
                            _vs_contexto_anterior = {}
                        resultado["evidencias_dast_correlacionadas"] = {
                            "origem": "OWASP ZAP",
                            "arquivo": str(_vs_dast_caminho),
                            "correlacoes": _vs_correlacoes,
                            "alertas": _vs_evidencias,
                            "classificacao_dast": "inconclusivo",
                            "justificativa": (
                                "Alertas e correlacoes nao constituem, "
                                "isoladamente, comprovacao da vulnerabilidade."
                            ),
                            "investigacao_adicional_necessaria": True,
                        }
                        _vs_contexto_novo = resultado.get('evidencias_dast_correlacionadas')
                        if isinstance(_vs_contexto_novo, dict):
                            for _vs_campo in (
                                'associacoes_contextuais',
                                'propriedade_seguranca_comprovada',
                                'investigacao_adicional_necessaria',
                            ):
                                if _vs_campo in _vs_contexto_anterior:
                                    _vs_contexto_novo[_vs_campo] = (
                                        _vs_contexto_anterior[_vs_campo]
                                    )
                            if _vs_contexto_anterior.get('associacoes_contextuais'):
                                _vs_contexto_novo['alertas'] = _vs_contexto_anterior.get('alertas', [])
                    except (OSError, ValueError, TypeError, KeyError) as _vs_erro:
                        resultado["evidencias_dast_correlacionadas"] = {
                            "classificacao_dast": "inconclusivo",
                            "erro": type(_vs_erro).__name__,
                            "justificativa": "Nao foi possivel associar evidencias DAST.",
                        }

                # Deduplicacao exata; nao altera o veredito dos agentes.
                resultado = _vs_deduplicar_evidencias_dast(resultado)

                with _cond:

                    job = _jobs[
                        job_id
                    ]

                    arquivo = (
                        _salvar_resultado(
                            job=job,
                            indice=posicao,
                            achado=achado,
                            resultado=resultado,
                        )
                    )

                    job[
                        "resultados"
                    ].append(
                        {
                            "indice":
                                posicao,

                            "achado_id":
                                achado_id,

                            "arquivo":
                                arquivo,
                        }
                    )

                    job[
                        "total_processado"
                    ] += 1

                    job[
                        "etapa_atual"
                    ] = (
                        "checkpoint_achado"
                    )

                    job[
                        "agente_atual"
                    ] = None

                    job[
                        "provedor_atual"
                    ] = None

                    job[
                        "atualizado_em"
                    ] = agora()

                    _persistir(
                        job
                    )

                if not _esperar_se_pausado(
                    job_id
                ):
                    break
        finally:
            _pool_achados.shutdown(
                wait=False,
                cancel_futures=True,
            )

        with _cond:

            job = _jobs[
                job_id
            ]

            if job[
                "parada_solicitada"
            ]:
                job["estado"] = (
                    "INTERROMPIDO"
                )

                job[
                    "motivo_termino"
                ] = (
                    "INTERROMPIDO_PELO_USUARIO"
                )

            else:
                job["estado"] = (
                    "CONCLUIDO"
                )

                job[
                    "motivo_termino"
                ] = (
                    "TODOS_ACHADOS_PROCESSADOS"
                )

            job[
                "etapa_atual"
            ] = "finalizado"

            job[
                "agente_atual"
            ] = None

            job[
                "provedor_atual"
            ] = None

            job[
                "finalizado_em"
            ] = agora()

            job[
                "atualizado_em"
            ] = agora()

            _persistir(
                job
            )

    except Exception as exc:

        with _cond:

            job = _jobs.get(
                job_id
            )

            if job is not None:

                job["estado"] = (
                    "ERRO"
                )

                job["erro"] = (
                    type(exc).__name__
                    + ": "
                    + str(exc)
                )[:2000]

                job[
                    "motivo_termino"
                ] = (
                    "ERRO_CONTROLADO"
                )

                job[
                    "finalizado_em"
                ] = agora()

                job[
                    "atualizado_em"
                ] = agora()

                _persistir(
                    job
                )

    finally:

        vincular_execucao(
            None
        )


def iniciar_execucao(
    payload: dict[str, Any],
) -> dict[str, Any]:

    entrada = (
        validar_entrada_operacional(
            payload
        )
    )
    # VERITASSEC_DAST_AUTOMATICO_RESTAURADO
    #
    # A configuração é interna, sem confirmação manual.
    # O alvo precisa ser uma origem local aprovada.
    # A autorização de cada acesso permanece subordinada
    # às políticas de escopo do pipeline.
    import os as _vs_os
    from urllib.parse import urlsplit as _vs_urlsplit
    from .contrato_dast import (
        validar_configuracao_dast as _vs_validar_dast,
    )

    _vs_base = _vs_os.environ.get(
        "VERITASSEC_RUNTIME_LOCAL_BASE_URL",
        "",
    ).strip()

    if not _vs_base:
        _vs_base = "http://127.0.0.1:3001"

    _vs_url = _vs_urlsplit(_vs_base)

    _dast_validada = _vs_validar_dast(
        True,
        _vs_base,
        autorizado=True,
    )


    job_id = uuid4().hex

    diretorio = (
        _raiz_execucoes()
        / job_id
    )

    diretorio.mkdir(
        parents=True,
        exist_ok=False,
    )

    (
        diretorio
        / "resultados"
    ).mkdir(
        parents=True,
        exist_ok=True,
    )

    job = {
        "job_id":
            job_id,

        "estado":
            "PRONTO",

        "criado_em":
            agora(),

        "iniciado_em":
            None,

        "atualizado_em":
            agora(),

        "finalizado_em":
            None,

        "projeto_path":
            entrada[
                "projeto_path"
            ],

        "sarif_path":
            entrada[
                "sarif_path"
            ],

        "indice":
            entrada[
                "indice"
            ],

        "achado_id":
            entrada[
                "achado_id"
            ],

        "limite":
            entrada[
                "limite"
            ],

        "total_achados":
            0,

        "total_selecionado":
            0,

        "total_processado":
            0,

        "indice_atual":
            None,

        "achado_atual":
            None,

        "agente_atual":
            None,

        "provedor_atual":
            None,

        "etapa_atual":
            "aguardando_inicio",

        "detalhe_atual":
            None,

        "pausa_solicitada":
            False,

        "parada_solicitada":
            False,

        "erro":
            None,

        "motivo_termino":
            None,

        "diretorio_execucao":
            str(diretorio),

        "resultados":
            [],

        "configuracao_dast": {
            "habilitado": _dast_validada.habilitado,
            "url_base": _dast_validada.url_base,
            "autorizado": _dast_validada.autorizado,
        },
        "dast_coleta": {"estado": "NAO_EXECUTADO"},
    }

    with _cond:

        _jobs[
            job_id
        ] = job

        _persistir(
            job
        )

        thread = Thread(
            target=_worker,
            args=(
                job_id,
            ),
            name=(
                "veritassec-"
                + job_id[:8]
            ),
            daemon=True,
        )

        job["_thread"] = thread

        thread.start()

    return _estado_publico(
        job
    )



# VERITASSEC_RECUPERACAO_PERSISTENTE_20261022
def _recuperar_estado_persistido(
    job_id: str,
) -> dict[str, Any] | None:
    """
    Recupera estado salvo após reinício.

    Não retoma tarefas automaticamente.
    Não transforma execução interrompida em concluída.
    """
    import re

    if (
        not isinstance(job_id, str)
        or re.fullmatch(r"[0-9a-f]{32}", job_id) is None
    ):
        return None

    raiz = _raiz_execucoes().resolve()
    diretorio = (raiz / job_id).resolve()

    try:
        diretorio.relative_to(raiz)
    except ValueError:
        return None

    arquivo = diretorio / "estado.json"

    if not arquivo.is_file() or arquivo.is_symlink():
        return None

    try:
        dados = json.loads(
            arquivo.read_text(encoding="utf-8")
        )
    except (OSError, ValueError):
        return None

    if not isinstance(dados, dict):
        return None

    if dados.get("job_id") != job_id:
        return None

    if Path(
        str(dados.get("diretorio_execucao") or "")
    ).resolve() != diretorio:
        return None

    estado = str(dados.get("estado") or "")

    if estado not in ESTADOS_FINAIS:
        dados["estado"] = "INTERROMPIDO"
        dados["motivo_termino"] = (
            "PROCESSO_ANTERIOR_NAO_ESTA_ATIVO"
        )
        dados["finalizado_em"] = (
            dados.get("finalizado_em") or agora()
        )
        dados["agente_atual"] = None
        dados["provedor_atual"] = None
        dados["etapa_atual"] = (
            "execucao_interrompida_por_reinicio"
        )

    dados["diretorio_execucao"] = str(diretorio)

    return dados


def _obter_job_consulta(
    job_id: str,
) -> dict[str, Any] | None:
    """
    Consulta primeiro a execução ativa e,
    se ausente, o estado persistido em disco.
    """
    job = _jobs.get(job_id)

    if job is not None:
        return job

    return _recuperar_estado_persistido(job_id)


def existe_execucao(
    job_id: str,
) -> bool:

    with _cond:
        return _obter_job_consulta(job_id) is not None


def obter_execucao(
    job_id: str,
) -> dict[str, Any]:

    with _cond:

        job = _obter_job_consulta(job_id)

        if job is None:
            raise KeyError(job_id)

        return _estado_publico(job)


def pausar_execucao(
    job_id: str,
) -> dict[str, Any]:

    with _cond:

        job = _jobs.get(
            job_id
        )

        if job is None:
            raise KeyError(
                job_id
            )

        if job["estado"] in ESTADOS_FINAIS:
            raise ValueError(
                "Execucao ja finalizada"
            )

        job[
            "pausa_solicitada"
        ] = True

        job[
            "etapa_atual"
        ] = (
            "pausa_solicitada"
        )

        job[
            "atualizado_em"
        ] = agora()

        _persistir(
            job
        )

        _cond.notify_all()

        return _estado_publico(
            job
        )


def retomar_execucao(
    job_id: str,
) -> dict[str, Any]:

    with _cond:

        job = _jobs.get(
            job_id
        )

        if job is None:
            raise KeyError(
                job_id
            )

        if job["estado"] in ESTADOS_FINAIS:
            raise ValueError(
                "Execucao ja finalizada"
            )

        job[
            "pausa_solicitada"
        ] = False

        if job["estado"] == "PAUSADO":
            job["estado"] = (
                "EXECUTANDO"
            )

        job[
            "etapa_atual"
        ] = (
            "retomada_solicitada"
        )

        job[
            "atualizado_em"
        ] = agora()

        _persistir(
            job
        )

        _cond.notify_all()

        return _estado_publico(
            job
        )


def parar_execucao(
    job_id: str,
) -> dict[str, Any]:

    with _cond:

        job = _jobs.get(
            job_id
        )

        if job is None:
            raise KeyError(
                job_id
            )

        if job["estado"] in ESTADOS_FINAIS:
            return _estado_publico(
                job
            )

        job[
            "parada_solicitada"
        ] = True

        job[
            "pausa_solicitada"
        ] = False

        job[
            "etapa_atual"
        ] = (
            "parada_solicitada"
        )

        job[
            "atualizado_em"
        ] = agora()

        _persistir(
            job
        )

        _cond.notify_all()

        return _estado_publico(
            job
        )


# ============================================================
# VERITASSEC_PASSO3_RESULTADOS_OPERACIONAIS
# ============================================================

def obter_resultados_execucao(
    job_id: str,
) -> dict[str, Any]:

    with _cond:

        job = _obter_job_consulta(job_id)

        if job is None:
            raise KeyError(job_id)

        diretorio = Path(
            job[
                "diretorio_execucao"
            ]
        ).resolve()

        referencias = list(
            job.get(
                "resultados",
                [],
            )
        )

    resultados = []

    for referencia in referencias:

        arquivo = Path(
            referencia[
                "arquivo"
            ]
        ).resolve()

        try:
            arquivo.relative_to(
                diretorio
            )
        except ValueError as exc:
            raise RuntimeError(
                "Resultado fora do diretorio "
                "da execucao."
            ) from exc

        if not arquivo.is_file():
            continue

        try:
            dados = json.loads(
                arquivo.read_text(
                    encoding="utf-8"
                )
            )
        except Exception:
            continue

        resultados.append(
            dados
        )

    return {
        "job_id":
            job_id,

        "total":
            len(
                resultados
            ),

        "resultados":
            resultados,
    }



def _vs_limites_execucao_local(
    *,
    total: int,
    workers_originais: int,
    timeout_original: float,
):
    """
    Preserva os limites originais para GPT/Gemini.

    Quando o modelo Local participa:
      - um achado por vez;
      - timeout compatível com os sete agentes;
      - reserva para demais etapas;
      - nenhuma alteração no roteamento.
    """
    import math

    selecionados = {
        item.strip().lower()
        for item in os.getenv(
            "VERITASSEC_PROVEDORES_PAPEIS",
            "",
        ).split(",")
        if item.strip()
    }

    if "local" not in selecionados:
        return (
            workers_originais,
            timeout_original,
        )

    try:
        timeout_local = float(
            os.getenv(
                "VERITASSEC_TIMEOUT_LOCAL",
                "180",
            )
        )

        if not math.isfinite(timeout_local):
            raise ValueError(
                "TIMEOUT_LOCAL_NAO_FINITO"
            )

    except (ValueError, TypeError):
        timeout_local = 180.0

    timeout_local = min(
        600.0,
        max(60.0, timeout_local),
    )

    provedores_remotos = len(
        selecionados.intersection(
            {"gpt", "gemini"}
        )
    )

    # Sete agentes especializados.
    # Tempo para a tentativa Local de cada agente,
    # eventuais substituicoes e etapas complementares.

    timeout_achado = (
        7.0 * (
            timeout_local
            + 120.0 * provedores_remotos
        )
        + 300.0
    )

    timeout_achado = max(
        900.0,
        timeout_achado,
    )

    return (
        1,
        timeout_achado,
    )



# VERITASSEC_DEDUP_EVIDENCIAS_V2
def _vs_deduplicar_evidencias_dast(resultado):
    """
    Preserva a ordem e remove somente registros JSON
    integralmente iguais.
    """
    if not isinstance(resultado, dict):
        return resultado

    bloco = resultado.get(
        "evidencias_dast_correlacionadas"
    )

    if not isinstance(bloco, dict):
        return resultado

    for campo in ("alertas", "correlacoes"):
        registros = bloco.get(campo)

        if not isinstance(registros, list):
            continue

        vistos = set()
        unicos = []

        for registro in registros:
            try:
                chave = json.dumps(
                    registro,
                    sort_keys=True,
                    ensure_ascii=False,
                    separators=(",", ":"),
                    allow_nan=False
                )
            except (TypeError, ValueError):
                unicos.append(registro)
                continue

            if chave not in vistos:
                vistos.add(chave)
                unicos.append(registro)

        bloco[campo] = unicos

    return resultado
