from __future__ import annotations

import re

from pathlib import Path


ESTATICAS = (
    "run-shell-injection",
    "missing-integrity",
    "detected-generic-secret",
    "detected-jwt-token",
    "hardcoded-hmac-key",
    "hardcoded-jwt-secret",
    "jwt-hardcode",
)


def _get(
    obj,
    nome,
    default=None,
):
    if isinstance(
        obj,
        dict,
    ):
        return obj.get(
            nome,
            default,
        )

    return getattr(
        obj,
        nome,
        default,
    )


def _contexto(
    achado,
    raio=20,
):
    # Resolve o caminho SARIF contra a raiz autenticada do projeto.
    # Sem raiz válida, não interpreta arquivos relativos pelo CWD da API.
    arquivo = str(_get(achado, "arquivo", "") or "")
    meta = _get(achado, "metadados", {}) or {}
    raiz_informada = meta.get("projeto") if isinstance(meta, dict) else None
    p = Path(arquivo)
    if not p.is_absolute():
        if not raiz_informada:
            return ""
        raiz = Path(str(raiz_informada)).expanduser().resolve()
        p = (raiz / p).resolve()
        if not p.is_relative_to(raiz):
            return ""
    else:
        p = p.expanduser().resolve()
        if raiz_informada:
            raiz = Path(str(raiz_informada)).expanduser().resolve()
            if not p.is_relative_to(raiz):
                return ""
    if not p.is_file() or p.stat().st_size > 2_000_000:
        return ""

    linhas = p.read_text(
        encoding="utf-8",
        errors="replace",
    ).splitlines()

    try:
        n = int(
            _get(
                achado,
                "linha",
                1,
            )
            or 1
        )
    except Exception:
        n = 1

    pos = max(
        0,
        n - 1,
    )

    return "\n".join(
        linhas[
            max(
                0,
                pos - raio,
            ):
            min(
                len(linhas),
                pos + raio + 1,
            )
        ]
    )


def _estatica(
    regra,
):
    r = str(
        regra
    ).lower()

    return any(
        x in r
        for x in ESTATICAS
    )


def _prova(
    achado,
):
    regra = str(
        _get(
            achado,
            "regra",
            "",
        )
    ).lower()

    texto = _contexto(
        achado
    )

    if (
        "run-shell-injection"
        in regra
    ):

        ok = bool(
            re.search(
                r'''
                run\s*:
                [\s\S]{0,1200}?
                \$\{\{
                \s*github\.
                ''',
                texto,
                re.I | re.X,
            )
        )

        return (
            ok,
            (
                "Contexto github interpolado "
                "em bloco run."
            ),
        )

    if (
        "detected-jwt-token"
        in regra
    ):

        ok = bool(
            re.search(
                r'''
                eyJ
                [A-Za-z0-9_-]{4,}
                \.
                [A-Za-z0-9_-]{4,}
                \.
                [A-Za-z0-9_-]{4,}
                ''',
                texto,
                re.X,
            )
        )

        return (
            ok,
            "JWT literal observado.",
        )

    if (
        "missing-integrity"
        in regra
    ):

        tags = re.findall(
            r'''
            <
            (?:script|link)
            \b
            [^>]{1,2500}
            >
            ''',
            texto,
            re.I | re.X,
        )

        externos = [
            tag
            for tag in tags
            if (
                "http://" in tag.lower()
                or "https://" in tag.lower()
                or 'src="//' in tag.lower()
                or 'href="//' in tag.lower()
            )
        ]

        ok = any(
            "integrity="
            not in tag.lower()
            for tag in externos
        )

        return (
            ok,
            "Recurso externo sem integrity.",
        )

    if (
        "hardcoded-hmac-key"
        in regra
        or "hardcoded-jwt-secret"
        in regra
        or "jwt-hardcode"
        in regra
    ):

        ok = any(
            re.search(
                padrao,
                texto,
                re.I | re.X,
            )
            is not None
            for padrao in (
                r'''
                createHmac
                \s*\(
                [\s\S]{0,700}
                ['"][^'"]{3,}['"]
                ''',

                r'''
                jwt\.
                (?:sign|verify)
                \s*\(
                [\s\S]{0,700}
                ['"][^'"]{3,}['"]
                ''',

                r'''
                (?:
                    secret|
                    hmac|
                    key
                )
                [A-Za-z0-9_$]*
                \s*[:=]\s*
                ['"][^'"]{3,}['"]
                ''',
            )
        )

        return (
            ok,
            "Chave/segredo literal observado.",
        )

    if (
        "detected-generic-secret"
        in regra
    ):

        ok = bool(
            re.search(
                r'''
                (?:
                    password|
                    passwd|
                    secret|
                    token|
                    api[_-]?key|
                    private[_-]?key
                )
                [A-Za-z0-9_$-]*
                \s*[:=]\s*
                ['"][^'"]{4,}['"]
                ''',
                texto,
                re.I | re.X,
            )
        )

        return (
            ok,
            "Segredo literal observado.",
        )

    return (
        False,
        "Sem prova estática direta.",
    )


def _bool_rec(
    obj,
    nomes,
):
    if isinstance(
        obj,
        dict,
    ):

        for chave, valor in obj.items():

            if (
                chave in nomes
                and valor is True
            ):
                return True

            if _bool_rec(
                valor,
                nomes,
            ):
                return True

    elif isinstance(
        obj,
        list,
    ):

        return any(
            _bool_rec(
                x,
                nomes,
            )
            for x in obj
        )

    return False


def classificar_veredito_multivariado(
    *,
    achado,
    resultado,
):
    regra = str(
        _get(
            achado,
            "regra",
            "",
        )
    )

    meta = (
        _get(
            achado,
            "metadados",
            {},
        )
        or {}
    )

    resolucao = (
        meta.get(
            "resolucao_endpoint",
            {},
        )
        if isinstance(
            meta,
            dict,
        )
        else {}
    )

    endpoint = bool(
        resolucao.get(
            "resolvido"
        )
    )

    scr = (
        resultado.get(
            "scr",
            {},
        )
        or {}
    )

    sustentacao = str(
        scr.get(
            "nivel_sustentacao",
            "INCONCLUSIVO",
        )
    )

    ausentes = list(
        scr.get(
            "evidencias_ausentes",
            [],
        )
        or []
    )

    agregado = {
        "ciclo":
            resultado.get(
                "ciclo_adaptativo_operacional",
                {},
            ),

        "aquisicao":
            resultado.get(
                "aquisicao_evidencia",
                {},
            ),
    }

    dinamica = (
        bool(
            resultado.get(
                "evidencia_dinamica",
                False,
            )
        )
        or _bool_rec(
            agregado,
            {
                "evidencia_dinamica",
                "observavel",
            },
        )
    )

    oracle = (
        bool(
            resultado.get(
                "evidencia_oraculo",
                False,
            )
        )
        or _bool_rec(
            agregado,
            {
                "evidencia_oraculo",
            },
        )
    )

    violacao = _bool_rec(
        agregado,
        {
            "violacao",
            "violacao_confirmada",
        },
    )

    if _estatica(
        regra
    ):

        ok, prova = _prova(
            achado
        )

        # VERITASSEC_POLITICA_EVIDENCIA_ESTATICA_V1
        # Uma observacao estatica nao comprova automaticamente
        # exposicao, validade ou explorabilidade de credenciais.
        caminho_achado = str(
            _get(achado, "arquivo", "")
        ).replace("\\\\", "/").lower()

        arquivo_teste = (
            caminho_achado.endswith(
                (".spec.ts", ".test.ts", ".spec.js", ".test.js")
            )
            or "/__tests__/" in caminho_achado
            or "/test/" in caminho_achado
            or "/tests/" in caminho_achado
        )

        regra_credencial = any(
            termo in regra.lower()
            for termo in (
                "detected-jwt-token",
                "detected-generic-secret",
                "hardcoded-hmac-key",
                "hardcoded-jwt-secret",
                "jwt-hardcode",
            )
        )

        if ok and arquivo_teste and regra_credencial:
            return {
                "classificacao_final": "INCONCLUSIVO",
                "justificativa_classificacao": (
                    "Propriedade estatica observada: "
                    + prova
                    + " O artefato pertence a codigo de teste. "
                    "A observacao nao comprova que a credencial "
                    "seja real, ativa, sensivel ou utilizada "
                    "pela aplicacao em producao."
                ),
                "propriedade_observada": prova,
                "propriedade_comprovada": (
                    "Presenca do padrao estatico no artefato"
                ),
                "evidencias_sustentacao": [
                    "Padrao estatico identificado no codigo",
                    "Arquivo identificado como artefato de teste",
                ],
                "limitacoes": [
                    "Validade da credencial nao comprovada",
                    "Uso em producao nao comprovado",
                    "Explorabilidade nao comprovada",
                ],
                "evidencias_ausentes": [
                    "validade_credencial_nao_comprovada",
                    "uso_producao_nao_comprovado",
                    "explorabilidade_nao_comprovada",
                ],
                "fonte_veredito": (
                    "OBSERVACAO_ESTATICA_EM_ARQUIVO_TESTE"
                ),
                "sustentacao_scr": sustentacao,
                "endpoint_resolvido": endpoint,
                "evidencia_dinamica": dinamica,
                "evidencia_oraculo": oracle,
            }

        if ok:

            return {
                "classificacao_final":
                    "VERDADEIRO_POSITIVO",
                "propriedade_observada": prova,
                "propriedade_comprovada": (
                    "Presenca do padrao estatico no artefato"
                ),
                "evidencias_sustentacao": [
                    "Verificacao estatica direta do artefato"
                ],
                "limitacoes": [
                    "Explorabilidade nao demonstrada "
                    "por esta verificacao estatica",
                    "Impacto no contexto da aplicacao "
                    "depende da propriedade analisada",
                ],

                "justificativa_classificacao":
                    (
                        "A propriedade indicada "
                        "pela regra foi demonstrada "
                        "diretamente no artefato. "
                        + prova
                    ),

                "evidencias_ausentes":
                    [],

                "fonte_veredito":
                    "EVIDENCIA_ESTATICA_DIRETA",

                "sustentacao_scr":
                    sustentacao,

                "endpoint_resolvido":
                    endpoint,

                "evidencia_dinamica":
                    dinamica,

                "evidencia_oraculo":
                    oracle,
            }

        ausentes.append(
            "prova_estatica_direta_nao_demonstrada"
        )

    if (
        dinamica
        and oracle
        and violacao
    ):

        return {
            "classificacao_final":
                "VERDADEIRO_POSITIVO",

            "justificativa_classificacao":
                (
                    "Violação reproduzida "
                    "dinamicamente e confirmada "
                    "pelo Security Oracle."
                ),

            "evidencias_ausentes":
                [],

            "fonte_veredito":
                "DINAMICA_MAIS_ORACLE",

            "sustentacao_scr":
                sustentacao,

            "endpoint_resolvido":
                endpoint,

            "evidencia_dinamica":
                True,

            "evidencia_oraculo":
                True,
        }

    motivo = str(
        resultado.get(
            "motivo_termino",
            "",
        )
    )

    if (
        dinamica
        and oracle
        and not violacao
        and motivo
        in {
            "EVIDENCIA_SUFICIENTE_REFUTADA",
            "HIPOTESE_REFUTADA",
        }
    ):

        return {
            "classificacao_final":
                "FALSO_POSITIVO",

            "justificativa_classificacao":
                (
                    "Hipótese refutada "
                    "explicitamente por validação "
                    "dinâmica e Oracle."
                ),

            "evidencias_ausentes":
                [],

            "fonte_veredito":
                "REFUTACAO_EXPLICITA",

            "sustentacao_scr":
                sustentacao,

            "endpoint_resolvido":
                endpoint,

            "evidencia_dinamica":
                True,

            "evidencia_oraculo":
                True,
        }

    if not _estatica(
        regra
    ):

        if not endpoint:
            ausentes.append(
                "endpoint_runtime_nao_demonstrado"
            )

        if not dinamica:
            ausentes.append(
                "evidencia_dinamica_ausente"
            )

        if not oracle:
            ausentes.append(
                "security_oracle_ausente"
            )

    if (
        str(
            resultado.get(
                "estado_final",
                "",
            )
        )
        == "NAO_REPRODUZIDO"
    ):
        ausentes.append(
            "nao_reproduzido_sem_refutacao_explicita"
        )

    ausentes = list(
        dict.fromkeys(
            ausentes
        )
    )

    if not ausentes:
        ausentes = [
            "suficiencia_de_evidencia_nao_atingida"
        ]

    return {
        "classificacao_final":
            "INCONCLUSIVO",

        "justificativa_classificacao":
            (
                "Evidência insuficiente para "
                "confirmar ou refutar. "
                f"SCR={sustentacao}; "
                f"endpoint={endpoint}; "
                f"dinamica={dinamica}; "
                f"oracle={oracle}."
            ),

        "evidencias_ausentes":
            ausentes,

        "fonte_veredito":
            "EVIDENCIA_INSUFICIENTE",

        "sustentacao_scr":
            sustentacao,

        "endpoint_resolvido":
            endpoint,

        "evidencia_dinamica":
            dinamica,

        "evidencia_oraculo":
            oracle,
    }
