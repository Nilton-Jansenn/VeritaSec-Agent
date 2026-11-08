from __future__ import annotations

import copy
import json
import os
from typing import Any


from .modelos_agno import (
    PROVEDORES_SUPORTADOS,
    construir_modelo_agno,
)

from .modelos import (
    DecisaoAgenteLLM,
    PapelAgente,
    RegistroRaciocinioAgente,
)
from .registry import REGISTRO_AGENTES


# VERITASSEC_AGNO_CONFIG_INTEGRADA_20261022
def _configuracao_multimodelo() -> dict[str, str]:
    """Lê somente a configuração já utilizada pelo painel."""
    from pathlib import Path

    base = (
        Path.home()
        / ".config"
        / "veritassec"
        / "multimodel"
    )

    arquivo = base / "modelos.env"
    valores: dict[str, str] = {}

    if arquivo.is_file():
        for linha in arquivo.read_text(
            encoding="utf-8"
        ).splitlines():
            linha = linha.strip()

            if (
                not linha
                or linha.startswith("#")
                or "=" not in linha
            ):
                continue

            chave, valor = linha.split("=", 1)
            valores[chave.strip()] = (
                valor.strip().strip('"').strip("'")
            )

    return valores


def _credencial_multimodelo(
    provedor: str,
) -> str:
    """Nunca registra nem imprime a credencial."""
    from pathlib import Path

    nomes = {
        "gemini": "gemini-api-key",
        "openai": "openai-api-key",
    }

    nome = nomes.get(provedor)

    if nome is None:
        return ""

    arquivo = (
        Path.home()
        / ".config"
        / "veritassec"
        / "multimodel"
        / nome
    )

    if not arquivo.is_file():
        return ""

    # Impede leitura de arquivos acessíveis
    # por outros usuários.
    modo = arquivo.stat().st_mode

    if modo & 0o077:
        return ""

    return arquivo.read_text(
        encoding="utf-8"
    ).strip()


def _agente_habilitado() -> bool:
    """Desabilitação explícita sempre prevalece."""
    valor = os.getenv("IA_HABILITADA")

    if valor is None:
        valor = os.getenv(
            "VERITASSEC_MULTIMODELO_PAPEIS",
            "false",
        )

    return valor.strip().lower() in {
        "1", "true", "sim", "yes", "on",
    }



class MotorRaciocinioAgno:
    """
    Camada cognitiva dos sete agentes.

    A LLM produz somente decisão estruturada.
    Execução de ferramentas continua exclusivamente
    sob política determinística do VeritasSec-Agent.
    """

    def __init__(
        self,
        *,
        habilitada: bool | None = None,
        provedor: str | None = None,
        modelo: str | None = None,
        api_key: str | None = None,
        temperatura: float | None = None,
        max_tokens: int | None = None,
        timeout: float | None = None,
    ) -> None:

        if habilitada is None:
            habilitada = _agente_habilitado()

        self.habilitada = bool(habilitada)

        self.provedor = (
            provedor
            or os.getenv(
                "PROVEDOR_IA",
                "gemini",
            )
        ).strip().lower()

        configuracao_painel = (
            _configuracao_multimodelo()
            if self.habilitada
            else {}
        )

        modelos_painel = {
            "gemini": "VERITASSEC_GEMINI_MODEL",
            "openai": "VERITASSEC_OPENAI_MODEL",
        }

        chave_modelo = modelos_painel.get(
            self.provedor
        )

        modelo_painel = (
            (
                os.getenv(chave_modelo)
                or configuracao_painel.get(chave_modelo)
            )
            if chave_modelo
            else None
        )

        self.modelo = (
            modelo
            or os.getenv("MODELO_IA")
            or modelo_painel
            or "gemini-2.5-flash"
        ).strip()

        if api_key:
            self.api_key = str(
                api_key
            )

        elif self.provedor == "gemini":
            self.api_key = (
                os.getenv(
                    "GEMINI_API_KEY"
                )
                or os.getenv(
                    "CHAVE_GEMINI"
                )
                or ""
            )

        elif self.provedor == "openai":
            self.api_key = (
                os.getenv(
                    "OPENAI_API_KEY"
                )
                or os.getenv(
                    "CHAVE_OPENAI"
                )
                or ""
            )

        else:
            self.api_key = ""

        if (
            self.habilitada
            and not self.api_key
            and self.provedor in {"gemini", "openai"}
        ):
            self.api_key = _credencial_multimodelo(
                self.provedor
            )

        self.ollama_url = (
            os.getenv(
                "OLLAMA_URL"
            )
            or os.getenv(
                "URL_OLLAMA"
            )
            or "http://127.0.0.1:11434"
        )

        self.temperatura = (
            float(
                os.getenv(
                    "TEMPERATURA_IA",
                    "0.1",
                )
            )
            if temperatura is None
            else float(temperatura)
        )

        self.max_tokens = (
            int(
                os.getenv(
                    "MAX_TOKENS_IA",
                    '4096',
                )
            )
            if max_tokens is None
            else int(max_tokens)
        )

        self.timeout = (
            float(
                os.getenv(
                    "TIMEOUT_IA",
                    '10',
                )
            )
            if timeout is None
            else float(timeout)
        )


    # VERITASSEC_ROTEADOR_ESTRITO_20261022
    def _candidatos_selecionados(
        self,
        papel: PapelAgente,
    ):
        """
        Retorna somente provedores selecionados.

        Cada papel utiliza uma ordem de preferencia.
        Nenhum provedor desmarcado participa.
        """
        selecionados = {
            nome.strip().lower()
            for nome in os.getenv(
                "VERITASSEC_PROVEDORES_PAPEIS",
                "",
            ).split(",")
            if nome.strip()
        }

        if not selecionados:
            return []

        permitidos = {"local", "gpt", "gemini"}

        if not selecionados.issubset(permitidos):
            raise ValueError(
                "PROVEDOR_SELECIONADO_INVALIDO"
            )

        preferencias = {
            "orquestrador":
                ("gemini", "gpt", "local"),
            "analista_codigo":
                ("local", "gpt", "gemini"),
            "superficie_ataque":
                ("gpt", "gemini", "local"),
            "hipoteses":
                ("gemini", "gpt", "local"),
            "planejador":
                ("gpt", "gemini", "local"),
            "validacao":
                ("local", "gpt", "gemini"),
            "critico_adversarial":
                ("gpt", "gemini", "local"),
        }

        configuracao = _configuracao_multimodelo()

        resultado = []

        for nome in preferencias.get(
            papel.value,
            ("gemini", "gpt", "local"),
        ):
            if nome not in selecionados:
                continue

            if nome == "gemini":
                chave = (
                    os.getenv("GEMINI_API_KEY")
                    or os.getenv("CHAVE_GEMINI")
                    or _credencial_multimodelo("gemini")
                )

                modelo = (
                    os.getenv("VERITASSEC_GEMINI_MODEL")
                    or configuracao.get(
                        "VERITASSEC_GEMINI_MODEL"
                    )
                    or "gemini-2.5-flash"
                )

                resultado.append(
                    ("gemini", modelo, chave or "")
                )

            elif nome == "gpt":
                chave = (
                    os.getenv("OPENAI_API_KEY")
                    or os.getenv("CHAVE_OPENAI")
                    or _credencial_multimodelo("openai")
                )

                modelo = (
                    os.getenv("VERITASSEC_OPENAI_MODEL")
                    or configuracao.get(
                        "VERITASSEC_OPENAI_MODEL"
                    )
                    or "gpt-4o-mini"
                )

                resultado.append(
                    ("openai", modelo, chave or "")
                )

            else:
                # VERITASSEC_MODELO_LOCAL_REAL_V1
                modelo = (
                    os.getenv("VERITASSEC_LOCAL_MODEL_API")
                    or os.getenv("VERITASSEC_LOCAL_MODEL", "")
                ).strip()

                resultado.append(
                    ("llama_cpp", modelo, "")
                )

        return resultado

    @property
    def disponivel(self) -> bool:

        if not self.habilitada:
            return False

        if (
            self.provedor
            not in PROVEDORES_SUPORTADOS
        ):
            return False

        if self.provedor in {
            "gemini",
            "openai",
        }:
            return bool(
                self.api_key
            )

        if self.provedor == "llama_cpp":
            return bool(
                os.getenv("VERITASSEC_LLAMA_BASE_URL")
                and os.getenv("VERITASSEC_LLAMA_API_KEY")
            )

        # VERITASSEC_LLAMA_DISPONIVEL_V1
        if self.provedor == "llama_cpp":
            return bool(
                os.getenv("VERITASSEC_LLAMA_BASE_URL")
                and os.getenv("VERITASSEC_LLAMA_API_KEY")
            )

        if self.provedor == "ollama":
            return bool(
                self.ollama_url
            )

        return False


    def _fallback(
        self,
        *,
        decisao_base: str,
        motivo: str,
    ) -> RegistroRaciocinioAgente:

        return RegistroRaciocinioAgente(
            modo="FALLBACK_DETERMINISTICO",
            provedor=(
                self.provedor
                if self.habilitada
                else None
            ),
            modelo=(
                self.modelo
                if self.habilitada
                else None
            ),
            chamada_modelo_realizada=False,
            fallback_deterministico=True,
            erro=motivo,
            decisao=DecisaoAgenteLLM(
                decisao=decisao_base,
                observacoes=[
                    (
                        "Decisão produzida pela política "
                        "determinística; não representa "
                        "raciocínio LLM."
                    )
                ],
                ferramentas_sugeridas=[],
                requer_evidencia_adicional=True,
                confianca=0.0,
            ),
        )

    def decidir(
        self,
        *,
        papel: PapelAgente,
        objetivo: str,
        contexto: dict[str, Any],
        decisao_base: str,
    ) -> RegistroRaciocinioAgente:

        # VERITASSEC_ETAPA1_RACIOCINIO_ESPECIALIZADO
        #
        # O painel multimodelo complementa o raciocinio
        # dos agentes. Nao autoriza sua supressao.
        #
        # A disponibilidade real do modelo continua
        # sendo validada pelas verificacoes seguintes.
        # Falhas permanecem registradas como fallback.


        # Roteamento por papel, isolado da instancia global.
        if not getattr(
            self,
            "_roteamento_executando",
            False,
        ):
            candidatos = self._candidatos_selecionados(
                papel
            )

            if candidatos:
                erros = []

                for provedor, modelo, chave in candidatos:

                    # VERITASSEC_TIMEOUT_LOCAL_ISOLADO_V1
                    timeout_provedor = self.timeout

                    if provedor == "llama_cpp":
                        import math as _math_timeout_local

                        try:
                            _limite_local = float(
                                os.getenv(
                                    "VERITASSEC_TIMEOUT_LOCAL",
                                    "180",
                                )
                            )
                            if not _math_timeout_local.isfinite(_limite_local):
                                raise ValueError("TIMEOUT_NAO_FINITO")
                        except (ValueError, TypeError):
                            _limite_local = 180.0

                        timeout_provedor = max(
                            float(self.timeout),
                            min(600.0, max(60.0, _limite_local)),
                        )


                    # VERITASSEC_TELEMETRIA_CANDIDATO_V1
                    from .telemetria_execucao import (
                        emitir_progresso_operacional,
                    )

                    emitir_progresso_operacional(
                        etapa="inferencia_modelo",
                        agente=papel.value,
                        provedor=provedor,
                        detalhe="Tentativa de inferencia LLM",
                    )


                    if not modelo:
                        erros.append(
                            provedor + ":MODELO_AUSENTE"
                        )
                        continue

                    if (
                        provedor in {"gemini", "openai"}
                        and not chave
                    ):
                        erros.append(
                            provedor + ":API_KEY_AUSENTE"
                        )
                        continue

                    if provedor == "llama_cpp":
                        if not (
                            os.getenv(
                                "VERITASSEC_LLAMA_BASE_URL"
                            )
                            and os.getenv(
                                "VERITASSEC_LLAMA_API_KEY"
                            )
                        ):
                            erros.append(
                                "llama_cpp:CONFIGURACAO_AUSENTE"
                            )
                            continue

                    motor = MotorRaciocinioAgno(
                        habilitada=self.habilitada,
                        provedor=provedor,
                        modelo=modelo,
                        api_key=chave,
                        temperatura=self.temperatura,
                        max_tokens=self.max_tokens,
                        timeout=timeout_provedor,
                    )

                    motor._roteamento_executando = True

                    resultado = motor.decidir(
                        papel=papel,
                        objetivo=objetivo,
                        contexto=contexto,
                        decisao_base=decisao_base,
                    )

                    if (
                        resultado.modo == "LLM_REAL"
                        and resultado.chamada_modelo_realizada
                    ):
                        return resultado

                    erros.append(
                        provedor
                        + ":"
                        + str(
                            resultado.erro or "FALHA_LLM"
                        ).split(":", 1)[0]
                    )

                return self._fallback(
                    decisao_base=decisao_base,
                    motivo=(
                        "PROVEDORES_SELECIONADOS_FALHARAM:"
                        + ",".join(erros)
                    ),
                )

        if not self.habilitada:
            return self._fallback(
                decisao_base=decisao_base,
                motivo="IA_DESABILITADA",
            )

        if (
            self.provedor
            not in PROVEDORES_SUPORTADOS
        ):
            return self._fallback(
                decisao_base=decisao_base,
                motivo=(
                    "PROVEDOR_NAO_SUPORTADO:"
                    + self.provedor
                ),
            )

        if (
            self.provedor
            in {
                "gemini",
                "openai",
            }
            and not self.api_key
        ):
            return self._fallback(
                decisao_base=decisao_base,
                motivo=(
                    "API_KEY_AUSENTE:"
                    + self.provedor
                ),
            )

        # Copia local para nao alterar o agente global.

        # VERITASSEC_PROVEDOR_DURANTE_INFERENCIA_20261023
        from .telemetria_execucao import (
            emitir_progresso_operacional,
        )

        emitir_progresso_operacional(
            etapa="inferencia_modelo",
            agente=papel.value,
            provedor=self.provedor,
            detalhe="Inferencia LLM em andamento",
        )

        agente = copy.copy(
            REGISTRO_AGENTES.obter(
                papel
            )
        )

        # Cada Agent Agno real recebe explicitamente o
        # modelo Gemini configurado. Nenhuma tool é anexada.
        agente.model = (
            construir_modelo_agno(
                provedor=self.provedor,
                modelo=self.modelo,
                api_key=self.api_key,
                temperatura=(
                    self.temperatura
                ),
                max_tokens=(
                    self.max_tokens
                ),
                timeout=self.timeout,
                ollama_url=(
                    self.ollama_url
                ),
            )
        )

        prompt = {
            "papel": papel.value,
            "objetivo": objetivo,
            "contexto": contexto,
            "formato_resposta": {
                "tipo": "JSON_estruturado",
                "decisao": "texto objetivo, ate 300 caracteres",
                "observacoes": "ate 3 observacoes curtas",
                "ferramentas_sugeridas": "somente se necessario",
                "sementes_sugeridas": "somente se necessario",
                "requer_evidencia_adicional": "booleano",
                "confianca": "numero entre 0 e 1",
                "regra": (
                    "Responda de forma breve e completa. "
                    "Nao inclua explicacoes fora do JSON. "
                    "Nao invente evidencia."
                ),
            },
            "contrato_seeds": {
                "campo": "sementes_sugeridas",
                "tipo": "lista_de_strings",
                "maximo": 16,
                "tamanho_maximo": 512,
                "regra": (
                    "Sugira seeds somente no campo tipado. "
                    "Não gere comandos de shell. "
                    "Seeds não concedem autorização."
                ),
            },
            "restricoes_obrigatorias": [
                (
                    "Não declare vulnerabilidade confirmada "
                    "somente por raciocínio."
                ),
                (
                    "Não invente evidências, execução, "
                    "alcance ou impacto."
                ),
                (
                    "Não amplie o escopo."
                ),
                (
                    "Não forneça comandos de shell."
                ),
                (
                    "Ferramentas sugeridas são apenas "
                    "recomendações; a política determinística "
                    "decide se podem ser executadas."
                ),
                (
                    "Diferencie observação, hipótese e "
                    "evidência."
                ),
            ],
        }


        # VS_RETRY_CHAMADA_REAL_V3
        # Repete somente a inferencia; nunca ferramentas.
        def _executar_run_com_retry(*args, **kwargs):
            import time as _vs_time

            _permitido = (
                self.provedor == "gemini"
                and os.getenv(
                    "VERITASSEC_RETRY_TRANSITORIO",
                    "1",
                ).strip().lower()
                not in {"0", "false", "nao", "off"}
            )

            _limite = 2 if _permitido else 1

            for _indice in range(_limite):
                try:
                    return agente.run(*args, **kwargs)

                except Exception as _exc:
                    _erro = str(_exc).lower()
                    _tipo = type(_exc).__name__.lower()

                    _transitorio = (
                        "deadline_exceeded" in _erro
                        or "504" in _erro
                        or "timed out" in _erro
                        or "timeout" in _tipo
                    )

                    if (
                        _indice + 1 >= _limite
                        or not _transitorio
                    ):
                        raise

                    _vs_time.sleep(0.25)

        try:
            resposta = _executar_run_com_retry(
                json.dumps(
                    prompt,
                    ensure_ascii=False,
                    default=str,
                ),
                output_schema=DecisaoAgenteLLM,
                stream=False,
            )

            conteudo = getattr(
                resposta,
                "content",
                None,
            )

            if isinstance(
                conteudo,
                DecisaoAgenteLLM,
            ):
                decisao = conteudo

            elif isinstance(
                conteudo,
                dict,
            ):
                decisao = (
                    DecisaoAgenteLLM
                    .model_validate(
                        conteudo
                    )
                )

            elif isinstance(
                conteudo,
                str,
            ):
                decisao = (
                    DecisaoAgenteLLM
                    .model_validate_json(
                        conteudo
                    )
                )

            else:
                raise TypeError(
                    "resposta Agno sem conteúdo "
                    "estruturado reconhecível"
                )

            return RegistroRaciocinioAgente(
                modo="LLM_REAL",
                provedor=self.provedor,
                modelo=self.modelo,
                chamada_modelo_realizada=True,
                fallback_deterministico=False,
                erro=None,
                decisao=decisao,
            )

        except Exception as exc:
            # Fail closed:
            # a indisponibilidade da LLM não é mascarada.
            # A investigação pode continuar deterministicamente,
            # mas isso fica explicitamente registrado.
            return self._fallback(
                decisao_base=decisao_base,
                motivo=(
                    "FALHA_LLM:"
                    + type(exc).__name__
                    + ":"
                    + str(exc)[:300]
                ),
            )

