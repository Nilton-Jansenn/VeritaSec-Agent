from __future__ import annotations

import re

from functools import lru_cache
from pathlib import Path


EXT = {
    ".ts",
    ".js",
    ".tsx",
    ".jsx",
}


def _path(valor):
    valor = str(
        valor or ""
    ).strip()

    if not valor:
        return None

    if (
        "://" in valor
        or "${" in valor
        or "\x00" in valor
        or len(valor) > 300
    ):
        return None

    if re.match(
        r"^/?eyJ[A-Za-z0-9_-]+\.",
        valor,
    ):
        return None

    if not valor.startswith("/"):
        valor = "/" + valor

    return re.sub(
        r"/+",
        "/",
        valor,
    )


def _resolve_import(
    arquivo,
    modulo,
):
    base = (
        arquivo.parent
        / modulo
    ).resolve()

    candidatos = [
        base,
        base.with_suffix(".ts"),
        base.with_suffix(".js"),
        base.with_suffix(".tsx"),
        base.with_suffix(".jsx"),
        base / "index.ts",
        base / "index.js",
    ]

    for p in candidatos:

        if p.is_file():
            return p

    return None


@lru_cache(
    maxsize=4
)
def _indexar(
    projeto_str,
):
    projeto = Path(
        projeto_str
    ).resolve()

    rotas = {}
    imports = {}

    for arquivo in projeto.rglob("*"):

        if (
            not arquivo.is_file()
            or arquivo.suffix.lower()
            not in EXT
        ):
            continue

        arquivo = arquivo.resolve()

        try:
            texto = arquivo.read_text(
                encoding="utf-8",
                errors="replace",
            )
        except OSError:
            continue

        chave = str(
            arquivo
        )

        objetos = {
            "app",
            "router",
            "server",
        }

        for m in re.finditer(
            r'''
            (?:
                const|let|var
            )
            \s+
            ([A-Za-z_$][A-Za-z0-9_$]*)
            \s*=\s*
            (?:
                express\s*\.\s*Router
                |
                Router
            )
            \s*\(
            ''',
            texto,
            re.I | re.X,
        ):

            objetos.add(
                m.group(1)
            )

        obj_re = "|".join(
            re.escape(x)
            for x in sorted(
                objetos,
                key=len,
                reverse=True,
            )
        )

        rota_re = re.compile(
            rf'''
            (?<![A-Za-z0-9_$])
            (?P<obj>{obj_re})
            \s*\.\s*
            (?P<metodo>
                get|post|put|patch|
                delete|head|options|use
            )
            \s*\(
            \s*
            (?P<q>['"`])
            (?P<path>[^'"`]+)
            (?P=q)
            ''',
            re.I | re.X,
        )

        rotas[
            chave
        ] = []

        for m in rota_re.finditer(
            texto
        ):

            caminho = _path(
                m.group(
                    "path"
                )
            )

            if not caminho:
                continue

            linha = (
                texto.count(
                    "\n",
                    0,
                    m.start(),
                )
                + 1
            )

            rotas[
                chave
            ].append({
                "arquivo_registro":
                    chave,

                "linha_registro":
                    linha,

                "metodo":
                    m.group(
                        "metodo"
                    ).upper(),

                "caminho":
                    caminho,

                "trecho":
                    texto[
                        m.start():
                        min(
                            len(texto),
                            m.start() + 1500,
                        )
                    ],
            })

        imports[
            chave
        ] = []

        for m in re.finditer(
            r'''
            import\s+
            ([A-Za-z_$][A-Za-z0-9_$]*)
            \s+from\s+
            ['"](\.[^'"]+)['"]
            ''',
            texto,
            re.X,
        ):

            alvo = _resolve_import(
                arquivo,
                m.group(2),
            )

            if alvo:

                imports[
                    chave
                ].append({
                    "alias":
                        m.group(1),

                    "alvo":
                        str(alvo),
                })

        for m in re.finditer(
            r'''
            import\s*\{
            ([^}]+)
            \}\s*from\s*
            ['"](\.[^'"]+)['"]
            ''',
            texto,
            re.X,
        ):

            alvo = _resolve_import(
                arquivo,
                m.group(2),
            )

            if not alvo:
                continue

            for item in m.group(
                1
            ).split(","):

                item = item.strip()

                if not item:
                    continue

                partes = re.split(
                    r"\s+as\s+",
                    item,
                    maxsplit=1,
                )

                alias = (
                    partes[1].strip()
                    if len(partes) == 2
                    else partes[0].strip()
                )

                imports[
                    chave
                ].append({
                    "alias":
                        alias,

                    "alvo":
                        str(alvo),
                })

    return {
        "rotas": rotas,
        "imports": imports,
    }




# VERITASSEC_ESCOPO_LEXICO_ROTA_20261027
def _rota_abrange_linha(rota, arquivo, linha):
    """
    Demonstra que a linha esta dentro da expressao
    de registro de uma rota JavaScript/TypeScript.

    Nao deduz uma rota apenas por proximidade.
    Em caso de sintaxe nao reconhecida, retorna False.
    """
    try:
        alvo = Path(arquivo).resolve()

        if not alvo.is_file():
            return False

        registro = Path(
            rota["arquivo_registro"]
        ).resolve()

        if registro != alvo:
            return False

        linha_alvo = int(linha)
        linha_registro = int(
            rota["linha_registro"]
        )

        if linha_alvo < linha_registro:
            return False

        texto = alvo.read_text(
            encoding="utf-8",
            errors="replace",
        )

        linhas = texto.splitlines(
            keepends=True
        )

        if not (
            1 <= linha_registro <= len(linhas)
            and 1 <= linha_alvo <= len(linhas)
        ):
            return False

        inicio_linha = sum(
            len(item)
            for item in linhas[:linha_registro - 1]
        )

        trecho = str(
            rota.get("trecho") or ""
        )

        if len(trecho) < 12:
            return False

        assinatura = trecho[:min(80, len(trecho))]

        inicio = texto.find(
            assinatura,
            inicio_linha,
            min(
                len(texto),
                inicio_linha + 2000
            ),
        )

        if inicio < 0:
            return False

        # A assinatura encontrada precisa iniciar na
        # linha do registro original.
        if (
            texto.count("\n", 0, inicio) + 1
            != linha_registro
        ):
            return False

        abertura = texto.find(
            "(",
            inicio,
            inicio + 200,
        )

        if abertura < 0:
            return False

        profundidade = 0
        string = None
        comentario_linha = False
        comentario_bloco = False
        escape = False
        fechamento = None

        limite = min(
            len(texto),
            abertura + 100000,
        )

        i = abertura

        while i < limite:
            c = texto[i]
            prox = (
                texto[i + 1]
                if i + 1 < limite
                else ""
            )

            if comentario_linha:
                if c == "\n":
                    comentario_linha = False
                i += 1
                continue

            if comentario_bloco:
                if c == "*" and prox == "/":
                    comentario_bloco = False
                    i += 2
                else:
                    i += 1
                continue

            if string is not None:
                if escape:
                    escape = False
                elif c == "\\":
                    escape = True
                elif c == string:
                    string = None

                i += 1
                continue

            if c == "/" and prox == "/":
                comentario_linha = True
                i += 2
                continue

            if c == "/" and prox == "*":
                comentario_bloco = True
                i += 2
                continue

            if c in ("'", '"'):
                string = c
                i += 1
                continue

            # Template literals com interpolacao
            # exigem analisador especializado.
            # Nao atribuir endpoint neste caso.
            if c == "`":
                return False

            if c == "(":
                profundidade += 1

            elif c == ")":
                profundidade -= 1

                if profundidade == 0:
                    fechamento = i
                    break

                if profundidade < 0:
                    return False

            i += 1

        if fechamento is None:
            return False

        linha_final = (
            texto.count("\n", 0, fechamento) + 1
        )

        return (
            linha_registro
            <= linha_alvo
            <= linha_final
        )

    except (
        OSError,
        ValueError,
        TypeError,
        KeyError,
        IndexError,
    ):
        return False



def _handler_na_chamada(trecho, alias):
    """Exige referência ao handler dentro da chamada Express."""
    import re

    if not isinstance(trecho, str):
        return False
    if not isinstance(alias, str):
        return False
    if not re.fullmatch(r"[A-Za-z_$][A-Za-z0-9_$]*", alias):
        return False

    inicio = trecho.find("(")
    if inicio < 0:
        return False

    nivel = 0
    estado = None
    comentario = None
    escape = False
    i = inicio
    argumentos = []
    fim = False

    while i < len(trecho):
        c = trecho[i]
        prox = trecho[i + 1:i + 2]

        if comentario == "linha":
            if c == "\\n":
                comentario = None
            i += 1
            continue

        if comentario == "bloco":
            if c == "*" and prox == "/":
                comentario = None
                i += 2
                continue
            i += 1
            continue

        if estado:
            if escape:
                escape = False
            elif c == "\\\\":
                escape = True
            elif c == estado:
                estado = None
            argumentos.append(" ")
            i += 1
            continue

        if c == "/" and prox == "/":
            comentario = "linha"
            i += 2
            continue
        if c == "/" and prox == "*":
            comentario = "bloco"
            i += 2
            continue
        if c in ("'", '"', "`"):
            estado = c
            argumentos.append(" ")
            i += 1
            continue

        if c == "(":
            nivel += 1
        elif c == ")":
            nivel -= 1
            if nivel == 0:
                fim = True
                break
            if nivel < 0:
                return False

        argumentos.append(c)
        i += 1

    if not fim:
        return False

    texto = "".join(argumentos)
    return bool(
        re.search(
            r"(?<![A-Za-z0-9_$])"
            + re.escape(alias)
            + r"(?![A-Za-z0-9_$])",
            texto,
        )
    )


def resolver_endpoints(
    *,
    arquivo,
    linha,
    projeto,
):
    raiz = Path(
        projeto
    ).resolve()

    alvo = Path(
        arquivo
    ).resolve()

    try:
        alvo.relative_to(
            raiz
        )
    except Exception:
        return {
            "resolvido": False,
            "motivo":
                "ARQUIVO_FORA_DO_PROJETO",
            "candidatos": [],
        }

    if (
        alvo.suffix.lower()
        not in EXT
    ):
        return {
            "resolvido": False,
            "motivo":
                "ARTEFATO_NAO_ROTEAVEL",
            "candidatos": [],
        }

    idx = _indexar(
        str(raiz)
    )

    alvo_s = str(
        alvo
    )

    candidatos = []

    # Direto.
    for r in idx[
        "rotas"
    ].get(
        alvo_s,
        [],
    ):

        if (
            r[
                "metodo"
            ]
            != "USE"
        ):
            candidatos.append({
                **r,
                "origem":
                    "ROTA_DIRETA",
            })

    # Importação direta do handler.
    for arquivo_registro, itens in (
        idx[
            "imports"
        ].items()
    ):

        for imp in itens:

            if (
                imp[
                    "alvo"
                ]
                != alvo_s
            ):
                continue

            alias = imp[
                "alias"
            ]

            for r in idx[
                "rotas"
            ].get(
                arquivo_registro,
                [],
            ):

                if not _handler_na_chamada(r.get('trecho', ''), alias):
                    continue

                candidatos.append({
                    **r,

                    "origem":
                        "HANDLER_IMPORTADO",
                })

    # Deduplicar.
    unicos = {}

    for c in candidatos:

        caminho = _path(
            c.get(
                "caminho"
            )
        )

        if not caminho:
            continue

        assert not caminho.startswith(
            "/eyJ"
        )

        chave = (
            c.get(
                "metodo"
            ),
            caminho,
        )

        unicos[
            chave
        ] = {
            **c,
            "caminho":
                caminho,
        }

    candidatos = list(
        unicos.values()
    )

    escolhida = None

    try:
        linha_i = int(
            linha
        )
    except Exception:
        linha_i = None


    # VERITASSEC_CORRECAO_ASSOCIACAO_20261101
    #
    # A proximidade entre a linha SAST e o registro
    # de uma rota não comprova vínculo funcional.
    #
    # A seleção direta exige escopo léxico demonstrado.
    # Associações por handler importado continuam
    # sujeitas à resolução inequívoca.

    if linha_i is not None:
        abrangentes = [
            c
            for c in candidatos
            if (
                c.get("arquivo_registro") == alvo_s
                and _rota_abrange_linha(
                    c,
                    alvo_s,
                    linha_i,
                )
            )
        ]

        if len(abrangentes) == 1:
            escolhida = {
                **abrangentes[0],
                "origem":
                    "ROTA_COM_ESCOPO_LEXICO_DEMONSTRADO",
            }

    if (
        escolhida is None
        and len(
            candidatos
        ) == 1
    ):
        escolhida = candidatos[
            0
        ]

    # VERITASSEC_ESCOPO_LEXICO_ROTA_20261027
    # Resolve apenas quando exatamente uma rota
    # comprovadamente contem a linha investigada.
    if (
        escolhida is None
        and linha_i is not None
        and len(candidatos) > 1
    ):
        abrangentes = [
            c
            for c in candidatos
            if _rota_abrange_linha(
                c,
                alvo_s,
                linha_i,
            )
        ]

        if len(abrangentes) == 1:
            escolhida = {
                **abrangentes[0],
                "origem":
                    "ROTA_COM_ESCOPO_LEXICO_DEMONSTRADO",
            }

    if escolhida is None:

        return {
            "resolvido": False,

            "motivo":
                (
                    "SEM_ENDPOINT_DEMONSTRADO"
                    if not candidatos
                    else
                    "ENDPOINT_AMBIGUO"
                ),

            "quantidade_candidatos":
                len(
                    candidatos
                ),

            "candidatos":
                candidatos,
        }

    return {
        "resolvido":
            True,

        "motivo":
            escolhida[
                "origem"
            ],

        "metodo_http":
            escolhida[
                "metodo"
            ],

        "caminho_http":
            escolhida[
                "caminho"
            ],

        "prova":
            escolhida,

        "quantidade_candidatos":
            len(
                candidatos
            ),

        "candidatos":
            candidatos,
    }


def enriquecer_achado_endpoint(
    achado,
    *,
    projeto,
):
    saida = dict(
        achado
    )

    resolucao = resolver_endpoints(
        arquivo=saida.get(
            "arquivo",
            "",
        ),
        linha=saida.get(
            "linha"
        ),
        projeto=projeto,
    )

    meta = dict(
        saida.get(
            "metadados",
            {},
        )
        or {}
    )

    meta[
        "resolucao_endpoint"
    ] = resolucao

    saida[
        "metadados"
    ] = meta

    if resolucao.get(
        "resolvido"
    ):

        saida[
            "caminho_http"
        ] = resolucao[
            "caminho_http"
        ]

        metodo = resolucao[
            "metodo_http"
        ]

        if (
            metodo
            and metodo
            != "ANY"
        ):

            saida[
                "metodo_http"
            ] = metodo

    return saida
