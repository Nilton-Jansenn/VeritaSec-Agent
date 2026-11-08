from __future__ import annotations
from .aquisicao_evidencia import ExecutorAquisicaoEvidencia, OrcamentoInvestigacao
from .executor_cognitivo import obter_executor_ferramentas
from .plano_evidencia import construir_plano_aquisicao
from .plano_seeds_tipadas import construir_plano_aquisicao_com_seeds
from .politica_escopo import calcular_capacidades_autorizadas

from typing import Any

from .modelos import AchadoMultiagente
from .ciclo_finding import (
    construir_callbacks_ciclo,
    possui_dinamica_autorizada,
)
from .orquestrador import OrquestradorMultiagente


def _executar_pipeline_agent_base_integral(
    achado: AchadoMultiagente | dict[str, Any],
) -> dict[str, Any]:

    if isinstance(achado, dict):
        achado = AchadoMultiagente(**achado)

    resultado = (
        OrquestradorMultiagente()
        .investigar(achado)
    )

    dados = resultado.model_dump(
        mode="json"
    )

    raciocinios = []

    for evento in dados.get(
        "trilha",
        [],
    ):
        registro = (
            evento
            .get("saida", {})
            .get("raciocinio_agente")
        )

        if registro:
            raciocinios.append(
                {
                    "agente": evento.get(
                        "agente"
                    ),
                    **registro,
                }
            )

    chamadas_reais = sum(
        1
        for item in raciocinios
        if item.get(
            "chamada_modelo_realizada"
        )
    )

    fallbacks = sum(
        1
        for item in raciocinios
        if item.get(
            "fallback_deterministico"
        )
    )

    dados["raciocinio"] = {
        "agentes_total": len(
            raciocinios
        ),
        "chamadas_llm_reais": (
            chamadas_reais
        ),
        "fallbacks_deterministicos": (
            fallbacks
        ),
        "modo": (
            "LLM_REAL"
            if chamadas_reais
            == len(raciocinios)
            == 7
            else (
                "FALLBACK_DETERMINISTICO"
                if fallbacks
                == len(raciocinios)
                == 7
                else "MISTO"
            )
        ),
        "agentes": raciocinios,
    }


    # --------------------------------------------------------
    # Plano cognitivo de aquisição de evidência.
    #
    # A saída da LLM é declarativa. Nenhuma ferramenta é
    # executada diretamente a partir desta saída.
    # --------------------------------------------------------
    decisoes_cognitivas = []

    for item in raciocinios:
        agente_nome = str(
            item.get(
                "agente",
                "",
            )
        )

        decisao_agente = item.get(
            "decisao",
            {},
        )

        decisoes_cognitivas.append(
            (
                agente_nome,
                decisao_agente,
            )
        )

    capacidades_registradas = {
        "busca_codigo",
        "revisao_codigo_seguro",
        "path_traversal",
        "runtime_http",
        "autorizacao_http",
        "busca_evolucionaria",
        "zap",
        "oraculo_path_traversal",
        "oraculo_autorizacao",
        "proveniencia",
    }

    # A autorização efetiva deriva do finding/escopo,
    # nunca da própria LLM e nunca apenas do registry.
    politica_escopo = calcular_capacidades_autorizadas(
        achado=achado,
        capacidades_registradas=capacidades_registradas,
    )

    capacidades_autorizadas = set(
        politica_escopo.capacidades_autorizadas
    )

    dados["politica_escopo"] = (
        politica_escopo.dump()
    )

    plano, auditoria_seeds = (
        construir_plano_aquisicao_com_seeds(
            decisoes_por_agente=(
                decisoes_cognitivas
            ),
            capacidades_registradas=(
                capacidades_registradas
            ),
            capacidades_autorizadas=(
                capacidades_autorizadas
            ),
            execucao_dinamica_permitida=bool(
                getattr(
                    achado,
                    "execucao_dinamica_permitida",
                    False,
                )
            ),
        )
    )

    dados[
        "plano_aquisicao_evidencia"
    ] = plano.model_dump()

    dados[
        "seeds_cognitivas"
    ] = auditoria_seeds

    # VERITASSEC_CORRECAO_PONTA_A_PONTA_20261027
    # O ZAP somente e planejado quando a politica
    # deterministica ja autorizou o achado e o endpoint.

    metadados_zap = getattr(
        achado, "metadados", {}
    ) or {}

    resolucao_zap = metadados_zap.get(
        "resolucao_endpoint", {}
    )

    if not isinstance(resolucao_zap, dict):
        resolucao_zap = {}

    metodo_zap = str(
        getattr(achado, "metodo_http", None)
        or resolucao_zap.get("metodo_http")
        or ""
    ).upper()

    elegivel_zap = (
        "zap" in capacidades_autorizadas
        and resolucao_zap.get("resolvido") is True
        and metodo_zap == "GET"
        and bool(
            getattr(achado, "caminho_http", None)
        )
    )

    decisoes_zap = dados[
        "plano_aquisicao_evidencia"
    ]["decisoes_politica"]

    if elegivel_zap:

        ja_autorizado = [
            d for d in decisoes_zap
            if (
                d.get("capacidade") == "zap"
                and d.get("autorizada") is True
            )
        ]

        if ja_autorizado:
            item = ja_autorizado[0]
            decisoes_zap.remove(item)
            decisoes_zap.insert(0, item)

        else:
            decisoes_zap.insert(0, {
                "agente": "planejador",
                "capacidade": "zap",
                "autorizada": True,
                "motivo": (
                    "ESCOPADO_POR_POLITICA_DETERMINISTICA"
                ),
                "sementes": [],
            })

        dados["orquestracao_zap"] = {
            "elegivel": True,
            "metodo": "GET",
            "planejamento": "AUTORIZADO",
        }

    else:
        dados["orquestracao_zap"] = {
            "elegivel": False,
            "tipo": "AQUISICAO_INDIVIDUAL",
            "motivo": (
                "SEM_ENDPOINT_GET_COM_ESCOPO_AUTORIZADO"
            ),
            "coleta_passiva_aplicacao": (
                "GERENCIADA_PELO_JOB"
            ),
            "observacao": (
                "A ausência de endpoint GET no achado "
                "não determina o estado da coleta "
                "passiva da aplicação."
            ),
        }


    # M21B — a LLM já passou pela política M20.
    # Somente decisões autorizadas chegam ao executor.
    try:
        executor_operacional = (
            obter_executor_ferramentas(
                achado=achado
            )
        )

        aquisitor = (
            ExecutorAquisicaoEvidencia(
                executor_operacional,
                orcamento=(
                    OrcamentoInvestigacao(
                        max_acoes=8,
                        max_sementes_por_acao=16,
                    )
                ),
            )
        )

        aquisicao = (
            aquisitor.executar_plano(
                achado=achado,
                plano=dados[
                    "plano_aquisicao_evidencia"
                ],
            )
        )

    except Exception as exc:
        aquisicao = {
            "criterio_parada":
                "FERRAMENTA_INDISPONIVEL",
            "orcamento": {
                "max_acoes": 8,
                "acoes_executadas": 0,
                "acoes_negadas": 0,
                "erros": 1,
            },
            "resultados": [],
            "erro": (
                type(exc).__name__
                + ": "
                + str(exc)
            )[:2000],
        }

    dados[
        "aquisicao_evidencia"
    ] = aquisicao

    # A observacao do ZAP e avaliada pelo Oracle.
    # Resposta HTTP nao equivale a prova de explorabilidade.

    from .oracle_adaptativo import (
        avaliar_resultado as _avaliar_zap
    )

    avaliacoes_zap = []

    for registro_zap in aquisicao.get(
        "resultados", []
    ):

        if registro_zap.get(
            "capacidade"
        ) != "zap":
            continue

        retorno_zap = registro_zap.get(
            "resultado"
        )

        if not isinstance(retorno_zap, dict):
            retorno_zap = {}

        aval = _avaliar_zap({
            "capacidade": "zap",
            "resultado": retorno_zap,
        })

        avaliacoes_zap.append({
            "executada": bool(
                registro_zap.get("executada")
            ),
            "avaliacao_deterministica": aval,
            "propriedade_seguranca_verificada": False,
            "resultado": (
                "EVIDENCIA_HTTP_SEM_ORACULO_ESPECIFICO"
                if registro_zap.get("executada")
                else "ZAP_NAO_EXECUTADO"
            ),
        })

    dados[
        "avaliacao_security_oracle_zap"
    ] = avaliacoes_zap

    condicoes_zap = []

    for registro_zap in aquisicao.get(
        "resultados", []
    ):

        if (
            registro_zap.get("capacidade") != "zap"
            or not registro_zap.get("executada")
        ):
            continue

        retorno_zap = (
            registro_zap.get("resultado") or {}
        )

        evidencia_zap = (
            retorno_zap.get("evidencia") or {}
        )

        condicoes_zap.append({
            "capacidade": "zap",
            "metodo": "GET",
            "varredura_ativa": False,
            "endpoint": evidencia_zap.get(
                "endpoint"
            ),
            "hash_sha256": retorno_zap.get(
                "hash_sha256"
            ),
            "observacoes_http": evidencia_zap.get(
                "observacoes", []
            ),
            "propriedade_seguranca_comprovada": False,
        })

    if condicoes_zap:

        dados["condicoes_teste"] = condicoes_zap

        lacunas_zap = list(
            dados.get("lacunas") or []
        )

        lacunas_zap.append(
            "oraculo_de_seguranca_especifico_nao_executado"
        )

        dados["lacunas"] = list(
            dict.fromkeys(lacunas_zap)
        )

    (
        contexto_ciclo,
        planejador_ciclo,
        autorizador_ciclo,
    ) = construir_callbacks_ciclo(
        achado=achado,
        dados=dados,
    )

    if possui_dinamica_autorizada(
        contexto_ciclo
    ):
        ciclo_operacional = (
            executar_ciclo_adaptativo_agent(
                contexto=contexto_ciclo,
                planejar=planejador_ciclo,
                autorizar=autorizador_ciclo,
                max_rodadas=min(
                    3,
                    max(
                        1,
                        int(
                            getattr(
                                achado,
                                "max_iteracoes",
                                3,
                            )
                            or 3
                        ),
                    ),
                ),
                max_acoes=8,
            )
        )

        ciclo_operacional[
            "executado"
        ] = True

        ciclo_operacional[
            "motivo_nao_execucao"
        ] = None

    else:
        ciclo_operacional = {
            "executado": False,
            "motivo_nao_execucao": (
                "SEM_CAPACIDADE_DINAMICA_AUTORIZADA"
            ),
            "ciclo_adaptativo": {
                "rodadas": [],
                "acoes_executadas": 0,
                "evidencia_confirmatoria": False,
            },
            "correlacao_evidencias": {},
            "estado_correlacionado": (
                "INCONCLUSIVO"
            ),
        }

    dados[
        "ciclo_adaptativo_operacional"
    ] = ciclo_operacional


    scr_m24b = {}

    for evento_m24b in dados.get(
        "trilha",
        [],
    ):
        if (
            evento_m24b.get("agente")
            == "analista_codigo"
        ):
            scr_m24b = (
                evento_m24b
                .get("saida", {})
                .get("scr", {})
            )
            break

    dados["scr"] = scr_m24b

    dados["scr_m24b"] = {
        "executado": bool(
            scr_m24b.get(
                "executado",
                False,
            )
        ),
        "nivel_sustentacao": (
            scr_m24b.get(
                "nivel_sustentacao",
                "INCONCLUSIVO",
            )
        ),
        "propriedade_seguranca": (
            scr_m24b.get(
                "propriedade_seguranca"
            )
        ),
        "evidencias_ausentes": (
            scr_m24b.get(
                "evidencias_ausentes",
                [],
            )
        ),
        "llm_confirma_sozinha": False,
    }

    return dados


def executar_pipeline_sarif_agent(
    *,
    sarif_path: str,
    projeto_path: str,
    indice: int | None = None,
    achado_id: str | None = None,
    limite: int | None = None,
):
    """
    Executa achados SARIF pelo pipeline VeritasSec-Agent.

    indice/achado_id:
        processamento individual explícito.

    sem indice/achado_id:
        processamento multi-achado.

    limite=None:
        todos os achados.
    """
    from .sarif_agent import (
        carregar_achados_sarif,
        selecionar_achado,
    )

    achados = carregar_achados_sarif(
        sarif_path,
        projeto_path,
    )

    if not achados:
        raise ValueError(
            "SARIF não contém achados utilizáveis"
        )

    # VERITASSEC_RUNTIME_ESCoPO_20261028
    # Habilita apenas achados com rota GET explicitamente resolvida.
    # Nao cria rotas, nao converte POST em GET e nao altera vereditos.
    import os as _os
    from urllib.parse import urlparse as _urlparse
    _runtime_ativo = _os.environ.get('VERITASSEC_RUNTIME_LOCAL', '').strip().lower() in ('1','true','sim')
    _zap_ativo = _os.environ.get('VERITASSEC_ZAP_HABILITADO', '').strip().lower() in ('1','true','sim')
    _base = _os.environ.get('VERITASSEC_RUNTIME_LOCAL_BASE_URL', '').strip()
    _url = _urlparse(_base)
    _loopback = _url.hostname in ('localhost','127.0.0.1','::1')
    _base_ok = (_url.scheme in ('http','https') and _loopback and not _url.username and not _url.password)
    if _runtime_ativo and _base_ok:
        for _achado in achados:
            _meta = getattr(_achado, 'metadados', None)
            if not isinstance(_meta, dict):
                continue
            _res = _meta.get('resolucao_endpoint') or {}
            if not isinstance(_res, dict):
                continue
            _metodo = str(_res.get('metodo_http') or _res.get('metodo') or '').upper()
            _caminho = _res.get('caminho_http') or _res.get('rota') or _res.get('path')
            _confirmado = _res.get('resolvido') is True or _res.get('confirmado') is True
            if not (_confirmado and _metodo == 'GET' and isinstance(_caminho, str)
                    and _caminho.startswith('/') and not _caminho.startswith('//')
                    and '://' not in _caminho and '\x00' not in _caminho):
                continue
            _achado.execucao_dinamica_permitida = True
            _achado.base_url_http = _base
            _achado.caminho_http = _caminho
            _achado.marcador_recurso = 'veritassec-runtime-local'
            _achado.max_iteracoes = 3
            _meta['runtime_local_autorizado'] = True
            _meta['zap_runtime_habilitado'] = bool(_zap_ativo)

    if achado_id is not None or indice is not None:
        achado = selecionar_achado(
            achados,
            indice=indice,
            achado_id=achado_id,
        )

        resultado = executar_pipeline_agent(
            achado
        )

        return {
            "modo": "individual",
            "total_achados_sarif": len(achados),
            "total_selecionado": 1,
            "total_processado": 1,
            "achado": achado,
            "resultado": resultado,
        }

    if limite is not None:
        if (
            isinstance(limite, bool)
            or not isinstance(limite, int)
            or limite <= 0
        ):
            raise ValueError(
                "limite deve ser inteiro maior que zero"
            )

        selecionados = achados[:limite]

    else:
        selecionados = achados

    resultados = []

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
    
    _pool_achados = ThreadPoolExecutor(
        max_workers=_workers_achados,
        thread_name_prefix="veritassec-achado",
    )
    try:
    
        _futuros = [
            _pool_achados.submit(
                executar_pipeline_agent,
                _achado,
            )
            for _achado in selecionados
        ]
    
        for posicao, achado in enumerate(
            selecionados
        ):
            try:
                resultado = _futuros[posicao].result(timeout=_timeout_achado)
            except Exception as exc:
                resultado = {
                    "classificacao_final": "INCONCLUSIVO",
                    "justificativa_classificacao": "Falha do pipeline: " + type(exc).__name__,
                    "estado_execucao": "FALHA_OU_TIMEOUT",
                    "erro_tipo": type(exc).__name__,
                    "aquisicao_evidencia": {"resultados": [], "criterio_parada": "FALHA_PIPELINE"},
                    "avaliacao_security_oracle_zap": [],
                    "explicabilidade_xai": {"estado": "NAO_PRODUZIDA", "motivo": "Falha do pipeline"},
                }
            resultados.append({
                "indice": posicao,
                "achado": achado,
                "resultado": resultado,
            })
    finally:
        _pool_achados.shutdown(
            wait=False,
            cancel_futures=True,
        )

    return {
        "modo": "multiachado",
        "total_achados_sarif": len(achados),
        "total_selecionado": len(selecionados),
        "total_processado": len(resultados),
        "limite": limite,
        "resultados": resultados,
    }


def executar_ciclo_adaptativo_agent(
    *,
    contexto: dict[str, Any],
    planejar,
    autorizar,
    max_rodadas: int = 3,
    max_acoes: int = 8,
) -> dict[str, Any]:
    from aplicacao.multiagente.ciclo_adaptativo import (
        CicloAdaptativoInvestigacao,
    )
    from aplicacao.multiagente.executor_adaptativo import (
        ExecutorAdaptativo,
    )
    from aplicacao.multiagente.oracle_adaptativo import (
        avaliar_resultado,
    )
    from aplicacao.multiagente.correlacao import (
        correlacionar_evidencias,
    )

    executor = ExecutorAdaptativo()

    ciclo = CicloAdaptativoInvestigacao(
        planejar=planejar,
        autorizar=autorizar,
        executar=executor.executar,
        avaliar_oraculo=avaliar_resultado,
        max_rodadas=max_rodadas,
        max_acoes=max_acoes,
    )

    resultado = ciclo.executar(contexto)

    evidencias = [
        e
        for rodada in resultado.rodadas
        for e in rodada.evidencias
    ]

    correlacao = correlacionar_evidencias(
        evidencia_estatica=bool(
            contexto.get(
                "evidencia_estatica",
                True,
            )
        ),
        plausibilidade_semantica=bool(
            contexto.get(
                "plausibilidade_semantica",
                True,
            )
        ),
        evidencia_dinamica=any(
            e.observavel
            for e in evidencias
        ),
        violacao_oraculo=any(
            e.violacao
            for e in evidencias
        ),
        reproduzivel=bool(
            resultado.evidencia_confirmatoria
        ),
    )

    return {
        "ciclo_adaptativo": resultado.dump(),
        "correlacao_evidencias": correlacao.dump(),
        "estado_correlacionado": correlacao.estado,
    }


from .veredito_multivariado import (
    classificar_veredito_multivariado,
)


def _vs_historico_executar_pipeline_agent_1(
    achado,
):
    resultado = (
        _executar_pipeline_agent_base_integral(
            achado
        )
    )

    achado_dict = (
        achado.model_dump(
            mode="json"
        )
        if hasattr(
            achado,
            "model_dump",
        )
        else dict(
            achado
        )
    )

    vm = (
        classificar_veredito_multivariado(
            achado=achado_dict,
            resultado=resultado,
        )
    )

    resultado[
        "veredito_multivariado"
    ] = vm

    resultado[
        "classificacao_final"
    ] = vm[
        "classificacao_final"
    ]

    resultado[
        "justificativa_classificacao"
    ] = vm[
        "justificativa_classificacao"
    ]

    resultado[
        "evidencias_ausentes_classificacao"
    ] = vm[
        "evidencias_ausentes"
    ]

    return resultado

executar_pipeline_agent = _vs_historico_executar_pipeline_agent_1


# ============================================================
# VERITASSEC_PASSO1_FUNDAMENTACAO
#
# Wrapper preserva o contrato do pipeline.
# ============================================================

from functools import wraps as _wraps_passo1


_executar_pipeline_agent_sem_fundamentacao_passo1 = (
    executar_pipeline_agent
)


@_wraps_passo1(
    _executar_pipeline_agent_sem_fundamentacao_passo1
)
def _vs_historico_executar_pipeline_agent_2(*args, **kwargs):

    from .fundamentacao import (
        anexar_fundamentacao_tecnica,
    )

    resultado = (
        _executar_pipeline_agent_sem_fundamentacao_passo1(
            *args,
            **kwargs,
        )
    )

    return anexar_fundamentacao_tecnica(
        resultado
    )

executar_pipeline_agent = _vs_historico_executar_pipeline_agent_2



# ============================================================
# VERITASSEC_ETAPA03_XAI
#
# Acrescenta rastreabilidade sem reclassificar achados.
# Preserva todos os wrappers preexistentes do pipeline.
# ============================================================

from functools import wraps as _vs_xai_wraps

from .explicabilidade_xai import (
    anexar_explicabilidade_xai,
)

_vs_pipeline_anterior_xai = executar_pipeline_agent


@_vs_xai_wraps(_vs_pipeline_anterior_xai)
def _vs_historico_executar_pipeline_agent_3(*args, **kwargs):
    resultado = _vs_pipeline_anterior_xai(
        *args,
        **kwargs,
    )

    return anexar_explicabilidade_xai(
        resultado
    )

executar_pipeline_agent = _vs_historico_executar_pipeline_agent_3


# VERITASSEC_CONTRATO_OPERACIONAL_EVIDENCIAS_V1
# Não modifica classificação. Expõe lacunas verificáveis para XAI e interface.
_vs_pipeline_xai_pre_contrato = executar_pipeline_agent

@_vs_xai_wraps(_vs_pipeline_xai_pre_contrato)

# VERITASSEC_DAST_PIPELINE_XAI_V1
# Evidencias previamente coletadas; sem novas requisicoes de rede.
def _vs_extrair_contexto_dast(achado):
    campo = "evidencias_dast_correlacionadas"

    if isinstance(achado, dict):
        contexto = achado.get(campo)
        entrada = dict(achado)
        entrada.pop(campo, None)
    else:
        contexto = getattr(achado, campo, None)
        entrada = achado

    if not isinstance(contexto, dict):
        return entrada, None

    correlacoes = contexto.get("correlacoes", [])
    alertas = contexto.get("alertas", [])
    # VERITASSEC_DAST_CONTEXTUAL_PIPELINE_V1
    associacoes = contexto.get("associacoes_contextuais", [])

    if not isinstance(correlacoes, list):
        correlacoes = []
    if not isinstance(alertas, list):
        alertas = []
    if not isinstance(associacoes, list):
        associacoes = []

    import json as _vs_json

    def _vs_unicos(itens):
        vistos = set()
        saida = []

        for item in itens:
            if not isinstance(item, dict):
                continue

            chave = _vs_json.dumps(
                item,
                sort_keys=True,
                ensure_ascii=False,
                default=str,
            )

            if chave not in vistos:
                vistos.add(chave)
                saida.append(item)

        return saida

    contexto_limpo = {
        "origem": "OWASP ZAP",
        "correlacoes": _vs_unicos(correlacoes),
        "associacoes_contextuais": _vs_unicos(associacoes),
        "alertas": _vs_unicos(alertas),
        "estado": "CORRELACAO_NAO_CONFIRMATORIA",
        "propriedade_seguranca_comprovada": False,
        "investigacao_adicional_necessaria": True,
    }

    # VERITASSEC_DAST_SETE_AGENTES_V2
    if isinstance(entrada, dict):
        entrada[campo] = contexto_limpo
    elif hasattr(entrada, "model_copy"):
        entrada = entrada.model_copy(
            update={campo: contexto_limpo}
        )

    return entrada, contexto_limpo


def _vs_anexar_contexto_dast(resultado, contexto):
    if contexto is None:
        return resultado

    if not isinstance(resultado, dict):
        raise TypeError("RESULTADO_PIPELINE_INVALIDO")

    resultado["evidencias_dast_correlacionadas"] = contexto

    # Nao confundir observacao do ZAP com execucao de um
    # oraculo especifico de seguranca.
    resultado["avaliacao_dast_preexistente"] = {
        "estado": "NAO_CONFIRMATORIO",
        "fonte": "OWASP ZAP",
        "correlacoes": len(contexto["correlacoes"]),
        "associacoes_contextuais": len(
            contexto.get("associacoes_contextuais", [])
        ),
        "alertas": len(contexto["alertas"]),
        "security_oracle_executado_nesta_etapa": False,
        "propriedade_seguranca_comprovada": False,
        "motivo": (
            "Alertas e correlacoes nao comprovam "
            "isoladamente uma vulnerabilidade."
        ),
    }

    # Recalcula somente a explicabilidade, sem reclassificar.
    from .explicabilidade_xai import (
        anexar_explicabilidade_xai,
    )

    resultado = anexar_explicabilidade_xai(resultado)

    xai = resultado.get("explicabilidade_xai")

    if not isinstance(xai, dict):
        raise TypeError("XAI_INVALIDO")

    xai["evidencias_dast_preexistentes"] = {
        "origem": "OWASP ZAP",
        "correlacoes_registradas": len(
            contexto["correlacoes"]
        ),
        "associacoes_contextuais_registradas": len(
            contexto.get("associacoes_contextuais", [])
        ),
        "alertas_registrados": len(
            contexto["alertas"]
        ),
        "disponibilizadas_aos_agentes": True,
        "consumidas_pelos_agentes": False,
        "consumo_pelos_agentes_comprovado": False,
        "utilizadas_para_reclassificacao": False,
        "carater": "NAO_CONFIRMATORIO",
    }

    return resultado


def executar_pipeline_agent(*args, **kwargs):
    _vs_contexto = None

    if args:
        _vs_entrada, _vs_contexto = (
            _vs_extrair_contexto_dast(args[0])
        )
        args = (_vs_entrada, *args[1:])

    elif "achado" in kwargs:
        _vs_entrada, _vs_contexto = (
            _vs_extrair_contexto_dast(kwargs["achado"])
        )
        kwargs = dict(kwargs)
        kwargs["achado"] = _vs_entrada

    resultado = _vs_pipeline_xai_pre_contrato(
        *args, **kwargs
    )

    resultado = _vs_anexar_contexto_dast(
        resultado, _vs_contexto
    )
    if not isinstance(resultado, dict):
        raise TypeError("RESULTADO_PIPELINE_INVALIDO")
    aquisicao = resultado.get("aquisicao_evidencia") or {}
    registros = aquisicao.get("resultados") or [] if isinstance(aquisicao, dict) else []
    confirmados = [r for r in registros if isinstance(r, dict) and r.get("executada") is True]
    zap = [r for r in confirmados if r.get("capacidade") == "zap"]
    oraculo = resultado.get("avaliacao_security_oracle_zap") or []
    vm = resultado.get("veredito_multivariado") or {}
    xai = resultado.get("explicabilidade_xai") or {}
    resultado["observabilidade_investigacao"] = {
        "aquisicoes_executadas": len(confirmados),
        "aquisicoes_zap_executadas": len(zap),
        "avaliacoes_oracle_registradas": len(oraculo) if isinstance(oraculo, list) else 0,
        "justificativa_presente": bool(resultado.get("justificativa_classificacao")),
        "xai_presente": bool(xai),
        "evidencias_ausentes": vm.get("evidencias_ausentes", []) if isinstance(vm, dict) else [],
        "aviso": "HTTP_200_NAO_CONFIRMA_VULNERABILIDADE",
    }
    return resultado


# VERITASSEC_ETAPA04_INTEGRACAO_DAST_V1
_vs_etapa04_sarif_original = executar_pipeline_sarif_agent

def executar_pipeline_sarif_agent(*args, **kwargs):
    resultado = _vs_etapa04_sarif_original(*args, **kwargs)
    import os as _vs_os
    if _vs_os.environ.get("VERITASSEC_DAST_INTEGRAR", "").lower() not in ("1", "true", "sim"):
        return resultado
    from .integracao_dast_pipeline import enriquecer_resultado_sarif
    return enriquecer_resultado_sarif(resultado)


# VERITASSEC_FASE09_EXTENSAO_SEMANTICA
def executar_correlacao_semantica(sarif, alertas):
    """Executa integração semântica sem alterar vereditos LLM."""
    from aplicacao.multiagente.integracao_semantica_dast import integrar
    return integrar(sarif, alertas)
