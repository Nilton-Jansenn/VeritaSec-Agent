from __future__ import annotations

import json
import os
import threading
import time
import uuid
from pathlib import Path

from fastapi import Body, HTTPException
from fastapi.responses import FileResponse

from pydantic import BaseModel, Field

from aplicacao.ui.interface_agent import (
    pagina_interface,
)


ROOT = Path(__file__).resolve().parents[2]

SAIDAS = Path(
    os.getenv(
        "VERITASSEC_SAIDAS_DIR",
        str(
            Path.home()
            / "Documentos"
            / "Projetos"
            / "VeritasSec-Agent-Saidas"
        ),
    )
).resolve()

INPUT = (ROOT / "input").resolve()
PROJECTS = (INPUT / "projects").resolve()
SARIFS = (INPUT / "sarif").resolve()

OUTPUT = (
    SAIDAS / "resultados"
).resolve()

CONFIG_DIR = (
    SAIDAS / "config"
).resolve()

CONFIG_FILE = (
    CONFIG_DIR / "interface.json"
)

for diretorio in (
    PROJECTS,
    SARIFS,
    OUTPUT,
    CONFIG_DIR,
):
    diretorio.mkdir(
        parents=True,
        exist_ok=True,
    )


_KEYS: dict[str, str] = {}

_ANALISE_JOBS: dict[str, dict] = {}

_ANALISE_JOBS_LOCK = (
    threading.RLock()
)

# Uma análise completa por processo.
#
# As configurações da IA e a chave do provedor pertencem
# ao processo da aplicação. Serializar a análise evita que
# dois jobs alterem esse contexto simultaneamente.
_ANALISE_EXECUCAO_LOCK = (
    threading.Lock()
)


DEFAULT = {
    "provedor": "gemini",
    "modelo": "",
    "timeout": 120,
    "max_tokens": 2500,
    "temperatura": 0.1,
}


MODELOS_SUPORTADOS: dict[str, tuple[str, ...]] = {
    "openai": (
        "gpt-4o-mini",
        "gpt-5.4",
    ),
    "gemini": (
        "gemini-2.5-flash",
        "gemini-3.1-pro-preview",
    ),
    "ollama": (
        "qwen2.5-coder:7b",
    ),
}



class ConfigInterface(BaseModel):

    provedor: str
    modelo: str
    timeout: int = Field(
        ge=1,
        le=3600,
    )

    max_tokens: int = Field(
        ge=1,
        le=200000,
    )

    temperatura: float = Field(
        ge=0,
        le=2,
    )


class ChaveInterface(BaseModel):

    provedor: str

    api_key: str = Field(
        min_length=8,
        max_length=2000,
    )


class AnaliseInterface(BaseModel):

    projeto: str
    sarif: str



    subdiretorio_saida: str = Field(
        default="interface",
        min_length=1,
        max_length=180,
    )


def carregar_config():

    if not CONFIG_FILE.exists():
        return dict(DEFAULT)

    try:

        dados = json.loads(
            CONFIG_FILE.read_text(
                encoding="utf-8"
            )
        )

        permitidas = set(
            DEFAULT
        )

        return {
            **DEFAULT,
            **{
                chave: valor
                for chave, valor
                in dados.items()
                if chave in permitidas
            },
        }

    except Exception:
        return dict(DEFAULT)


def caminho_seguro(
    base: Path,
    relativo: str,
    exigir_existencia: bool = False,
):

    if (
        not relativo
        or "\x00" in relativo
    ):
        raise HTTPException(
            status_code=400,
            detail="Caminho invalido.",
        )

    p = Path(relativo)

    if p.is_absolute():
        raise HTTPException(
            status_code=400,
            detail=(
                "Caminho absoluto "
                "nao permitido."
            ),
        )

    base = base.resolve()

    alvo = (
        base / p
    ).resolve()

    try:
        alvo.relative_to(base)

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=(
                "Caminho fora da "
                "area autorizada."
            ),
        ) from exc

    if (
        exigir_existencia
        and not alvo.exists()
    ):
        raise HTTPException(
            status_code=404,
            detail=(
                "Caminho nao encontrado."
            ),
        )

    return alvo


def relativo(
    base: Path,
    caminho: Path,
):

    return (
        caminho
        .resolve()
        .relative_to(base.resolve())
        .as_posix()
    )


def interface_html():

    return pagina_interface()


def obter_config():

    cfg = carregar_config()

    return {
        **cfg,
        "modelos_disponiveis": {
            provedor: list(modelos)
            for provedor, modelos
            in MODELOS_SUPORTADOS.items()
        },
        "api_key_necessaria": (
            cfg["provedor"]
            in {
                "openai",
                "gemini",
            }
        ),
        "api_key_configurada":
            bool(
                _KEYS.get(
                    cfg["provedor"]
                )
            ),
    }


def salvar_config(
    req: ConfigInterface,
):

    if req.provedor not in {
        "openai",
        "gemini",
        "ollama",
    }:
        raise HTTPException(
            status_code=400,
            detail="Provedor invalido.",
        )


    modelos_provedor = (
        MODELOS_SUPORTADOS.get(
            req.provedor,
            (),
        )
    )

    if req.modelo not in modelos_provedor:

        raise HTTPException(
            status_code=400,
            detail=(
                "Modelo invalido para o provedor "
                f"{req.provedor}: {req.modelo}"
            ),
        )


    CONFIG_FILE.write_text(
        json.dumps(
            req.model_dump(),
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    return {
        **req.model_dump(),
        "api_key_configurada":
            bool(
                _KEYS.get(
                    req.provedor
                )
            ),
    }


def carregar_chave(
    req: ChaveInterface,
):

    if req.provedor not in {
        "openai",
        "gemini",
    }:
        raise HTTPException(
            status_code=400,
            detail=(
                "API key nao aplicavel "
                "ao provedor."
            ),
        )

    _KEYS[
        req.provedor
    ] = req.api_key

    # A chave permanece somente na memória deste processo.
    # Os clientes LLM existentes consomem estas variáveis.
    if req.provedor == "gemini":
        os.environ["GEMINI_API_KEY"] = req.api_key
        os.environ["CHAVE_GEMINI"] = req.api_key

    elif req.provedor == "openai":
        os.environ["OPENAI_API_KEY"] = req.api_key

    return {
        "status": "OK",
        "provedor": req.provedor,
        "api_key_configurada": True,
    }


def remover_chave(
    provedor: str,
):

    _KEYS.pop(
        provedor,
        None,
    )

    # Remover também a cópia em memória utilizada pelo cliente LLM.
    if provedor == "gemini":
        os.environ.pop("GEMINI_API_KEY", None)
        os.environ.pop("CHAVE_GEMINI", None)

    elif provedor == "openai":
        os.environ.pop("OPENAI_API_KEY", None)

    return {
        "status": "OK",
        "provedor": provedor,
        "api_key_configurada": False,
    }


def testar_conexao():

    cfg = carregar_config()

    return {
        "status": "CONFIGURADO",
        "provedor": cfg["provedor"],
        "modelo": cfg["modelo"],
        "api_key_configurada":
            bool(
                _KEYS.get(
                    cfg["provedor"]
                )
            ),
        "fail_closed": True,
    }


def listar_inputs():

    projetos = []

    for p in sorted(
        PROJECTS.iterdir(),
        key=lambda x:
            x.name.lower(),
    ):

        if (
            p.is_dir()
            and not p.is_symlink()
        ):

            projetos.append({
                "nome": p.name,
                "caminho":
                    relativo(
                        INPUT,
                        p,
                    ),
            })

    sarifs = []
    vistos = set()

    for raiz in (
        SARIFS,
        PROJECTS,
    ):

        for p in raiz.rglob("*"):

            if (
                not p.is_file()
                or p.is_symlink()
            ):
                continue

            nome = p.name.lower()

            if not (
                nome.endswith(
                    ".sarif"
                )
                or nome.endswith(
                    ".sarif.json"
                )
            ):
                continue

            caminho = relativo(
                INPUT,
                p,
            )

            if caminho in vistos:
                continue

            vistos.add(caminho)

            sarifs.append({
                "nome": p.name,
                "caminho": caminho,
            })

    return {
        "projetos": projetos,
        "sarifs": sorted(
            sarifs,
            key=lambda x:
                x["caminho"],
        ),
    }


def _executar_analise_sincrona(payload: dict):
    """
    Entrada operacional única do VeritasSec-Agent.

    Formato principal:
      sarif_path + projeto_path + índice/achado_id

    Não existe fallback para pipeline histórico.
    """


    # --------------------------------------------------------
    # Configuração cognitiva operacional.
    #
    # A API key nunca é escrita em artefato.
    # salvar_api_key() já a mantém em memória e no ambiente
    # do processo atual.
    # --------------------------------------------------------
    cfg_ia = carregar_config()

    provedor_ia = str(
        cfg_ia.get(
            "provedor",
            "gemini",
        )
    ).strip().lower()

    modelo_ia = str(
        cfg_ia.get(
            "modelo",
            "",
        )
        or "gemini-2.5-flash"
    ).strip()

    os.environ[
        "PROVEDOR_IA"
    ] = provedor_ia

    os.environ[
        "MODELO_IA"
    ] = modelo_ia


    os.environ[
        "TIMEOUT_IA"
    ] = str(
        cfg_ia.get(
            "timeout",
            120,
        )
    )

    os.environ[
        "MAX_TOKENS_IA"
    ] = str(
        cfg_ia.get(
            "max_tokens",
            2500,
        )
    )

    os.environ[
        "TEMPERATURA_IA"
    ] = str(
        cfg_ia.get(
            "temperatura",
            0.1,
        )
    )

    chave_memoria = _KEYS.get(
        provedor_ia,
        "",
    )

    if provedor_ia == "gemini":

        chave = (
            chave_memoria
            or os.environ.get(
                "GEMINI_API_KEY",
                "",
            )
            or os.environ.get(
                "CHAVE_GEMINI",
                "",
            )
        )

        if chave:
            os.environ[
                "GEMINI_API_KEY"
            ] = chave

            os.environ[
                "CHAVE_GEMINI"
            ] = chave

            os.environ[
                "IA_HABILITADA"
            ] = "true"

        else:
            os.environ[
                "IA_HABILITADA"
            ] = "false"

    elif provedor_ia == "openai":

        chave = (
            chave_memoria
            or os.environ.get(
                "OPENAI_API_KEY",
                "",
            )
            or os.environ.get(
                "CHAVE_OPENAI",
                "",
            )
        )

        if chave:
            os.environ[
                "OPENAI_API_KEY"
            ] = chave

            os.environ[
                "CHAVE_OPENAI"
            ] = chave

            os.environ[
                "IA_HABILITADA"
            ] = "true"

        else:
            os.environ[
                "IA_HABILITADA"
            ] = "false"

    elif provedor_ia == "ollama":

        os.environ[
            "OLLAMA_URL"
        ] = (
            os.environ.get(
                "OLLAMA_URL"
            )
            or os.environ.get(
                "URL_OLLAMA"
            )
            or "http://127.0.0.1:11434"
        )

        # Ollama local não usa API key.
        os.environ[
            "IA_HABILITADA"
        ] = "true"

    else:

        os.environ[
            "IA_HABILITADA"
        ] = "false"

    from aplicacao.multiagente.artefatos_agent import (
        persistir_resultado_agent,
    )
    from aplicacao.multiagente.artefatos_execucao_agent import (
        gerar_artefatos_analiticos,
    )

    from aplicacao.multiagente.pipeline_agent import (
        executar_pipeline_agent,
        executar_pipeline_sarif_agent,
    )

    sarif_path = (
        payload.get("sarif_path")
        or payload.get("sarif")
    )

    projeto_path = (
        payload.get("projeto_path")
        or payload.get("projeto")
    )

    # --------------------------------------------------------
    # A interface trabalha com caminhos relativos a INPUT:
    #
    #   projects/juice-shop
    #   sarif/juiceShop_code.sarif
    #
    # O pipeline, porém, exige caminhos reais/absolutos.
    # --------------------------------------------------------

    def _resolver_entrada(
        valor,
        *,
        esperado,
    ):
        # Aceita caminho legado relativo a INPUT e caminho
        # absoluto sob HOME. Mantém fail-closed fora de HOME.
        if not valor:
            return None

        bruto = str(valor)

        if "\x00" in bruto:
            raise HTTPException(
                status_code=400,
                detail="Caminho invalido.",
            )

        candidato = Path(
            bruto
        ).expanduser()

        home = (
            Path.home()
            .resolve()
        )

        if candidato.is_absolute():

            alvo = candidato.resolve()

            try:
                alvo.relative_to(
                    home
                )
            except ValueError as exc:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Caminho absoluto fora "
                        "da HOME autorizada."
                    ),
                ) from exc

        else:

            base = INPUT.resolve()

            alvo = (
                base
                / candidato
            ).resolve()

            try:
                alvo.relative_to(
                    base
                )
            except ValueError as exc:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Caminho relativo fora "
                        "da area INPUT."
                    ),
                ) from exc

        if esperado == "SARIF":

            if (
                not alvo.is_file()
                or not (
                    alvo.name.lower().endswith(
                        ".sarif"
                    )
                    or alvo.name.lower().endswith(
                        ".sarif.json"
                    )
                )
            ):
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "SARIF inexistente ou invalido: "
                        + str(alvo)
                    ),
                )

        elif esperado == "Projeto":

            if not alvo.is_dir():
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Projeto inexistente ou invalido: "
                        + str(alvo)
                    ),
                )

        return str(
            alvo
        )

    if sarif_path:
        sarif_path = _resolver_entrada(
            sarif_path,
            esperado="SARIF",
        )

    if projeto_path:
        projeto_path = _resolver_entrada(
            projeto_path,
            esperado="Projeto",
        )

    if sarif_path or projeto_path:
        if not sarif_path:
            raise ValueError(
                "sarif_path obrigatório"
            )

        if not projeto_path:
            raise ValueError(
                "projeto_path obrigatório"
            )

        pacote = executar_pipeline_sarif_agent(
            sarif_path=sarif_path,
            projeto_path=projeto_path,
            indice=payload.get(
                "indice"
            ),
            achado_id=payload.get(
                "achado_id"
            ),
        )

        if pacote["modo"] == "individual":
            resultado = pacote[
                "resultado"
            ]

            artefatos = (
                persistir_resultado_agent(
                    resultado
                )
            )

            return {
                "modo": "agent",
                "arquitetura": "multiagente",
                "origem": "sarif",
                "processamento": "individual",
                "total_achados_sarif": pacote[
                    "total_achados_sarif"
                ],
                "total_selecionado": 1,
                "total_processado": 1,
                "achado": pacote["achado"],
                "resultado": resultado,
                "artefatos": artefatos,
            }

        itens = []

        for item in pacote["resultados"]:
            resultado_item = item[
                "resultado"
            ]

            artefatos_item = (
                persistir_resultado_agent(
                    resultado_item
                )
            )

            itens.append({
                **item,
                "artefatos": artefatos_item,
            })

        artefatos_execucao = (
            gerar_artefatos_analiticos(
                pacote=pacote,
                itens=itens,
                projeto_path=projeto_path,
                sarif_path=sarif_path,
                saidas_root=SAIDAS,
                subdiretorio_saida=payload.get(
                    "subdiretorio_saida"
                ),
            )
        )

        return {
            "modo": "agent",
            "arquitetura": "multiagente",
            "origem": "sarif",
            "processamento": "multiachado",
            "total_achados_sarif": pacote[
                "total_achados_sarif"
            ],
            "total_selecionado": pacote[
                "total_selecionado"
            ],
            "total_processado": pacote[
                "total_processado"
            ],
            "resultados": itens,
            "artefatos_execucao": artefatos_execucao,
            "diretorio_saida": artefatos_execucao[
                "diretorio"
            ],
        }

    # Entrada unitária interna/controlada.
    resultado = executar_pipeline_agent(
        payload
    )

    artefatos = persistir_resultado_agent(
        resultado
    )

    return {
        "modo": "agent",
        "arquitetura": "multiagente",
        "origem": "achado",
        "resultado": resultado,
        "artefatos": artefatos,
    }


def _worker_analise(
    job_id: str,
    payload: dict,
) -> None:

    with _ANALISE_JOBS_LOCK:

        job = _ANALISE_JOBS.get(
            job_id
        )

        if job is None:
            return

        job["status"] = (
            "AGUARDANDO_EXECUCAO"
        )

    try:

        with _ANALISE_EXECUCAO_LOCK:

            with _ANALISE_JOBS_LOCK:

                job = _ANALISE_JOBS.get(
                    job_id
                )

                if job is None:
                    return

                job["status"] = (
                    "EM_EXECUCAO"
                )

                job[
                    "inicio_execucao"
                ] = time.time()

            resultado = (
                _executar_analise_sincrona(
                    payload
                )
            )

        with _ANALISE_JOBS_LOCK:

            job = _ANALISE_JOBS.get(
                job_id
            )

            if job is not None:

                job["status"] = (
                    "CONCLUIDA"
                )

                job["fim"] = (
                    time.time()
                )

                job["resultado"] = (
                    resultado
                )

                job["erro"] = None

    except Exception as exc:

        with _ANALISE_JOBS_LOCK:

            job = _ANALISE_JOBS.get(
                job_id
            )

            if job is not None:

                job["status"] = (
                    "FALHA"
                )

                job["fim"] = (
                    time.time()
                )

                job["resultado"] = None

                job["erro"] = (
                    type(exc).__name__
                    + ": "
                    + str(exc)
                )


def _vs_historico_executar_analise_1(
    payload: dict,
):
    """
    Único ponto operacional de análise.

    Sem 'assincrono':
        comportamento síncrono compatível.

    assincrono=true:
        cria job e retorna imediatamente.
    """

    if not isinstance(
        payload,
        dict,
    ):

        raise HTTPException(
            status_code=400,
            detail="Payload invalido.",
        )

    assincrono = bool(
        payload.get(
            "assincrono",
            False,
        )
    )

    if not assincrono:

        return (
            _executar_analise_sincrona(
                payload
            )
        )

    payload_job = dict(
        payload
    )

    payload_job.pop(
        "assincrono",
        None,
    )

    job_id = uuid.uuid4().hex

    agora = time.time()

    with _ANALISE_JOBS_LOCK:

        _ANALISE_JOBS[
            job_id
        ] = {
            "job_id": job_id,
            "status": "CRIADA",
            "criada_em": agora,
            "inicio_execucao": None,
            "fim": None,
            "resultado": None,
            "erro": None,
        }

    thread = threading.Thread(
        target=_worker_analise,
        args=(
            job_id,
            payload_job,
        ),
        daemon=True,
        name=(
            "veritassec-analise-"
            + job_id[:8]
        ),
    )

    thread.start()

    return {
        "job_id": job_id,
        "status": "CRIADA",
        "assincrono": True,
    }

executar_analise = _vs_historico_executar_analise_1


def _vs_historico_obter_status_analise_1(
    job_id: str,
):

    with _ANALISE_JOBS_LOCK:

        job = _ANALISE_JOBS.get(
            job_id
        )

        if job is None:

            raise HTTPException(
                status_code=404,
                detail=(
                    "Analise nao encontrada."
                ),
            )

        resposta = {
            "job_id":
                job["job_id"],

            "status":
                job["status"],

            "criada_em":
                job["criada_em"],

            "inicio_execucao":
                job[
                    "inicio_execucao"
                ],

            "fim":
                job["fim"],

            "erro":
                job["erro"],
        }

        if (
            job["status"]
            == "CONCLUIDA"
        ):

            resposta[
                "resultado"
            ] = job[
                "resultado"
            ]

        return resposta

obter_status_analise = _vs_historico_obter_status_analise_1




def listar_outputs(
    diretorio: str = "interface",
):

    pasta = caminho_seguro(
        OUTPUT,
        diretorio,
    )

    if not pasta.exists():

        return {
            "diretorio":
                diretorio,

            "arquivos":
                [],
        }

    arquivos = []

    for p in sorted(
        pasta.rglob("*")
    ):

        if (
            p.is_file()
            and not p.is_symlink()
        ):

            arquivos.append({

                "nome":
                    p.name,

                "caminho":
                    relativo(
                        OUTPUT,
                        p,
                    ),

                "tamanho_bytes":
                    p.stat().st_size,
            })

    return {
        "diretorio":
            diretorio,

        "arquivos":
            arquivos,
    }


def baixar_output(
    caminho: str,
):

    p = caminho_seguro(
        OUTPUT,
        caminho,
        True,
    )

    if not p.is_file():

        raise HTTPException(
            status_code=404,
            detail=(
                "Arquivo "
                "nao encontrado."
            ),
        )

    return FileResponse(
        p,
        filename=p.name,
    )


# ============================================================
# VeritasSec-Agent — pipeline multiagente operacional
# ============================================================



def obter_status_ia_seguro() -> dict:
    """
    Estado operacional da camada cognitiva.

    Nunca retorna conteúdo da API key.
    """
    import os

    cfg = carregar_config()

    provedor = str(
        cfg.get(
            "provedor",
            "gemini",
        )
    ).strip().lower()

    modelo = str(
        cfg.get(
            "modelo",
            "",
        )
        or "gemini-2.5-flash"
    ).strip()

    chave_memoria = bool(
        _KEYS.get(
            provedor,
            "",
        )
    )

    chave_ambiente = bool(
        os.environ.get(
            "GEMINI_API_KEY"
        )
        or os.environ.get(
            "CHAVE_GEMINI"
        )
    )

    habilitada = (
        os.environ.get(
            "IA_HABILITADA",
            "false",
        ).strip().lower()
        in {
            "1",
            "true",
            "sim",
            "yes",
            "on",
        }
    )

    return {
        "provedor": provedor,
        "modelo": modelo,
        "api_key_configurada": (
            chave_memoria
            or chave_ambiente
        ),
        "ia_habilitada": habilitada,
        "segredo_exposto": False,
    }


# ============================================================
# VERITASSEC_PASSO2_BACKEND_OPERACIONAL
#
# A rota oficial /api/interface/analisar continua sendo
# a única entrada operacional de análise.
#
# payload["operacional"] == True:
#     cria execução controlável em background.
#
# demais payloads:
#     preservam integralmente o comportamento histórico.
# ============================================================

_executar_analise_sincrono_compat_passo2 = executar_analise
_obter_status_analise_compat_passo2 = obter_status_analise


def executar_analise(
    payload: dict,
):
    from fastapi import HTTPException

    if not isinstance(
        payload,
        dict,
    ):
        raise HTTPException(
            status_code=400,
            detail="Payload invalido.",
        )

    if not payload.get(
        "operacional",
        False,
    ):
        return (
            _executar_analise_sincrono_compat_passo2(
                payload
            )
        )

    # DAST: contrato validado antes da criação da execução.
    from aplicacao.multiagente.contrato_dast import (
        validar_configuracao_dast, ConfiguracaoDASTInvalida,
    )
    try:
        dast = validar_configuracao_dast(False, None)
    except ConfiguracaoDASTInvalida as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    payload["dast"] = {

        "habilitado": dast.habilitado,

        "url_base": dast.url_base,

    }


    _hidratar_multimodelo_operacional()

    from aplicacao.multiagente.controle_execucao import (
        iniciar_execucao,
    )

    try:
        estado = iniciar_execucao(
            payload
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return {
        "modo":
            "agent",

        "arquitetura":
            "multiagente",

        "operacional":
            True,

        **estado,
    }


def obter_status_analise(
    job_id: str,
):
    from aplicacao.multiagente.controle_execucao import (
        existe_execucao,
        obter_execucao,
    )

    if existe_execucao(
        job_id
    ):
        return obter_execucao(
            job_id
        )

    return (
        _obter_status_analise_compat_passo2(
            job_id
        )
    )


def pausar_analise(
    job_id: str,
):
    from fastapi import HTTPException

    from aplicacao.multiagente.controle_execucao import (
        pausar_execucao,
    )

    try:
        return pausar_execucao(
            job_id
        )

    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail="Execucao inexistente.",
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc


def retomar_analise(
    job_id: str,
):
    from fastapi import HTTPException

    from aplicacao.multiagente.controle_execucao import (
        retomar_execucao,
    )

    try:
        return retomar_execucao(
            job_id
        )

    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail="Execucao inexistente.",
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc


def parar_analise(
    job_id: str,
):
    from fastapi import HTTPException

    from aplicacao.multiagente.controle_execucao import (
        parar_execucao,
    )

    try:
        return parar_execucao(
            job_id
        )

    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail="Execucao inexistente.",
        ) from exc


# ============================================================
# VERITASSEC_PASSO3_API_RESULTADOS
# ============================================================

def obter_resultados_operacionais(
    job_id: str,
):
    from fastapi import HTTPException

    from aplicacao.multiagente.controle_execucao import (
        obter_resultados_execucao,
    )

    try:
        return obter_resultados_execucao(
            job_id
        )

    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail="Execucao inexistente.",
        ) from exc


# ============================================================
# VERITASSEC_PASSO4_136_EXPORTACAO
# ============================================================

def exportar_execucao_final_136(
    job_id: str,
    formatos: list[str] | None = Body(
        default=None,
        embed=True,
    ),
    destino_pasta: str | None = Body(
        default=None,
        embed=True,
    ),
):
    """Exporta somente formatos selecionados de execução concluída."""

    import hashlib
    import re
    import shutil
    import tempfile
    import uuid
    from pathlib import Path

    from aplicacao.relatorios.fechamento_veritassec import (
        gerar_exportacao_operacional,
    )

    permitidos = {"DOCX", "CSV"}

    if (
        not isinstance(formatos, list)
        or not formatos
        or any(
            type(item) is not str
            or item not in permitidos
            for item in formatos
        )
    ):
        raise HTTPException(
            status_code=400,
            detail="Selecione DOCX, CSV ou ambos.",
        )

    if (
        not isinstance(job_id, str)
        or re.fullmatch(r"[a-zA-Z0-9_-]{1,128}", job_id) is None
    ):
        raise HTTPException(
            status_code=400,
            detail="Identificador de execução inválido.",
        )

    formatos = list(dict.fromkeys(formatos))

    try:
        status = obter_status_analise(job_id)
        dados = obter_resultados_operacionais(job_id)
    except Exception as exc:
        raise HTTPException(
            status_code=404,
            detail="Execução não localizada.",
        ) from exc

    if status.get("estado") != "CONCLUIDO":
        raise HTTPException(
            status_code=409,
            detail="A execução precisa estar concluída.",
        )

    raiz = (
        Path.home()
        / "Documentos"
        / "Projetos"
        / "VeritasSec-Agent-Saidas"
        / "exports-interface"
        / job_id
    )


    # VERITASSEC_EXPORTACAO_DESTINO_ZIP_20261020
    # Destinos externos a HOME são negados.
    if destino_pasta is not None:

        if (
            not isinstance(destino_pasta, str)
            or not destino_pasta.strip()
            or len(destino_pasta) > 4096
        ):
            raise HTTPException(
                status_code=400,
                detail="Diretório de destino inválido.",
            )

        from pathlib import Path

        home = Path.home().resolve()

        pasta = Path(
            destino_pasta.strip()
        ).expanduser().resolve()

        try:
            pasta.relative_to(home)
        except ValueError as exc:
            raise HTTPException(
                status_code=403,
                detail="Destino permitido somente dentro de HOME.",
            ) from exc

        if not pasta.is_dir():
            raise HTTPException(
                status_code=400,
                detail="O diretório selecionado não existe.",
            )

        raiz = pasta / "VeritasSec-Agent" / job_id

    raiz.mkdir(parents=True, exist_ok=True)

    nome_entrega = "selecao-" + uuid.uuid4().hex
    destino_final = raiz / nome_entrega

    with tempfile.TemporaryDirectory(
        prefix="exportacao-temporaria-",
        dir=str(raiz),
    ) as temporario:

        origem = Path(temporario) / "gerados"

        manifesto_original = gerar_exportacao_operacional(
            resultados=dados.get("resultados", []),
            diretorio=origem,
            projeto=str(
                status.get("projeto_path", "não informado")
            ),
            sarif=str(
                status.get("sarif_path", "não informado")
            ),
        )

        nomes = []

        if "DOCX" in formatos:
            nomes.append("relatorio-veritassec.docx")

        if "CSV" in formatos:
            nomes.extend([
                "resultados.csv",
                "evidencias.csv",
            ])

        # VERITASSEC_ZIP_XAI_MARKDOWN_V2
        # Mantem os formatos publicos existentes e entrega a explicacao junto.
        if "relatorio-veritassec.md" not in nomes:
            nomes.append("relatorio-veritassec.md")

        for nome in nomes:
            if not (origem / nome).is_file():
                raise RuntimeError(
                    "ARTEFATO_NAO_GERADO: " + nome
                )

        entrega_temp = Path(temporario) / "entrega"
        entrega_temp.mkdir()

        hashes = {}

        for nome in nomes:
            arquivo_origem = origem / nome
            arquivo_destino = entrega_temp / nome

            shutil.copy2(
                arquivo_origem,
                arquivo_destino,
            )

            hashes[nome] = hashlib.sha256(
                arquivo_destino.read_bytes()
            ).hexdigest()

        (entrega_temp / "SHA256SUMS.txt").write_text(
            "".join(
                f"{hashes[nome]}  {nome}\n"
                for nome in sorted(hashes)
            ),
            encoding="utf-8",
        )

        # Publica apenas uma entrega inteiramente validada.
        entrega_temp.rename(destino_final)

    arquivos = {
        nome: str(destino_final / nome)
        for nome in nomes
    }

    return {
        "status": "GERADO",
        "diretorio": str(destino_final),
        "manifesto": {
            "formatos": formatos,
            "arquivos": arquivos,
            "sha256": hashes,
            "arquivo_hashes": str(
                destino_final / "SHA256SUMS.txt"
            ),
            "total": manifesto_original.get("total"),
            "ground_truth_usado": False,
        },
    }




# ============================================================
# VERITASSEC_CORRECAO_INTERFACE_FS_MULTIMODELO
# ============================================================

MULTIMODELO_CONFIG_FILE = (
    CONFIG_DIR
    / "multimodelo-interface.json"
)


class ConfigMultimodeloInterface(BaseModel):

    usar_local: bool = True
    modelo_local: str = ""

    usar_gpt: bool = False
    modelo_gpt: str = ""

    usar_gemini: bool = False
    modelo_gemini: str = ""


def _modelo_legado_para(
    provedor: str,
) -> str:

    try:
        cfg = carregar_config()
    except Exception:
        return ""

    atual = str(
        cfg.get(
            "provedor",
            ""
        )
    ).strip().lower()

    if provedor == "gpt":
        valido = {
            "openai",
            "gpt",
        }
    else:
        valido = {
            provedor
        }

    if atual not in valido:
        return ""

    return str(
        cfg.get(
            "modelo",
            ""
        )
        or ""
    )


def obter_config_multimodelo():

    padrao = {
        "usar_local":
            True,

        "modelo_local":
            (
                os.getenv(
                    "VERITASSEC_LOCAL_MODEL"
                )
                or ""
            ),

        "usar_gpt":
            False,

        "modelo_gpt":
            (
                os.getenv(
                    "VERITASSEC_GPT_MODEL"
                )
                or os.getenv(
                    "VERITASSEC_OPENAI_MODEL"
                )
                or os.getenv(
                    "MODELO_OPENAI"
                )
                or _modelo_legado_para(
                    "gpt"
                )
            ),

        "usar_gemini":
            False,

        "modelo_gemini":
            (
                os.getenv(
                    "VERITASSEC_GEMINI_MODEL"
                )
                or os.getenv(
                    "MODELO_GEMINI"
                )
                or _modelo_legado_para(
                    "gemini"
                )
            ),
    }

    if MULTIMODELO_CONFIG_FILE.is_file():

        try:
            dados = json.loads(
                MULTIMODELO_CONFIG_FILE.read_text(
                    encoding="utf-8"
                )
            )

            padrao.update(
                dados
            )

        except Exception:
            pass

    return {
        **padrao,

        "api_key_gpt_configurada":
            bool(
                _KEYS.get(
                    "openai"
                )
            ),

        "api_key_gemini_configurada":
            bool(
                _KEYS.get(
                    "gemini"
                )
            ),

        "fail_closed":
            True,
    }


def salvar_config_multimodelo(
    req: ConfigMultimodeloInterface,
):

    dados = req.model_dump()

    selecionados = []

    if req.usar_local:

        if not req.modelo_local.strip():
            raise HTTPException(
                status_code=400,
                detail=(
                    "Modelo local obrigatorio "
                    "quando Local estiver habilitado."
                ),
            )

        selecionados.append(
            "local"
        )

    if req.usar_gpt:

        if not req.modelo_gpt.strip():
            raise HTTPException(
                status_code=400,
                detail=(
                    "Modelo GPT obrigatorio "
                    "quando GPT estiver habilitado."
                ),
            )

        selecionados.append(
            "gpt"
        )

    if req.usar_gemini:

        if not req.modelo_gemini.strip():
            raise HTTPException(
                status_code=400,
                detail=(
                    "Modelo Gemini obrigatorio "
                    "quando Gemini estiver habilitado."
                ),
            )

        selecionados.append(
            "gemini"
        )

    if not selecionados:

        raise HTTPException(
            status_code=400,
            detail=(
                "Selecione pelo menos um provedor."
            ),
        )

    MULTIMODELO_CONFIG_FILE.write_text(
        json.dumps(
            dados,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    os.environ[
        "IA_HABILITADA"
    ] = "true"

    os.environ[
        "VERITASSEC_MULTIMODELO_PAPEIS"
    ] = (
        "true"
        if len(
            selecionados
        ) > 1
        else "false"
    )

    os.environ[
        "VERITASSEC_PROVEDORES_PAPEIS"
    ] = ",".join(
        selecionados
    )

    if req.usar_local:

        os.environ[
            "VERITASSEC_LOCAL_MODEL"
        ] = req.modelo_local.strip()

    else:

        os.environ.pop(
            "VERITASSEC_LOCAL_MODEL",
            None,
        )

    if req.usar_gpt:

        modelo = req.modelo_gpt.strip()

        os.environ[
            "VERITASSEC_GPT_MODEL"
        ] = modelo

        os.environ[
            "VERITASSEC_OPENAI_MODEL"
        ] = modelo

        os.environ[
            "MODELO_OPENAI"
        ] = modelo

    else:

        for nome in (
            "VERITASSEC_GPT_MODEL",
            "VERITASSEC_OPENAI_MODEL",
        ):
            os.environ.pop(
                nome,
                None,
            )

    if req.usar_gemini:

        modelo = req.modelo_gemini.strip()

        os.environ[
            "VERITASSEC_GEMINI_MODEL"
        ] = modelo

        os.environ[
            "MODELO_GEMINI"
        ] = modelo

    else:

        os.environ.pop(
            "VERITASSEC_GEMINI_MODEL",
            None,
        )

    primeiro = selecionados[0]

    if primeiro == "local":

        os.environ[
            "PROVEDOR_IA"
        ] = "ollama"

        os.environ[
            "MODELO_IA"
        ] = req.modelo_local.strip()

        os.environ[
            "VERITASSEC_LLM_PROVIDER"
        ] = "local"

        os.environ[
            "VERITASSEC_LLM_MODEL"
        ] = req.modelo_local.strip()

    elif primeiro == "gpt":

        os.environ[
            "PROVEDOR_IA"
        ] = "openai"

        os.environ[
            "MODELO_IA"
        ] = req.modelo_gpt.strip()

        os.environ[
            "VERITASSEC_LLM_PROVIDER"
        ] = "openai"

        os.environ[
            "VERITASSEC_LLM_MODEL"
        ] = req.modelo_gpt.strip()

    else:

        os.environ[
            "PROVEDOR_IA"
        ] = "gemini"

        os.environ[
            "MODELO_IA"
        ] = req.modelo_gemini.strip()

        os.environ[
            "VERITASSEC_LLM_PROVIDER"
        ] = "gemini"

        os.environ[
            "VERITASSEC_LLM_MODEL"
        ] = req.modelo_gemini.strip()

    return {
        **obter_config_multimodelo(),

        "provedores_ativos":
            selecionados,

        "multimodelo_ativo":
            len(
                selecionados
            ) > 1,
    }



# ============================================================
# VERITASSEC_HIDRATACAO_MULTIMODELO_OPERACIONAL_20261019
#
# Reidrata a configuração multimodelo persistida somente para
# a execução operacional controlada.
# Não altera o caminho histórico/E2E.
# ============================================================


# VERITASSEC_LOCAL_DESCOBERTA_SEGURA_20261022
def _resolver_llama_agno() -> bool:

    # VERITASSEC_VALIDACAO_EXPLICITA_LLAMA_V2
    # Configuracao explicita invalida prevalece
    # sobre qualquer configuracao persistida.
    import ipaddress as _ipaddress_v2
    import os as _os_v2
    from urllib.parse import urlsplit as _urlsplit_v2

    _url_explicita_v2 = _os_v2.environ.get(
        "VERITASSEC_LLAMA_BASE_URL",
        "",
    ).strip()

    if _url_explicita_v2:
        try:
            _partes_v2 = _urlsplit_v2(
                _url_explicita_v2
            )

            _host_v2 = (
                _partes_v2.hostname or ""
            ).lower()

            if _host_v2 == "localhost":
                _interno_v2 = True
            else:
                try:
                    _ip_v2 = _ipaddress_v2.ip_address(
                        _host_v2
                    )

                    _interno_v2 = (
                        _ip_v2.version == 4
                        and any(
                            _ip_v2 in _ipaddress_v2.ip_network(
                                _rede_v2
                            )
                            for _rede_v2 in (
                                "127.0.0.0/8",
                                "10.0.0.0/8",
                                "172.16.0.0/12",
                                "192.168.0.0/16",
                            )
                        )
                    )

                except ValueError:
                    _interno_v2 = False

            _valido_v2 = (
                _partes_v2.scheme == "http"
                and _interno_v2
                and _partes_v2.port is not None
                and not _partes_v2.username
                and not _partes_v2.password
                and not _partes_v2.query
                and not _partes_v2.fragment
                and _partes_v2.path.rstrip("/")
                    in ("", "/v1")
            )

        except (ValueError, TypeError):
            _valido_v2 = False

        if not _valido_v2:
            return False

    # VERITASSEC_LLAMA_CONFIG_VALIDADA_V1
    import json as _json_llama
    from pathlib import Path as _Path_llama
    import os as _os_llama

    arquivo = (
        _Path_llama.home()
        / ".config/veritassec/multimodel/agno-local-validado.json"
    )

    if (
        arquivo.is_file()
        and not arquivo.is_symlink()
        and arquivo.stat().st_mode & 0o077 == 0
    ):
        try:
            dados = _json_llama.loads(
                arquivo.read_text(encoding="utf-8")
            )

            if all(
                dados.get(campo)
                for campo in ("url", "key", "modelo")
            ):
                _os_llama.environ.setdefault(
                    "VERITASSEC_LLAMA_BASE_URL",
                    dados["url"],
                )
                _os_llama.environ.setdefault(
                    "VERITASSEC_LLAMA_API_KEY",
                    dados["key"],
                )
                _os_llama.environ[
                    "VERITASSEC_LOCAL_MODEL_API"
                ] = dados["modelo"]

                return True
        except (OSError, ValueError, TypeError):
            pass

    """Reutiliza configuração local existente sem expor segredos."""
    import json
    import subprocess
    from urllib.parse import urlsplit

    base = os.environ.get(
        "VERITASSEC_LLAMA_BASE_URL", ""
    ).strip()

    chave = os.environ.get(
        "VERITASSEC_LLAMA_API_KEY", ""
    ).strip()

    config = (
        Path.home()
        / ".config"
        / "veritassec"
        / "multimodel"
    )

    def ler_arquivo(nome, segredo=False):
        caminho = config / nome

        if (
            not caminho.is_file()
            or caminho.is_symlink()
        ):
            return ""

        if segredo and caminho.stat().st_mode & 0o077:
            return ""

        return caminho.read_text(
            encoding="utf-8"
        ).strip()

    if not base:
        base = (
            ler_arquivo("llama-base-url")
            or ler_arquivo("llama-url")
        )

    if not chave:
        chave = (
            ler_arquivo("llama-api-key", True)
            or ler_arquivo("local-api-key", True)
        )

    if not base or not chave:
        try:
            processo = subprocess.run(
                [
                    "docker",
                    "inspect",
                    "veritassec-llama-runtime",
                ],
                capture_output=True,
                text=True,
                timeout=3,
                check=True,
            )

            info = json.loads(
                processo.stdout
            )[0]

            if not base:
                portas = (
                    info.get("NetworkSettings", {})
                    .get("Ports", {})
                    or {}
                )

                encontradas = []

                for destinos in portas.values():
                    for destino in destinos or []:
                        host = destino.get("HostIp", "")

                        if host not in {
                            "127.0.0.1",
                            "0.0.0.0",
                            "::1",
                            "",
                        }:
                            continue

                        porta = str(
                            destino.get("HostPort", "")
                        )

                        if porta.isdecimal():
                            encontradas.append(int(porta))

                if len(set(encontradas)) == 1:
                    base = (
                        "http://127.0.0.1:"
                        + str(encontradas[0])
                    )

            if not chave:
                ambiente = (
                    info.get("Config", {})
                    .get("Env", [])
                    or []
                )

                for entrada in ambiente:
                    nome, _, valor = entrada.partition("=")

                    if nome in {
                        "LLAMA_ARG_API_KEY",
                        "LLAMA_API_KEY",
                        "LLAMA_SERVER_API_KEY",
                    } and valor:
                        chave = valor
                        break

                if not chave:
                    comandos = (
                        info.get("Config", {})
                        .get("Cmd", [])
                        or []
                    )

                    comandos += (
                        info.get("Config", {})
                        .get("Entrypoint", [])
                        or []
                    )

                    for indice, argumento in enumerate(
                        comandos
                    ):
                        if (
                            argumento == "--api-key"
                            and indice + 1 < len(comandos)
                        ):
                            chave = str(
                                comandos[indice + 1]
                            )
                            break

        except (
            OSError,
            ValueError,
            IndexError,
            subprocess.SubprocessError,
        ):
            pass

    if not base or not chave:
        return False

    try:
        url = urlsplit(base)

        valido = (
            url.scheme == "http"
            and url.hostname in {
                "127.0.0.1",
                "localhost",
            }
            and url.port is not None
            and not url.username
            and not url.password
            and url.path in {
                "",
                "/",
                "/v1",
                "/v1/",
            }
            and not url.query
            and not url.fragment
        )

    except ValueError:
        valido = False

    if not valido:
        return False

    os.environ[
        "VERITASSEC_LLAMA_BASE_URL"
    ] = base.rstrip("/")

    os.environ[
        "VERITASSEC_LLAMA_API_KEY"
    ] = chave

    return True


def _hidratar_multimodelo_operacional():
    import os

    cfg = obter_config_multimodelo()

    selecionados = []

    if bool(
        cfg.get(
            "usar_local",
            False,
        )
    ):
        selecionados.append(
            "local"
        )

    if bool(
        cfg.get(
            "usar_gpt",
            False,
        )
    ):
        selecionados.append(
            "gpt"
        )

    if bool(
        cfg.get(
            "usar_gemini",
            False,
        )
    ):
        selecionados.append(
            "gemini"
        )

    if not selecionados:
        raise RuntimeError(
            "NENHUM_PROVEDOR_MULTIMODELO_ATIVO"
        )

    os.environ[
        "VERITASSEC_MULTIMODELO_PAPEIS"
    ] = (
        "true"
        if len(
            selecionados
        ) > 1
        else "false"
    )

    os.environ[
        "VERITASSEC_PROVEDORES_PAPEIS"
    ] = ",".join(
        selecionados
    )

    modelo_local = str(
        cfg.get(
            "modelo_local",
            "",
        )
        or ""
    ).strip()

    modelo_gpt = str(
        cfg.get(
            "modelo_gpt",
            "",
        )
        or ""
    ).strip()

    modelo_gemini = str(
        cfg.get(
            "modelo_gemini",
            "",
        )
        or ""
    ).strip()

    if "local" in selecionados:

        if not modelo_local:
            raise RuntimeError(
                "MODELO_LOCAL_AUSENTE"
            )

        os.environ[
            "VERITASSEC_LOCAL_MODEL"
        ] = modelo_local

        _resolver_llama_agno()

    else:

        os.environ.pop(
            "VERITASSEC_LOCAL_MODEL",
            None,
        )

    if "gpt" in selecionados:

        if not modelo_gpt:
            raise RuntimeError(
                "MODELO_GPT_AUSENTE"
            )

        os.environ[
            "VERITASSEC_GPT_MODEL"
        ] = modelo_gpt

        os.environ[
            "VERITASSEC_OPENAI_MODEL"
        ] = modelo_gpt

        os.environ[
            "MODELO_OPENAI"
        ] = modelo_gpt

    else:

        for nome in (
            "VERITASSEC_GPT_MODEL",
            "VERITASSEC_OPENAI_MODEL",
            "MODELO_OPENAI",
        ):
            os.environ.pop(
                nome,
                None,
            )

    if "gemini" in selecionados:

        if not modelo_gemini:
            raise RuntimeError(
                "MODELO_GEMINI_AUSENTE"
            )

        os.environ[
            "VERITASSEC_GEMINI_MODEL"
        ] = modelo_gemini

        os.environ[
            "MODELO_GEMINI"
        ] = modelo_gemini

    else:

        for nome in (
            "VERITASSEC_GEMINI_MODEL",
            "MODELO_GEMINI",
        ):
            os.environ.pop(
                nome,
                None,
            )


    # VERITASSEC_AGNO_OPERACIONAL_REGRESSAO_20261022
    #
    # Habilitacao de agentes nao depende da quantidade
    # de provedores selecionados.
    #
    # Nao exigir credenciais nesta etapa: o contrato
    # de hidratacao tambem atende testes com provedores
    # simulados. Credenciais sao validadas pelo motor
    # antes das chamadas reais.

    candidatos = []

    if "gemini" in selecionados:
        candidatos.append(
            (
                "gemini",
                modelo_gemini,
                "GEMINI_API_KEY",
                "CHAVE_GEMINI",
            )
        )

    if "gpt" in selecionados:
        candidatos.append(
            (
                "openai",
                modelo_gpt,
                "OPENAI_API_KEY",
                "CHAVE_OPENAI",
            )
        )

    if candidatos:
        provedor_preferido = (
            os.environ.get("PROVEDOR_IA", "")
            .strip()
            .lower()
        )

        # Priorizar provedor com credencial disponivel,
        # respeitando a preferencia quando possivel.
        candidatos.sort(
            key=lambda item: (
                item[0] != provedor_preferido,
            )
        )

        escolhido = None

        for candidato in candidatos:
            provedor, modelo, nome_env, nome_alternativo = (
                candidato
            )

            chave = (
                _KEYS.get(provedor)
                or os.environ.get(nome_env)
                or os.environ.get(nome_alternativo)
                or ""
            )

            if chave:
                escolhido = candidato
                break

        if escolhido is None:
            escolhido = candidatos[0]

        provedor, modelo, nome_env, nome_alternativo = (
            escolhido
        )

        chave = (
            _KEYS.get(provedor)
            or os.environ.get(nome_env)
            or os.environ.get(nome_alternativo)
            or ""
        )

        if chave:
            os.environ[nome_env] = chave

        os.environ["PROVEDOR_IA"] = provedor
        os.environ["MODELO_IA"] = modelo
        os.environ["IA_HABILITADA"] = "true"

    else:
        # VERITASSEC_SELECAO_LIVRE_20261022
        # Local tambem e um provedor LLM.
        # Sua disponibilidade sera verificada pelo motor.
        os.environ["PROVEDOR_IA"] = "llama_cpp"
        os.environ["MODELO_IA"] = modelo_local
        os.environ["IA_HABILITADA"] = "true"

    return {
        "provedores_ativos":
            tuple(
                selecionados
            ),

        "multimodelo_ativo":
            len(
                selecionados
            ) > 1,
    }

def listar_sistema_arquivos(
    path: str | None = None,
    tipo: str = "diretorio",
):

    if tipo not in {
        "diretorio",
        "sarif",
    }:
        raise HTTPException(
            status_code=400,
            detail="Tipo invalido.",
        )

    home = (
        Path.home()
        .resolve()
    )

    atual = (
        Path(path)
        .expanduser()
        .resolve()
        if path
        else home
    )

    try:
        atual.relative_to(
            home
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=403,
            detail=(
                "Navegacao limitada a HOME."
            ),
        ) from exc

    if not atual.is_dir():
        raise HTTPException(
            status_code=400,
            detail=(
                "Diretorio inexistente."
            ),
        )

    itens = []

    for item in sorted(
        atual.iterdir(),
        key=lambda p: (
            not p.is_dir(),
            p.name.lower(),
        ),
    ):

        if item.is_symlink():
            continue

        try:
            item.resolve().relative_to(
                home
            )
        except ValueError:
            continue

        if item.is_dir():

            itens.append({
                "nome":
                    item.name,

                "caminho":
                    str(
                        item.resolve()
                    ),

                "tipo":
                    "diretorio",
            })

            continue

        if tipo == "sarif":

            nome = item.name.lower()

            if (
                nome.endswith(
                    ".sarif"
                )
                or nome.endswith(
                    ".sarif.json"
                )
            ):

                itens.append({
                    "nome":
                        item.name,

                    "caminho":
                        str(
                            item.resolve()
                        ),

                    "tipo":
                        "sarif",
                })

    pai = None

    if atual != home:

        candidato = (
            atual.parent
            .resolve()
        )

        try:
            candidato.relative_to(
                home
            )
            pai = str(
                candidato
            )
        except ValueError:
            pai = None

    return {
        "home":
            str(home),

        "atual":
            str(atual),

        "pai":
            pai,

        "tipo":
            tipo,

        "itens":
            itens,
    }


# VERITASSEC_EXPORTACAO_ZIP_20261020
def baixar_exportacao_zip_20261020(
    job_id: str,
    formatos: list[str] | None = Body(
        default=None,
        embed=True,
    ),
):
    """Produz ZIP somente com artefatos da execução solicitada."""

    import io
    import zipfile

    from fastapi.responses import StreamingResponse

    # Reutiliza a validação de execução e formatos.
    entrega = exportar_execucao_final_136(
        job_id=job_id,
        formatos=formatos,
        destino_pasta=None,
    )

    manifesto = entrega["manifesto"]

    arquivos = manifesto["arquivos"]

    memoria = io.BytesIO()

    with zipfile.ZipFile(
        memoria,
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=6,
    ) as pacote:

        for nome, caminho in sorted(arquivos.items()):

            if nome not in {
                "relatorio-veritassec.docx",
                "resultados.csv",
                "evidencias.csv",
                "relatorio-veritassec.md",
            }:
                raise HTTPException(
                    status_code=500,
                    detail="Artefato inesperado.",
                )

            arquivo = Path(caminho).resolve()

            raiz_entrega = Path(
                entrega["diretorio"]
            ).resolve()

            if arquivo.parent != raiz_entrega:
                raise HTTPException(
                    status_code=500,
                    detail="Caminho de artefato inválido.",
                )

            pacote.write(
                arquivo,
                arcname=nome,
            )

        hashes = Path(
            manifesto["arquivo_hashes"]
        ).resolve()

        if hashes.parent != Path(
            entrega["diretorio"]
        ).resolve():
            raise HTTPException(
                status_code=500,
                detail="Manifesto de integridade inválido.",
            )

        pacote.write(
            hashes,
            arcname="SHA256SUMS.txt",
        )

    memoria.seek(0)

    return StreamingResponse(
        memoria,
        media_type="application/zip",
        headers={
            "Content-Disposition":
                'attachment; filename="veritassec-resultados.zip"',
            "Cache-Control": "no-store",
            "X-Content-Type-Options": "nosniff",
        },
    )
