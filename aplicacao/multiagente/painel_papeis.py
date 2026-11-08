from __future__ import annotations

"""
Local, GPT e Gemini são provedores de raciocínio.

Eles NÃO são agentes adicionais.
Eles NÃO autorizam ferramentas.
Eles NÃO executam ferramentas.
Eles NÃO produzem o veredito final.
"""

from concurrent.futures import (
    ThreadPoolExecutor,
)

import json
import os

from pathlib import Path
from typing import Any
from .telemetria_execucao import (
    vincular_execucao,
    job_atual,
    emitir_progresso_operacional,
)



CAMPOS_PROIBIDOS = (
    "ground_truth",
    "groundtruth",
    "validacao_manual",
    "rotulo_manual",
    "rótulo_manual",
    "label_manual",
    "veredito_final",
    "classificacao_final",
)


PAPEIS = {
    "analista_codigo",
    "superficie_ataque",
    "hipoteses",
    "planejador",
    "validacao",
    "critico_adversarial",
}


def habilitado() -> bool:

    # VERITASSEC_EVITAR_CONSULTA_MULTIPLA_20261022
    # O Agno já distribui as inferências dos agentes.
    # Evita consultar novamente todos os provedores.
    if (
        os.getenv(
            "VERITASSEC_PROVEDORES_PAPEIS", ""
        ).strip()
        and os.getenv(
            "IA_HABILITADA", ""
        ).lower() in {
            "1",
            "true",
            "sim",
            "yes",
            "on",
        }
    ):
        return False


    valor = os.getenv(
        "VERITASSEC_MULTIMODELO_PAPEIS",
        "false",
    )

    return (
        valor.strip().lower()
        in {
            "1",
            "true",
            "sim",
            "yes",
            "on",
        }
    )


def sanitizar(
    valor: Any,
) -> Any:

    if isinstance(valor, dict):

        resultado = {}

        for chave, sub in valor.items():

            nome = str(chave).lower()

            if any(
                proibido in nome
                for proibido in CAMPOS_PROIBIDOS
            ):
                continue

            resultado[str(chave)] = (
                sanitizar(sub)
            )

        return resultado

    if isinstance(
        valor,
        (
            list,
            tuple,
            set,
        ),
    ):
        return [
            sanitizar(x)
            for x in valor
        ]

    if isinstance(
        valor,
        (
            str,
            int,
            float,
            bool,
            type(None),
        ),
    ):
        return valor

    if hasattr(
        valor,
        "model_dump",
    ):
        try:
            return sanitizar(
                valor.model_dump()
            )
        except Exception:
            pass

    if hasattr(
        valor,
        "__dict__",
    ):
        try:
            return sanitizar(
                vars(valor)
            )
        except Exception:
            pass

    return repr(valor)


def _modelos() -> tuple[str, str]:

    cfg = (
        Path.home()
        / ".config"
        / "veritassec"
        / "multimodel"
    )

    env_file = (
        cfg
        / "modelos.env"
    )

    valores = {}

    if env_file.is_file():

        for linha in env_file.read_text(
            encoding="utf-8"
        ).splitlines():

            linha = linha.strip()

            if (
                not linha
                or linha.startswith("#")
                or "=" not in linha
            ):
                continue

            chave, valor = linha.split(
                "=",
                1,
            )

            valores[
                chave.strip()
            ] = (
                valor.strip()
                .strip('"')
                .strip("'")
            )

    openai_model = (
        os.getenv(
            "VERITASSEC_OPENAI_MODEL"
        )
        or valores.get(
            "VERITASSEC_OPENAI_MODEL"
        )
        or ""
    )

    gemini_model = (
        os.getenv(
            "VERITASSEC_GEMINI_MODEL"
        )
        or valores.get(
            "VERITASSEC_GEMINI_MODEL"
        )
        or ""
    )

    if not openai_model:
        raise RuntimeError(
            "Modelo OpenAI ausente"
        )

    if not gemini_model:
        raise RuntimeError(
            "Modelo Gemini ausente"
        )

    return (
        openai_model,
        gemini_model,
    )


def _gestor():

    # Imports somente quando o multimodelo
    # estiver realmente habilitado.
    from aplicacao.llm import (
        criar_gestor_padrao,
        criar_registro_provedores,
    )

    from aplicacao.llm.provedores_externos import (
        ProvedorGeminiREST,
        ProvedorOpenAIResponses,
    )

    from aplicacao.llm.runtime_local import (
        criar_provedor_runtime_local,
    )

    cfg = (
        Path.home()
        / ".config"
        / "veritassec"
        / "multimodel"
    )

    openai_key = cfg / "openai-api-key"
    gemini_key = cfg / "gemini-api-key"

    if not openai_key.is_file():
        raise RuntimeError(
            "Credencial OpenAI ausente"
        )

    if not gemini_key.is_file():
        raise RuntimeError(
            "Credencial Gemini ausente"
        )

    openai_model, gemini_model = (
        _modelos()
    )

    registro = criar_registro_provedores(
        local=
            criar_provedor_runtime_local(),

        gpt=
            ProvedorOpenAIResponses(
                modelo=openai_model,
                api_key_file=openai_key,
            ),

        gemini=
            ProvedorGeminiREST(
                modelo=gemini_model,
                api_key_file=gemini_key,
            ),
    )

    return criar_gestor_padrao(
        registro,

        max_tokens_saida_por_agente={
            "analista_codigo": 320,
            "superficie_ataque": 320,
            "hipoteses": 380,
            "planejador": 320,
            "validacao": 380,
            "critico_adversarial": 400,
        },
    )


def _instrucao(
    papel: str,
    fase: str | None,
) -> str:

    especifico = {
        "analista_codigo": (
            "Avalie código, source, sink, fluxo, "
            "sanitização, guards, framework e reachability."
        ),

        "superficie_ataque": (
            "Avalie entry points, endpoints, parâmetros "
            "controláveis, autenticação e pré-condições."
        ),

        "hipoteses": (
            "Formule hipóteses verificáveis e refutáveis, "
            "indicando evidências necessárias."
        ),

        "planejador": (
            "Identifique evidências faltantes e mecanismos "
            "adequados para obtê-las. Não autorize execução."
        ),

        "validacao": (
            "Avalie suficiência, causalidade, limitações "
            "e contradições das evidências."
        ),

        "critico_adversarial": (
            "Tente refutar ativamente a hipótese ou a "
            "interpretação da evidência. Procure explicações "
            "alternativas e saltos lógicos."
        ),
    }

    texto = (
        "Você é um provedor de raciocínio utilizado por "
        "um papel cognitivo do VeritasSec. Você não é um "
        "agente adicional. Não autorize ou execute ferramentas. "
        "Não produza o veredito final. Não invente fatos. "
        "Consenso entre modelos não constitui prova. "
        "NAO_REPRODUZIDO não significa automaticamente "
        "FALSO_POSITIVO.\n\n"
        + especifico[papel]
    )

    if papel == "critico_adversarial":
        texto += (
            "\nFASE_ADVERSARIAL="
            + str(fase or "nao_informada")
        )

    texto += (
        '\nRetorne somente JSON: '
        '{"observacoes":[],'
        '"hipoteses":[],'
        '"lacunas":[],'
        '"objecoes":[],'
        '"recomendacoes":[]}'
    )

    return texto


def _parse(
    texto: str,
) -> dict[str, Any]:

    bruto = texto.strip()

    if bruto.startswith("```"):
        bruto = (
            bruto
            .replace(
                "```json",
                "",
                1,
            )
            .replace(
                "```",
                "",
            )
            .strip()
        )

    try:
        resultado = json.loads(
            bruto
        )
    except Exception:
        resultado = {
            "observacoes": [
                bruto[:2000]
            ],
            "hipoteses": [],
            "lacunas": [
                "resposta_nao_estruturada"
            ],
            "objecoes": [],
            "recomendacoes": [],
        }

    if not isinstance(
        resultado,
        dict,
    ):
        resultado = {
            "observacoes": [
                str(resultado)[:2000]
            ]
        }

    # Mesmo se o provedor tentar retornar veredito,
    # ele é removido.
    for chave in list(resultado):
        nome = str(chave).lower()

        if (
            "veredito" in nome
            or "classificacao_final" in nome
            or "ground_truth" in nome
        ):
            resultado.pop(
                chave,
                None,
            )

    for campo in (
        "observacoes",
        "hipoteses",
        "lacunas",
        "objecoes",
        "recomendacoes",
    ):
        valor = resultado.get(
            campo,
            [],
        )

        if isinstance(valor, str):
            valor = [valor]

        if not isinstance(valor, list):
            valor = [str(valor)]

        resultado[campo] = [
            str(x)[:1500]
            for x in valor[:20]
        ]

    return resultado


def consultar(
    *,
    papel: str,
    contexto: dict[str, Any],
    finding_id: str,
    fase: str | None = None,
) -> dict[str, Any]:

    if papel not in PAPEIS:
        return {
            "habilitado": False,
            "motivo": "papel_nao_suportado",
        }

    if not habilitado():
        return {
            "habilitado": False,
            "motivo": "multimodelo_desabilitado",
        }

    try:
        gestor = _gestor()

        from aplicacao.llm import (
            Evidencia,
            SolicitacaoLLM,
        )

    except Exception as exc:
        return {
            "habilitado": True,
            "status": "INDISPONIVEL",
            "erro": type(exc).__name__,
            "detalhe": str(exc)[:500],
        }

    contexto_limpo = sanitizar(
        contexto
    )

    # VERITASSEC_CORRECAO_CONTEXTO_PROVEDOR
    _job_telemetria = job_atual()

    def _executar_provedor_com_telemetria(provedor: str):
        vincular_execucao(_job_telemetria)
        try:
            return executar(provedor)
        finally:
            vincular_execucao(None)

    def executar(provedor: str):

        # VERITASSEC_PASSO2_TELEMETRIA_PROVEDORES
        emitir_progresso_operacional(
            etapa=(
                "raciocinio_multimodelo_"
                + papel
            ),
            agente=papel,
            provedor=provedor,
        )

        evidencia = Evidencia(
            id=(
                f"CTX-{finding_id}-"
                f"{papel}-{provedor}"
            ),
            fonte="contexto_agente",
            conteudo=json.dumps(
                contexto_limpo,
                ensure_ascii=False,
                sort_keys=True,
                default=str,
            ),
        )

        r = gestor.executar(
            provedor,

            SolicitacaoLLM(
                prompt_sistema=
                    _instrucao(
                        papel,
                        fase,
                    ),

                prompt_usuario=(
                    "Execute a análise técnica "
                    "correspondente ao papel."
                ),

                evidencias=(
                    evidencia,
                ),

                max_tokens_saida=400,
                temperatura=0.0,

                metadados={
                    "execution_id":
                        "papel-multimodelo",

                    "finding_id":
                        finding_id,

                    "agente":
                        papel,
                },
            ),
        )

        return {
            "provedor":
                provedor,

            "modelo":
                r.resposta.modelo,

            "analise":
                _parse(
                    r.resposta.texto
                ),

            "tokens_total":
                r.resposta.uso.total,

            "cache_hit":
                bool(r.cache_hit),
        }

    provedores = (
        "local",
        "gpt",
        "gemini",
    )

    respostas = {}

    with ThreadPoolExecutor(
        max_workers=3
    ) as pool:

        futuros = {
            p: pool.submit(
                _executar_provedor_com_telemetria,
                p,
            )
            for p in provedores
        }

        for p in provedores:

            try:
                respostas[p] = (
                    futuros[p].result()
                )

            except Exception as exc:
                respostas[p] = {
                    "provedor": p,
                    "status": "INDISPONIVEL",
                    "erro":
                        type(exc).__name__,
                    "detalhe":
                        str(exc)[:500],
                }

    return {
        "habilitado": True,
        "papel": papel,
        "fase": fase,
        "provedores": respostas,
        "autoridade_decisoria": False,
    }


def _consolidar(
    painel: dict[str, Any],
    campo: str,
) -> list[str]:

    resultado = []

    provedores = painel.get(
        "provedores",
        {},
    )

    if not isinstance(
        provedores,
        dict,
    ):
        return resultado

    for nome in (
        "local",
        "gpt",
        "gemini",
    ):

        item = provedores.get(
            nome,
            {},
        )

        analise = item.get(
            "analise",
            {},
        )

        valores = analise.get(
            campo,
            [],
        )

        if isinstance(valores, str):
            valores = [valores]

        if not isinstance(valores, list):
            continue

        for valor in valores:
            texto = str(valor).strip()

            if (
                texto
                and texto not in resultado
            ):
                resultado.append(texto)

    return resultado[:40]


def painel_pre_planejamento(
    *,
    achado: Any,
    contexto_codigo: Any,
    scr: Any,
    superficie: Any,
    hipotese: Any,
    evidencias: Any,
) -> dict[str, Any]:

    finding_id = str(
        getattr(
            achado,
            "id",
            "",
        )
    )

    base = {
        "achado":
            sanitizar(achado),

        "contexto_codigo":
            sanitizar(
                contexto_codigo
            ),

        "scr":
            sanitizar(scr),

        "superficie":
            sanitizar(superficie),

        "hipotese":
            sanitizar(hipotese),

        "evidencias":
            sanitizar(evidencias),
    }

    paineis = {}

    for papel in (
        "analista_codigo",
        "superficie_ataque",
        "hipoteses",
    ):

        paineis[papel] = consultar(
            papel=papel,
            contexto=base,
            finding_id=finding_id,
            fase="pre_planejamento",
        )

    contexto_critico = dict(base)

    contexto_critico[
        "analises_multimodelo"
    ] = paineis

    paineis[
        "critico_adversarial"
    ] = consultar(
        papel="critico_adversarial",
        contexto=contexto_critico,
        finding_id=finding_id,
        fase="pre_execucao",
    )

    hipoteses = []
    lacunas = []
    objecoes = []

    for papel, painel in paineis.items():

        hipoteses.extend(
            _consolidar(
                painel,
                "hipoteses",
            )
        )

        lacunas.extend(
            _consolidar(
                painel,
                "lacunas",
            )
        )

        if papel == "critico_adversarial":
            objecoes.extend(
                _consolidar(
                    painel,
                    "objecoes",
                )
            )

    return {
        "paineis": paineis,

        "hipoteses_candidatas":
            list(
                dict.fromkeys(
                    hipoteses
                )
            ),

        "lacunas":
            list(
                dict.fromkeys(
                    lacunas
                )
            ),

        "objecoes":
            list(
                dict.fromkeys(
                    objecoes
                )
            ),

        "autoridade_decisoria":
            False,
    }
