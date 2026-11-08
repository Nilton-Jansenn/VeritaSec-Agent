from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re


@dataclass(slots=True)
class EvidenciaSCR:
    tipo: str
    descricao: str
    linha: int | None = None
    trecho: str | None = None

    def dump(self):
        return {
            "tipo": self.tipo,
            "descricao": self.descricao,
            "linha": self.linha,
            "trecho": self.trecho,
        }


@dataclass(slots=True)
class ResultadoSCR:
    executado: bool
    arquivo: str
    linha_referencia: int | None
    classe_vulnerabilidade: str | None

    entradas_identificadas: list[EvidenciaSCR] = field(
        default_factory=list
    )
    propagacoes_identificadas: list[EvidenciaSCR] = field(
        default_factory=list
    )
    sinks_identificados: list[EvidenciaSCR] = field(
        default_factory=list
    )
    controles_identificados: list[EvidenciaSCR] = field(
        default_factory=list
    )
    validacoes_sanitizacoes: list[EvidenciaSCR] = field(
        default_factory=list
    )
    controles_autorizacao: list[EvidenciaSCR] = field(
        default_factory=list
    )

    precondicoes: list[str] = field(default_factory=list)
    propriedade_seguranca: str | None = None

    evidencias_encontradas: list[str] = field(default_factory=list)
    evidencias_ausentes: list[str] = field(default_factory=list)

    nivel_sustentacao: str = "INCONCLUSIVO"
    hipotese_sustentada: bool = False

    observacoes: list[str] = field(default_factory=list)

    def dump(self):
        d = {
            nome: getattr(self, nome)
            for nome in self.__dataclass_fields__
        }

        return {
            chave: (
                [item.dump() for item in valor]
                if isinstance(valor, list)
                and valor
                and isinstance(valor[0], EvidenciaSCR)
                else valor
            )
            for chave, valor in d.items()
        }


ENTRADAS = (
    r"\breq\.(params|query|body|headers|cookies)\b",
    r"\brequest\.(args|form|json|headers|cookies)\b",
    r"@RequestParam\b",
    r"@PathVariable\b",
    r"@RequestBody\b",
    r"\bgetParameter\s*\(",
)

SINKS = (
    r"\breadFile\s*\(",
    r"\breadFileSync\s*\(",
    r"\bcreateReadStream\s*\(",
    r"\bwriteFile\s*\(",
    r"\bopen\s*\(",
    r"\bPaths\.get\s*\(",
    r"\bPath\.of\s*\(",
    r"\bnew\s+File\s*\(",
    r"\bexec\s*\(",
    r"\bspawn\s*\(",
    r"\bProcessBuilder\b",
)

VALIDACOES = (
    r"\bvalidate",
    r"\bvalidar",
    r"\bsanitize",
    r"\bnormalize",
    r"\bresolve",
    r"\bcanonical",
    r"\ballowlist",
    r"\bstartsWith\s*\(",
)

AUTORIZACOES = (
    r"\bauthoriz",
    r"\bautoriz",
    r"\bpermission",
    r"\brole\b",
    r"\bowner",
    r"\bhasRole",
    r"\bhasAuthority",
)


def localizar(linhas, padroes, tipo, inicio):
    return [
        EvidenciaSCR(
            tipo=tipo,
            descricao=f"Padrao {tipo} observado no codigo.",
            linha=numero,
            trecho=texto.strip()[:500],
        )
        for numero, texto in enumerate(linhas, inicio)
        if any(
            re.search(padrao, texto, re.I)
            for padrao in padroes
        )
    ]



# VERITASSEC_ETAPA2_PROPAGACAO
def identificar_propagacoes_simples(linhas, inicio):
    """
    Identifica ligacao sintatica direta entre
    entrada HTTP e argumento de operacao sensivel.

    Nao comprova fluxo semantico, ausencia de
    sanitizacao ou explorabilidade.
    """

    atribuicao = re.compile(
        r"\b(?:const|let|var)\s+"
        r"([A-Za-z_$][\w$]*)\s*=\s*"
        r"(?:req\.(?:params|query|body|headers|cookies)"
        r"|request\.(?:args|form|json|headers|cookies))"
        r"(?:\.|\[)",
        re.I,
    )

    sink = re.compile(
        r"\b(?:readFile|readFileSync|createReadStream|"
        r"writeFile|open|exec|spawn)\s*\(\s*"
        r"([A-Za-z_$][\w$]*)\b",
        re.I,
    )

    origens = []
    evidencias = []

    for numero, texto in enumerate(linhas, inicio):

        for achado in atribuicao.finditer(texto):
            origens.append((achado.group(1), numero))

        for achado in sink.finditer(texto):

            variavel = achado.group(1)

            for nome, linha_origem in origens:

                if nome == variavel and linha_origem <= numero:
                    evidencias.append(
                        EvidenciaSCR(
                            tipo="PROPAGACAO_SINTATICA",
                            descricao=(
                                "Ligacao sintatica observada. "
                                "Fluxo semantico nao comprovado."
                            ),
                            linha=numero,
                            trecho=texto.strip()[:500],
                        )
                    )
                    break

    return evidencias


def executar_scr(
    *,
    arquivo: str,
    linha: int | None,
    regra=None,
    cwe=None,
    mensagem=None,
    endpoint=None,
    metodo_http=None,
):
    caminho = Path(arquivo).expanduser().resolve()
    classe = cwe or regra or "NAO_CLASSIFICADA"

    if not caminho.is_file():
        return ResultadoSCR(
            executado=False,
            arquivo=str(caminho),
            linha_referencia=linha,
            classe_vulnerabilidade=classe,
            evidencias_ausentes=[
                "arquivo_fonte_indisponivel",
                "source_nao_verificado",
                "sink_nao_verificado",
            ],
        )

    linhas = caminho.read_text(
        encoding="utf-8",
        errors="replace",
    ).splitlines()

    inicio = max(
        0,
        (linha or 1) - 81,
    )

    fim = min(
        len(linhas),
        (linha or 1) + 80,
    )

    janela = linhas[inicio:fim]
    linha_base = inicio + 1

    entradas = localizar(
        janela,
        ENTRADAS,
        "SOURCE",
        linha_base,
    )

    sinks = localizar(
        janela,
        SINKS,
        "SINK",
        linha_base,
    )

    validacoes = localizar(
        janela,
        VALIDACOES,
        "VALIDACAO_SANITIZACAO",
        linha_base,
    )

    autorizacoes = localizar(
        janela,
        AUTORIZACOES,
        "AUTORIZACAO",
        linha_base,
    )

    propagacoes = identificar_propagacoes_simples(
        janela,
        linha_base,
    )

    material = " ".join(
        str(valor or "")
        for valor in (
            regra,
            cwe,
            mensagem,
        )
    ).lower()

    path_traversal = any(
        termo in material
        for termo in (
            "cwe-22",
            "path traversal",
            "directory traversal",
        )
    )

    autorizacao = any(
        termo in material
        for termo in (
            "cwe-639",
            "cwe-862",
            "authorization",
            "idor",
            "bola",
        )
    )

    if path_traversal:
        propriedade = (
            "Entrada controlavel nao deve resolver "
            "caminho fora da raiz autorizada."
        )
    elif autorizacao:
        propriedade = (
            "O acesso ao recurso deve respeitar "
            "a politica de autorizacao."
        )
    else:
        propriedade = (
            "A propriedade de seguranca requer "
            "evidencia suficiente."
        )

    encontradas = []
    ausentes = []

    if entradas:
        encontradas.append("source_observado")
    else:
        ausentes.append(
            "source_nao_identificado_na_janela"
        )

    if sinks:
        encontradas.append("sink_observado")
    else:
        ausentes.append(
            "sink_nao_identificado_na_janela"
        )

    if (
        path_traversal
        and not validacoes
    ):
        ausentes.append(
            "controle_de_caminho_nao_identificado"
        )

    if (
        autorizacao
        and not autorizacoes
    ):
        ausentes.append(
            "controle_autorizacao_nao_identificado"
        )

    if entradas and sinks and propagacoes:
        nivel = "PLAUSIVEL"
    elif entradas or sinks:
        nivel = "PARCIAL"
    else:
        nivel = "INCONCLUSIVO"

    precondicoes = []

    if endpoint:
        precondicoes.append(
            f"endpoint_informado:{endpoint}"
        )

    if metodo_http:
        precondicoes.append(
            f"metodo_http:{metodo_http}"
        )

    return ResultadoSCR(
        executado=True,
        arquivo=str(caminho),
        linha_referencia=linha,
        classe_vulnerabilidade=classe,
        entradas_identificadas=entradas,
        propagacoes_identificadas=propagacoes,
        sinks_identificados=sinks,
        controles_identificados=(
            validacoes + autorizacoes
        ),
        validacoes_sanitizacoes=validacoes,
        controles_autorizacao=autorizacoes,
        precondicoes=precondicoes,
        propriedade_seguranca=propriedade,
        evidencias_encontradas=encontradas,
        evidencias_ausentes=ausentes,
        nivel_sustentacao=nivel,
        hipotese_sustentada=(
            nivel == "PLAUSIVEL"
        ),
        observacoes=[
            (
                "SCR conservador; nao confirma "
                "vulnerabilidade isoladamente."
            )
        ],
    )
