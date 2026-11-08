from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .executor import ExecutorFerramentas
from .modelos import (
    AchadoMultiagente,
    ArquiteturaMultiagente,
    EstadoPasso,
    EventoAgente,
    PapelAgente,
    ResultadoMultiagente,
)
from .raciocinio import MotorRaciocinioAgno
from .scr import executar_scr
from .telemetria_execucao import (
    emitir_progresso_operacional,
)

from .painel_papeis import (
    consultar as consultar_painel_papel,
    painel_pre_planejamento,
)
from .adversarial_duas_fases import (
    aplicar_fase1_na_hipotese,
    construir_contexto_fase1,
    consolidar_fase1,
)
from .registry import (
    DEFINICOES,
    REGISTRO_AGENTES,
)


def agora() -> str:
    return datetime.now(timezone.utc).isoformat()


class OrquestradorMultiagente:

    def __init__(self) -> None:
        self.registry = REGISTRO_AGENTES
        self.executor = ExecutorFerramentas()
        self.raciocinio = MotorRaciocinioAgno()

    def arquitetura(self) -> ArquiteturaMultiagente:

        capacidades = self.executor.capacidades()

        return ArquiteturaMultiagente(
            framework="Agno",
            quantidade_agentes=self.registry.quantidade(),
            agentes=[
                {
                    "papel": d.papel.value,
                    "nome": d.nome,
                    "funcao": d.funcao,
                }
                for d in DEFINICOES
            ],
            ferramentas_deterministicas=[
                nome
                for nome, info in capacidades.items()
                if info["ativa"]
            ],
            regra_confirmacao=(
                "Conclusão de agente não equivale a "
                "vulnerabilidade confirmada. Confirmação forte "
                "requer evidência dinâmica correlacionada a "
                "oráculo de segurança."
            ),
        )

    def investigar(
        self,
        achado: AchadoMultiagente,
    ) -> ResultadoMultiagente:

        inicio = agora()

        trilha: list[EventoAgente] = []
        evidencias: list[str] = []
        executadas: list[str] = []
        planejadas: list[str] = []

        seq = 0

        # VERITASSEC_DAST_SETE_AGENTES_V2
        contexto_dast = (
            achado.evidencias_dast_correlacionadas
            if isinstance(
                achado.evidencias_dast_correlacionadas,
                dict,
            )
            else {}
        )

        contexto_dast_agentes = {
            "origem": "OWASP ZAP",
            "correlacoes": contexto_dast.get(
                "correlacoes", []
            ),
            "alertas": contexto_dast.get(
                "alertas", []
            ),
            "carater": "NAO_CONFIRMATORIO",
            "exige_oraculo_independente": True,
        }

        def evento(
            papel: PapelAgente,
            funcao: str,
            decisao: str,
            ferramenta: str | None = None,
            entrada: dict[str, Any] | None = None,
            saida: dict[str, Any] | None = None,
            ev: list[str] | None = None,
            estado: EstadoPasso = EstadoPasso.CONCLUIDO,
            registro_precomputado: Any | None = None,
        ) -> None:

            nonlocal seq

            # Gate estrutural:
            # o papel precisa corresponder a uma instância Agent real.
            self.registry.obter(papel)

            # VERITASSEC_CORRECAO_PONTA_A_PONTA_20261027
            # Propagacao auditavel do contexto entre papeis.
            entrada_efetiva = dict(entrada or {})
            historico_agentes = []

            for anterior in trilha:
                saida_anterior = (
                    anterior.saida
                    if isinstance(anterior.saida, dict)
                    else {}
                )

                resumo = {
                    "papel": str(
                        getattr(
                            anterior.agente,
                            "value",
                            anterior.agente,
                        )
                    ),
                    "funcao": str(anterior.funcao)[:120],
                    "decisao": str(anterior.decisao)[:300],
                    "estado": str(
                        getattr(
                            anterior.estado,
                            "value",
                            anterior.estado,
                        )
                    ),
                    "dados": {},
                }

                for chave in (
                    "scr",
                    "endpoint",
                    "tipo",
                    "sustentacao_scr",
                    "lacunas",
                    "ferramentas_planejadas",
                    "motivos",
                    "evidencia_dinamica",
                    "evidencia_oraculo",
                ):
                    if chave in saida_anterior:
                        resumo["dados"][chave] = str(
                            saida_anterior[chave]
                        )[:450]

                historico_agentes.append(resumo)

            if historico_agentes:
                entrada_efetiva[
                    "contexto_agentes_anteriores"
                ] = historico_agentes

            contexto_cognitivo = {
                "achado": {
                    "id": achado.id,
                    "regra": achado.regra,
                    "cwe": achado.cwe,
                    "mensagem": achado.mensagem,
                    "arquivo": achado.arquivo,
                    "linha": achado.linha,
                    "endpoint": achado.endpoint,
                    "metodo_http": achado.metodo_http,
                },
                "entrada_etapa": entrada_efetiva,
                "evidencias_dast_correlacionadas": (
                    contexto_dast_agentes
                ),
                "saida_deterministica": saida or {},
                "evidencias_observadas": ev or [],
                "ferramenta_proposta": ferramenta,
            }

            # VERITASSEC_ETAPA1_AGENTES_ESPECIALIZADOS
            #
            # Cada um dos sete papeis executa sua
            # atividade cognitiva especializada.
            #
            # O painel multimodelo permanece como
            # mecanismo complementar de investigacao.
            #
            # Um registro precomputado so e reutilizado
            # quando representa deliberacao ja realizada,
            # como a primeira fase do critico adversarial.
            #
            # A politica deterministica continua sendo
            # a unica autoridade para executar ferramentas.

            if registro_precomputado is not None:

                registro_llm = registro_precomputado
                usar_decisao_llm = False

            else:

                registro_llm = self.raciocinio.decidir(
                    papel=papel,
                    objetivo=funcao,
                    contexto=contexto_cognitivo,
                    decisao_base=decisao,
                )

                usar_decisao_llm = True

            saida_evento = dict(
                saida or {}
            )

            saida_evento[
                "raciocinio_agente"
            ] = registro_llm.model_dump(
                mode="json"
            )

            # Se houve LLM real, a decisão textual exibida
            # pertence ao Agent. A execução de ferramenta,
            # entretanto, continua governada pela política.
            if (
                usar_decisao_llm
                and registro_llm
                .chamada_modelo_realizada
            ):
                decisao_evento = (
                    registro_llm
                    .decisao
                    .decisao
                )
            else:
                decisao_evento = decisao

            seq += 1

            # VERITASSEC_PASSO2_TELEMETRIA_AGENTES
            # VERITASSEC_PROVEDOR_RESULTADO_20261023
            emitir_progresso_operacional(
                etapa=funcao,
                provedor=(
                    registro_llm.provedor
                    if registro_llm.chamada_modelo_realizada
                    else None
                ),
                agente=str(
                    getattr(
                        papel,
                        "value",
                        papel,
                    )
                ),
                detalhe=(
                    "Evento cognitivo "
                    + str(seq)
                    + "/7"
                ),
            )

            trilha.append(
                EventoAgente(
                    sequencia=seq,
                    agente=papel,
                    funcao=funcao,
                    decisao=decisao_evento,
                    ferramenta=ferramenta,
                    entrada=entrada_efetiva,
                    saida=saida_evento,
                    evidencias=ev or [],
                    estado=estado,
                )
            )

        # ----------------------------------------------------
        # 1. ORQUESTRADOR
        # ----------------------------------------------------

        evento(
            PapelAgente.ORQUESTRADOR,
            "controle da investigação",
            (
                "Investigação iniciada dentro do escopo "
                "informado; nenhuma ampliação automática "
                "de alvo é permitida."
            ),
            "politica_deterministica",
            entrada={
                "achado_id": achado.id,
            },
        )

        # ----------------------------------------------------
        # 2. ANALISTA DE CÓDIGO
        # ----------------------------------------------------

        contexto = self.executor.adquirir_contexto_codigo(
            achado.arquivo,
            achado.linha,
        )
        scr = executar_scr(
            arquivo=achado.arquivo,
            linha=achado.linha,
            regra=achado.regra,
            cwe=achado.cwe,
            mensagem=achado.mensagem,
            endpoint=achado.endpoint,
            metodo_http=achado.metodo_http,
        )
        scr_dados = scr.dump()

        if contexto.get("executada"):
            executadas.append("busca_codigo")
            evidencias.append("contexto_codigo_observado")

            estado_codigo = EstadoPasso.CONCLUIDO
            decisao_codigo = (
                "Contexto estático adquirido diretamente "
                "do arquivo reportado."
            )
        else:
            estado_codigo = EstadoPasso.INCONCLUSIVO
            decisao_codigo = (
                "Não foi possível adquirir contexto estático "
                "do arquivo informado."
            )

        evento(
            PapelAgente.ANALISTA_CODIGO,
            "aquisição e interpretação estática",
            decisao_codigo,
            "busca_codigo",
            entrada={
                "arquivo": achado.arquivo,
                "linha": achado.linha,
            },
            saida={**contexto, "scr": scr_dados},
            ev=(
                ["contexto_codigo_observado"]
                if contexto.get("executada")
                else []
            ),
            estado=estado_codigo,
        )

        # ----------------------------------------------------
        # 3. SUPERFÍCIE DE ATAQUE
        # ----------------------------------------------------

        superficie = {
            "endpoint_informado": bool(achado.endpoint),
            "metodo_http_informado": bool(achado.metodo_http),
            "arquivo_observado": bool(
                contexto.get("executada")
            ),
        }

        if achado.endpoint:
            superficie["endpoint"] = achado.endpoint

        evento(
            PapelAgente.SUPERFICIE_ATAQUE,
            "análise de alcançabilidade e precondições",
            (
                "Superfície registrada somente com os dados "
                "observáveis disponíveis; alcançabilidade "
                "não é presumida."
            ),
            "analise_superficie",
            saida=superficie,
        )

        # ----------------------------------------------------
        # 4. HIPÓTESES
        # ----------------------------------------------------

        tipo = (
            achado.cwe
            or achado.regra
            or "tipo_nao_classificado"
        )

        hipotese = {
            "tipo": tipo,
            "scr": scr_dados,
            "sustentacao_scr": scr_dados.get(
                "nivel_sustentacao",
                "INCONCLUSIVO",
            ),
            "propriedade_seguranca": scr_dados.get(
                "propriedade_seguranca"
            ),
            "descricao": (
                f"O achado {achado.id} pode representar "
                f"{tipo}, mas requer evidência suficiente "
                "para sustentar o veredito."
            ),
            "testavel": True,
            "confirmada": False,
        }

        evento(
            PapelAgente.HIPOTESES,
            "formulação de hipótese causal testável",
            "Hipótese criada sem declarar confirmação.",
            "raciocinio_estruturado",
            saida=hipotese,
        )

        # ----------------------------------------------------

        # ====================================================
        # VERITASSEC_PASSO1_FASE1_INTERNA
        #
        # O mesmo critico_adversarial executa raciocínio
        # antes do Planejador, mas ainda NÃO registra
        # EventoAgente. O único evento desse agente será
        # registrado na etapa histórica 7, após validação.
        # ====================================================

        painel_fase1 = painel_pre_planejamento(
            achado=achado,
            contexto_codigo=contexto,
            scr=scr,
            superficie=superficie,
            hipotese=hipotese,
            evidencias=evidencias,
        )

        contexto_critico_fase1 = (
            construir_contexto_fase1(
                achado=achado,
                hipotese=hipotese,
                superficie=superficie,
                scr=scr,
                evidencias=evidencias,
                painel=painel_fase1,
            )
        )

        contexto_critico_fase1 = dict(
            contexto_critico_fase1
        )
        contexto_critico_fase1[
            "evidencias_dast_correlacionadas"
        ] = contexto_dast_agentes

        registro_critico_fase1 = (
            self.raciocinio.decidir(
                papel=PapelAgente.CRITICO,
                objetivo=(
                    "falsificação adversarial "
                    "pré-execução"
                ),
                contexto=contexto_critico_fase1,
                decisao_base=(
                    "Tentar refutar a hipótese e "
                    "explicitar evidências faltantes "
                    "antes do planejamento."
                ),
            )
        )

        critica_fase1 = consolidar_fase1(
            registro_agente=registro_critico_fase1,
            painel=painel_fase1,
        )

        aplicar_fase1_na_hipotese(
            hipotese=hipotese,
            fase1=critica_fase1,
        )

        # 5. PLANEJADOR
        # ----------------------------------------------------

        lacunas = list(
            scr_dados.get(
                "evidencias_ausentes",
                [],
            )
        )

        if not contexto.get("executada"):
            lacunas.append("contexto_codigo")

        lacunas.extend([
            "execucao_dinamica",
            "oraculo",
        ])

        regra = (
            f"{achado.regra} "
            f"{achado.cwe or ''} "
            f"{achado.mensagem}"
        ).lower()

        if any(
            x in regra
            for x in (
                "path traversal",
                "path-traversal",
                "cwe-22",
                "directory traversal",
            )
        ):
            planejadas.extend([
                "path_traversal",
                "busca_evolucionaria",
                "oraculo_path_traversal",
            ])

        if any(
            x in regra
            for x in (
                "authorization",
                "autorizacao",
                "autorização",
                "idor",
                "bola",
                "cwe-639",
                "cwe-862",
            )
        ):
            planejadas.extend([
                "runtime_http",
                "autorizacao_http",
                "oraculo_autorizacao",
            ])

        if contexto.get("executada"):
            planejadas.append(
                "revisao_codigo_seguro"
            )

        planejadas = list(
            dict.fromkeys(planejadas)
        )

        evento(
            PapelAgente.PLANEJADOR,
            "planejamento adaptativo",
            (
                "Próximas aquisições selecionadas conforme "
                "tipo do achado e lacunas de evidência."
            ),
            "planejamento_adaptativo",
            saida={
                "lacunas": lacunas,
                "ferramentas_planejadas": planejadas,
            },
        )

        # ----------------------------------------------------
        # 6. VALIDAÇÃO
        # ----------------------------------------------------

        capacidades = self.executor.capacidades()

        disponiveis = [
            nome
            for nome in planejadas
            if (
                nome in capacidades
                and capacidades[nome]["ativa"]
            )
        ]

        indisponiveis = [
            nome
            for nome in planejadas
            if nome not in disponiveis
        ]

        evidencia_dinamica = False
        evidencia_oraculo = False
        resultado_dinamico = None
        iteracoes = 1

        regra_path = any(
            x in regra
            for x in (
                "path traversal",
                "path-traversal",
                "directory traversal",
                "cwe-22",
            )
        )

        regra_auth = any(
            x in regra
            for x in (
                "authorization",
                "autorizacao",
                "autorização",
                "idor",
                "bola",
                "cwe-639",
                "cwe-862",
            )
        )


        if (
            regra_path
            and achado.execucao_dinamica_permitida
            and achado.raiz_sandbox
        ):
            resultado_dinamico = (
                self.executor
                .executar_path_traversal(
                    hipotese_id=achado.id,
                    raiz_sandbox=(
                        achado.raiz_sandbox
                    ),
                    sementes=achado.sementes,
                )
            )

            for nome in (
                "busca_evolucionaria",
                "path_traversal",
                "oraculo_path_traversal",
            ):
                if nome not in executadas:
                    executadas.append(nome)

            evidencia_dinamica = bool(
                resultado_dinamico.get(
                    "evidencia_dinamica"
                )
            )

            evidencia_oraculo = bool(
                resultado_dinamico.get(
                    "evidencia_oraculo"
                )
            )

            for digest in (
                resultado_dinamico
                .get("hashes", [])
            ):
                evidencias.append(
                    f"sha256:{digest}"
                )

            evento(
                PapelAgente.VALIDACAO,
                "execução dinâmica controlada",
                (
                    "Busca evolucionária, executor "
                    "controlado e oráculo executados "
                    "dentro da sandbox autorizada."
                ),
                "path_traversal",
                entrada={
                    "sandbox": (
                        achado.raiz_sandbox
                    ),
                    "sementes": (
                        achado.sementes
                    ),
                },
                saida={
                    **resultado_dinamico,
                    "execucao_dinamica_realizada": True,
                },
                ev=[
                    "execucao_dinamica_observada",
                    "oraculo_executado",
                ],
                estado=EstadoPasso.CONCLUIDO,
            )

        elif (
            regra_auth
            and achado.execucao_dinamica_permitida
            and achado.base_url_http
            and achado.caminho_http
            and achado.marcador_recurso
        ):
            resultado_dinamico = (
                self.executor
                .executar_autorizacao_http(
                    base_url=achado.base_url_http,
                    caminho=achado.caminho_http,
                    marcador=achado.marcador_recurso,
                    transport=(
                        achado.metadados.get(
                            "_transport_http"
                        )
                    ),
                )
            )

            for nome in (
                "runtime_http",
                "autorizacao_http",
                "oraculo_autorizacao",
            ):
                if nome not in executadas:
                    executadas.append(nome)

            evidencia_dinamica = bool(
                resultado_dinamico.get(
                    "executada",
                    False,
                )
            )

            evidencia_oraculo = bool(
                resultado_dinamico.get(
                    "resultado_oraculo"
                )
            )

            evento(
                PapelAgente.VALIDACAO,
                "execução dinâmica HTTP controlada",
                (
                    "Executor HTTP controlado e oráculo "
                    "de autorização executados sobre alvo "
                    "explicitamente autorizado."
                ),
                "autorizacao_http",
                entrada={
                    "base_url": (
                        achado.base_url_http
                    ),
                    "caminho": (
                        achado.caminho_http
                    ),
                },
                saida={
                    **resultado_dinamico,
                    "execucao_dinamica_realizada": True,
                },
                ev=[
                    "execucao_dinamica_http_observada",
                    "oraculo_autorizacao_executado",
                ],
                estado=EstadoPasso.CONCLUIDO,
            )

        else:
            motivos = []

            if not regra_path and not regra_auth:
                motivos.append(
                    "classe_sem_executor_dinamico_integrado"
                )

            if (
                regra_auth
                and not achado.execucao_dinamica_permitida
            ):
                motivos.append(
                    "execucao_dinamica_nao_autorizada"
                )

            if (
                regra_auth
                and achado.execucao_dinamica_permitida
                and not achado.base_url_http
            ):
                motivos.append(
                    "base_url_http_nao_informada"
                )

            if (
                regra_auth
                and achado.execucao_dinamica_permitida
                and not achado.caminho_http
            ):
                motivos.append(
                    "caminho_http_nao_informado"
                )

            if (
                regra_auth
                and achado.execucao_dinamica_permitida
                and not achado.marcador_recurso
            ):
                motivos.append(
                    "marcador_recurso_nao_informado"
                )

            if (
                regra_path
                and not
                achado.execucao_dinamica_permitida
            ):
                motivos.append(
                    "execucao_dinamica_nao_autorizada"
                )

            if (
                regra_path
                and achado.execucao_dinamica_permitida
                and not achado.raiz_sandbox
            ):
                motivos.append(
                    "sandbox_nao_informada"
                )

            evento(
                PapelAgente.VALIDACAO,
                "coordenação de validação controlada",
                (
                    "Nenhuma execução dinâmica foi "
                    "realizada; nenhuma evidência foi "
                    "presumida."
                ),
                "catalogo_ferramentas",
                saida={
                    "disponiveis": disponiveis,
                    "indisponiveis": indisponiveis,
                    "motivos": motivos,
                    "execucao_dinamica_realizada": False,
                },
                estado=(
                    EstadoPasso.INCONCLUSIVO
                    if planejadas
                    else EstadoPasso.BLOQUEADO
                ),
            )

        # ----------------------------------------------------
        # 7. CRÍTICO ADVERSARIAL — FASE 2 (PÓS-EVIDÊNCIA)
        # ----------------------------------------------------

        violacao_confirmada = bool(
            resultado_dinamico
            and resultado_dinamico.get(
                "violacao_confirmada",
                False,
            )
        )

        if (
            evidencia_dinamica
            and evidencia_oraculo
            and violacao_confirmada
        ):
            critica = (
                "Execução dinâmica reproduzível e "
                "oráculo confirmaram violação da "
                "propriedade de segurança."
            )

            estado_final = (
                "REPRODUZIDO_DINAMICAMENTE"
            )

            motivo = (
                "EVIDENCIA_SUFICIENTE_CONFIRMADA"
            )

        elif (
            evidencia_dinamica
            and evidencia_oraculo
            and not violacao_confirmada
        ):
            critica = (
                "Execução dinâmica e oráculo foram "
                "realizados, mas a violação não foi "
                "reproduzida nas condições testadas."
            )

            estado_final = "NAO_REPRODUZIDO"

            motivo = (
                "EVIDENCIA_SUFICIENTE_REFUTADA"
            )

        elif not evidencia_dinamica:
            critica = (
                "Hipótese não pode ser confirmada: "
                "não existe evidência dinâmica "
                "observada."
            )

            estado_final = (
                "EVIDENCIA_INSUFICIENTE"
            )

            motivo = (
                "EVIDENCIA_DINAMICA_AUSENTE"
            )

        else:
            critica = (
                "Existe execução dinâmica, mas "
                "não há oráculo suficiente."
            )

            estado_final = "INCONCLUSIVO"
            motivo = "ORACULO_AUSENTE"


        # VERITASSEC_LATENCIA_FASE2_SEM_EVIDENCIA_20261019
        #
        # Se nenhuma nova evidência dinâmica/oráculo foi obtida,
        # não existe informação adicional que justifique uma
        # segunda rodada multimodelo externa.
        #
        # O crítico adversarial fase 2 continua executando pela
        # regra determinística de suficiência de evidência.
        if (
            evidencia_dinamica
            or evidencia_oraculo
        ):
            painel_fase2 = consultar_painel_papel(
                papel="critico_adversarial",
                contexto={
                    "fase1": critica_fase1,
                    "hipotese": hipotese,
                    "evidencias": evidencias,
                    "evidencia_dinamica":
                        evidencia_dinamica,
                    "evidencia_oraculo":
                        evidencia_oraculo,
                    "violacao_confirmada":
                        violacao_confirmada,
                    "analise_suficiencia":
                        critica,
                    "estado_proposto":
                        estado_final,
                },
                finding_id=str(achado.id),
                fase="pos_evidencia",
            )
        else:
            painel_fase2 = {
                "habilitado": False,
                "motivo": (
                    "sem_nova_evidencia_"
                    "dinamica_ou_oraculo"
                ),
                "fase": "pos_evidencia",
                "autoridade_decisoria": False,
            }

        hipotese[
            "critica_adversarial_fase2"
        ] = {
            "fase":
                "pos_evidencia",

            "analise_deterministica":
                critica,

            "painel_multimodelo":
                painel_fase2,

            "estado_proposto":
                estado_final,
        }

        # O crítico continua sendo o sétimo agente.
        evento(
            PapelAgente.CRITICO,
            (
                "refutação adversarial e "
                "suficiência de evidência"
            ),
            critica,
            "regra_suficiencia_evidencia",
            saida={
                "evidencia_dinamica": (
                    evidencia_dinamica
                ),
                "evidencia_oraculo": (
                    evidencia_oraculo
                ),
                "violacao_confirmada": (
                    violacao_confirmada
                ),
                "estado_proposto": (
                    estado_final
                ),
            },
            registro_precomputado=registro_critico_fase1,
        )

        # ----------------------------------------------------
        # REPLANEJAMENTO
        #
        # IMPORTANTE:
        # replanejamento é estado interno do Planejador.
        # NÃO adiciona outro EventoAgente e NÃO transforma
        # os 7 agentes em 8 execuções.
        # ----------------------------------------------------

        if (
            estado_final
            in {
                "EVIDENCIA_INSUFICIENTE",
                "INCONCLUSIVO",
            }
            and achado.max_iteracoes > 1
        ):
            iteracoes = 2

            # Atualiza a saída do evento original do Planejador.
            for passo in trilha:
                if (
                    passo.agente
                    == PapelAgente.PLANEJADOR
                ):
                    passo.saida[
                        "replanejamento"
                    ] = {
                        "realizado": True,
                        "iteracao": 2,
                        "nova_acao": None,
                        "motivo": (
                            "nenhuma_nova_acao_autorizada_"
                            "com_ganho_de_informacao"
                        ),
                    }
                    break

        return ResultadoMultiagente(
            achado_id=achado.id,
            agentes_executados=[
                e.agente
                for e in trilha
            ],
            trilha=trilha,
            ferramentas_planejadas=planejadas,
            ferramentas_executadas=executadas,
            evidencias=evidencias,
            hipotese=hipotese,
            lacunas=lacunas,
            evidencia_dinamica=evidencia_dinamica,
            evidencia_oraculo=evidencia_oraculo,
            estado_final=estado_final,
            motivo_termino=motivo,
            iteracoes=iteracoes,
            inicio=inicio,
            fim=agora(),
        )
