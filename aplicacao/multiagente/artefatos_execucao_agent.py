from __future__ import annotations

import csv
import hashlib
import json
import re

from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt


def _nome_projeto(
    projeto_path: str,
) -> str:

    nome = Path(
        projeto_path
    ).resolve().name

    partes = [
        parte
        for parte in re.split(
            r"[^A-Za-z0-9]+",
            nome,
        )
        if parte
    ]

    if not partes:
        return "Sistema"

    return "_".join(
        p[:1].upper()
        + p[1:]
        for p in partes
    )


def _hash(
    caminho: Path,
) -> str:

    h = hashlib.sha256()

    with caminho.open(
        "rb"
    ) as f:

        for bloco in iter(
            lambda: f.read(
                1024 * 1024
            ),
            b"",
        ):
            h.update(bloco)

    return h.hexdigest()


def _resultado(
    item: dict[str, Any],
) -> dict[str, Any]:

    valor = item.get(
        "resultado"
    )

    return (
        valor
        if isinstance(
            valor,
            dict,
        )
        else {}
    )


def _achado(
    item: dict[str, Any],
) -> dict[str, Any]:

    valor = item.get(
        "achado"
    )

    return (
        valor
        if isinstance(
            valor,
            dict,
        )
        else {}
    )



def _lista_texto(
    valor,
) -> list[str]:

    if isinstance(
        valor,
        (list, tuple, set),
    ):

        return [
            str(x)
            for x in valor
            if str(x).strip()
        ]

    return []


def _classificar_veredito_base_integral(
    resultado: dict[str, Any],
) -> tuple[
    str,
    str,
    list[str],
]:

    """
    Produz o veredito final para apresentação.

    PLAUSIVEL/PARCIAL são estados intermediários do SCR
    e nunca são tratados como classificação final.
    """

    estado = str(
        resultado.get(
            "estado_final",
            "",
        )
        or ""
    ).strip().upper()

    motivo = str(
        resultado.get(
            "motivo_termino",
            "",
        )
        or ""
    ).strip().upper()

    evidencia_dinamica = bool(
        resultado.get(
            "evidencia_dinamica",
            False,
        )
    )

    evidencia_oraculo = bool(
        resultado.get(
            "evidencia_oraculo",
            False,
        )
    )

    hipotese = (
        resultado.get(
            "hipotese"
        )
        or {}
    )

    scr = (
        hipotese.get(
            "scr"
        )
        or resultado.get(
            "scr"
        )
        or {}
    )

    lacunas = _lista_texto(
        resultado.get(
            "lacunas"
        )
    )

    ausentes = _lista_texto(
        scr.get(
            "evidencias_ausentes"
        )
    )

    evidencias_ausentes = []

    for valor in (
        ausentes
        + lacunas
    ):
        if (
            valor
            not in evidencias_ausentes
        ):
            evidencias_ausentes.append(
                valor
            )

    # --------------------------------------------------------
    # VERDADEIRO POSITIVO
    #
    # Só existe quando a cadeia científica de confirmação
    # possui reprodução dinâmica + Oracle.
    # --------------------------------------------------------

    if (
        estado
        in {
            "REPRODUZIDO_DINAMICAMENTE",
            "IMPACTO_CONFIRMADO",
            "EXPLORABILIDADE_CONFIRMADA",
        }
        and evidencia_dinamica
        and evidencia_oraculo
    ):

        justificativa = (
            "A vulnerabilidade foi classificada como "
            "VERDADEIRO_POSITIVO porque houve reprodução "
            "dinâmica observável e confirmação pelo Security "
            "Oracle. A decisão não depende apenas do SAST, "
            "do SCR ou da LLM."
        )

        return (
            "VERDADEIRO_POSITIVO",
            justificativa,
            evidencias_ausentes,
        )

    # --------------------------------------------------------
    # FALSO POSITIVO
    #
    # Exige refutação suficiente, não simplesmente ausência
    # de reprodução.
    # --------------------------------------------------------

    if (
        motivo
        == "EVIDENCIA_SUFICIENTE_REFUTADA"
    ):

        justificativa = (
            "O achado foi classificado como FALSO_POSITIVO "
            "porque a investigação reuniu evidência suficiente "
            "para refutar a hipótese de vulnerabilidade."
        )

        return (
            "FALSO_POSITIVO",
            justificativa,
            evidencias_ausentes,
        )

    # --------------------------------------------------------
    # INCONCLUSIVO
    # --------------------------------------------------------

    razoes = []

    if not evidencia_dinamica:
        razoes.append(
            "não houve evidência dinâmica observável"
        )

    if not evidencia_oraculo:
        razoes.append(
            "não houve confirmação pelo Security Oracle"
        )

    if (
        "source_nao_identificado_na_janela"
        in evidencias_ausentes
    ):
        razoes.append(
            "o SCR não identificou uma origem de dados "
            "controlável suficiente"
        )

    if (
        "sink_nao_identificado_na_janela"
        in evidencias_ausentes
    ):
        razoes.append(
            "o SCR não identificou um sink relevante "
            "suficiente"
        )

    if (
        "execucao_dinamica"
        in evidencias_ausentes
        and not evidencia_dinamica
    ):
        razoes.append(
            "a lacuna de execução dinâmica permaneceu aberta"
        )

    if (
        "oraculo"
        in evidencias_ausentes
        and not evidencia_oraculo
    ):
        razoes.append(
            "a lacuna de validação por Oracle permaneceu aberta"
        )

    if not razoes:

        razoes.append(
            "as evidências disponíveis não foram suficientes "
            "para confirmar nem refutar a hipótese"
        )

    justificativa = (
        "Classificação INCONCLUSIVO: "
        + "; ".join(
            razoes
        )
        + ". "
        + (
            "O estado intermediário do SCR não é tratado "
            "como veredito final."
        )
    )

    return (
        "INCONCLUSIVO",
        justificativa,
        evidencias_ausentes,
    )


def _linhas(
    itens: list[dict[str, Any]],
) -> list[dict[str, Any]]:

    saida = []

    for item in itens:

        achado = _achado(
            item
        )

        resultado = _resultado(
            item
        )

        raciocinio = (
            resultado.get(
                "raciocinio"
            )
            or {}
        )

        hipotese = (
            resultado.get(
                "hipotese"
            )
            or {}
        )

        scr = (
            resultado.get(
                "scr"
            )
            or {}
        )

        ciclo = (
            resultado.get(
                "ciclo_adaptativo_operacional"
            )
            or {}
        )


        (
            classificacao_final,
            justificativa_classificacao,
            evidencias_ausentes,
        ) = _classificar_veredito(
            resultado
        )

        saida.append({
            "indice":
                item.get(
                    "indice"
                ),

            "achado_id":
                achado.get(
                    "id"
                ),

            "regra":
                achado.get(
                    "regra"
                ),

            "arquivo":
                achado.get(
                    "arquivo"
                ),

            "linha":
                achado.get(
                    "linha"
                ),

            "estado_final":
                resultado.get(
                    "estado_final",
                    "NAO_INFORMADO",
                ),


            "classificacao_final":
                classificacao_final,

            "justificativa_classificacao":
                justificativa_classificacao,

            "evidencias_ausentes":
                " | ".join(
                    evidencias_ausentes
                ),

            "motivo_termino":
                resultado.get(
                    "motivo_termino",
                    "NAO_INFORMADO",
                ),

            "sustentacao_scr":
                hipotese.get(
                    "sustentacao_scr"
                )
                or scr.get(
                    "nivel_sustentacao"
                )
                or "NAO_INFORMADO",

            "evidencia_dinamica":
                bool(
                    resultado.get(
                        "evidencia_dinamica",
                        False,
                    )
                ),

            "evidencia_oraculo":
                bool(
                    resultado.get(
                        "evidencia_oraculo",
                        False,
                    )
                ),

            "hipotese_confirmada":
                bool(
                    hipotese.get(
                        "confirmada",
                        False,
                    )
                ),

            "chamadas_llm_reais":
                int(
                    raciocinio.get(
                        "chamadas_llm_reais",
                        0,
                    )
                    or 0
                ),

            "fallbacks_deterministicos":
                int(
                    raciocinio.get(
                        "fallbacks_deterministicos",
                        0,
                    )
                    or 0
                ),

            "modo_raciocinio":
                raciocinio.get(
                    "modo",
                    "NAO_INFORMADO",
                ),

            "ciclo_adaptativo_executado":
                bool(
                    ciclo.get(
                        "executado",
                        False,
                    )
                ),

            "motivo_ciclo_nao_execucao":
                ciclo.get(
                    "motivo_nao_execucao"
                ),
        })

    return saida


def _grafico_contagem(
    *,
    contador: Counter,
    titulo: str,
    ylabel: str,
    caminho: Path,
) -> None:

    dados = [
        (
            str(chave),
            valor,
        )
        for chave, valor
        in contador.items()
    ]

    dados.sort(
        key=lambda x: (
            -x[1],
            x[0],
        )
    )

    nomes = [
        x[0]
        for x in dados
    ]

    valores = [
        x[1]
        for x in dados
    ]

    fig, ax = plt.subplots(
        figsize=(
            11,
            max(
                5,
                len(nomes)
                * 0.55,
            ),
        )
    )

    pos = range(
        len(nomes)
    )

    ax.barh(
        pos,
        valores,
    )

    ax.set_yticks(
        list(pos)
    )

    ax.set_yticklabels(
        nomes
    )

    ax.invert_yaxis()

    ax.set_title(
        titulo
    )

    ax.set_xlabel(
        ylabel
    )

    ax.grid(
        axis="x",
        alpha=0.25,
    )

    fig.tight_layout()

    fig.savefig(
        caminho,
        dpi=160,
        bbox_inches="tight",
    )

    plt.close(fig)


def _grafico_llm(
    linhas: list[dict[str, Any]],
    caminho: Path,
) -> None:

    indices = [
        str(
            int(
                linha[
                    "indice"
                ]
            )
            + 1
        )
        if isinstance(
            linha.get(
                "indice"
            ),
            int,
        )
        else str(
            pos + 1
        )
        for pos, linha
        in enumerate(
            linhas
        )
    ]

    chamadas = [
        linha[
            "chamadas_llm_reais"
        ]
        for linha in linhas
    ]

    fallbacks = [
        linha[
            "fallbacks_deterministicos"
        ]
        for linha in linhas
    ]

    x = list(
        range(
            len(indices)
        )
    )

    largura = 0.4

    fig, ax = plt.subplots(
        figsize=(14, 6)
    )

    ax.bar(
        [
            i - largura / 2
            for i in x
        ],
        chamadas,
        width=largura,
        label="Chamadas LLM reais",
    )

    ax.bar(
        [
            i + largura / 2
            for i in x
        ],
        fallbacks,
        width=largura,
        label="Fallbacks determinísticos",
    )

    ax.set_title(
        "Uso de LLM e fallbacks por achado"
    )

    ax.set_xlabel(
        "Achado"
    )

    ax.set_ylabel(
        "Quantidade"
    )

    ax.set_xticks(
        x
    )

    ax.set_xticklabels(
        indices,
        rotation=90,
    )

    ax.legend()

    ax.grid(
        axis="y",
        alpha=0.25,
    )

    fig.tight_layout()

    fig.savefig(
        caminho,
        dpi=160,
        bbox_inches="tight",
    )

    plt.close(fig)


def gerar_artefatos_analiticos(
    *,
    pacote: dict[str, Any],
    itens: list[dict[str, Any]],
    projeto_path: str,
    sarif_path: str,
    saidas_root: Path,
    subdiretorio_saida: str | None = None,
) -> dict[str, Any]:

    nome = _nome_projeto(
        projeto_path
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    base = (
        Path(
            saidas_root
        )
        / "resultados"
    )

    subdir = str(
        subdiretorio_saida
        or ""
    ).strip().strip("/")

    if (
        subdir
        and subdir.lower()
        != "interface"
    ):
        base = (
            base
            / subdir
        )

    diretorio = (
        base
        / f"{nome}_{timestamp}"
    )

    contador = 1
    original = diretorio

    while diretorio.exists():

        diretorio = Path(
            str(original)
            + f"_{contador:02d}"
        )

        contador += 1

    diretorio.mkdir(
        parents=True,
        exist_ok=False,
    )

    linhas = _linhas(
        itens
    )

    prefixo = nome

    caminho_json = (
        diretorio
        / f"{prefixo}_analise.json"
    )

    caminho_csv = (
        diretorio
        / f"{prefixo}_analise.csv"
    )

    caminho_md = (
        diretorio
        / f"{prefixo}_analise.md"
    )

    caminho_prom = (
        diretorio
        / f"{prefixo}_metricas.prom"
    )

    payload_json = {
        "projeto":
            str(
                Path(
                    projeto_path
                ).resolve()
            ),

        "sarif":
            str(
                Path(
                    sarif_path
                ).resolve()
            ),

        "total_achados_sarif":
            pacote.get(
                "total_achados_sarif"
            ),

        "total_selecionado":
            pacote.get(
                "total_selecionado"
            ),

        "total_processado":
            pacote.get(
                "total_processado"
            ),

        "achados":
            linhas,
    }

    caminho_json.write_text(
        json.dumps(
            payload_json,
            ensure_ascii=False,
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )

    campos = list(
        linhas[0].keys()
    ) if linhas else []

    with caminho_csv.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=campos,
        )

        if campos:
            writer.writeheader()
            writer.writerows(
                linhas
            )

    estados = Counter(
        x["estado_final"]
        for x in linhas
    )


    classificacoes = Counter(
        x["classificacao_final"]
        for x in linhas
    )

    sustentacao = Counter(
        x["sustentacao_scr"]
        for x in linhas
    )

    motivos = Counter(
        x["motivo_termino"]
        for x in linhas
    )

    modos = Counter(
        x["modo_raciocinio"]
        for x in linhas
    )

    total = len(
        linhas
    )

    total_llm = sum(
        x[
            "chamadas_llm_reais"
        ]
        for x in linhas
    )

    total_fallback = sum(
        x[
            "fallbacks_deterministicos"
        ]
        for x in linhas
    )

    dinamicos = sum(
        1
        for x in linhas
        if x[
            "evidencia_dinamica"
        ]
    )

    oraculos = sum(
        1
        for x in linhas
        if x[
            "evidencia_oraculo"
        ]
    )

    confirmados = sum(
        1
        for x in linhas
        if x[
            "hipotese_confirmada"
        ]
    )

    md = [
        "# Resultado da análise VeritasSec-Agent",
        "",
        f"- Projeto: {nome}",
        f"- Achados SARIF: {pacote.get('total_achados_sarif')}",
        f"- Achados processados: {pacote.get('total_processado')}",
        f"- Chamadas LLM reais: {total_llm}",
        f"- Fallbacks determinísticos: {total_fallback}",
        f"- Evidência dinâmica: {dinamicos}",
        f"- Evidência de oráculo: {oraculos}",
        f"- Hipóteses confirmadas: {confirmados}",
        "",
        "## Classificação final",
        "",
    ]

    for chave, valor in classificacoes.items():
        md.append(
            f"- {chave}: {valor}"
        )

    md.extend([
        "",
        "## Estados científicos internos",
        "",
    ])

    for chave, valor in estados.items():
        md.append(
            f"- {chave}: {valor}"
        )

    md.extend([
        "",
        "## Sustentação SCR",
        "",
    ])

    for chave, valor in sustentacao.items():
        md.append(
            f"- {chave}: {valor}"
        )

    md.extend([
        "",
        "## Motivos de término",
        "",
    ])

    for chave, valor in motivos.items():
        md.append(
            f"- {chave}: {valor}"
        )

    md.extend([
        "",
        "## Veredito por achado",
        "",
    ])

    for linha in linhas:

        md.extend([
            (
                "### Achado "
                + str(
                    (
                        linha.get("indice")
                        if linha.get("indice") is not None
                        else "?"
                    )
                )
            ),
            "",
            (
                "- Classificação final: "
                + str(
                    linha[
                        "classificacao_final"
                    ]
                )
            ),
            (
                "- Regra: "
                + str(
                    linha.get(
                        "regra"
                    )
                )
            ),
            (
                "- Arquivo: "
                + str(
                    linha.get(
                        "arquivo"
                    )
                )
            ),
            (
                "- Linha: "
                + str(
                    linha.get(
                        "linha"
                    )
                )
            ),
            (
                "- Justificativa: "
                + str(
                    linha[
                        "justificativa_classificacao"
                    ]
                )
            ),
            (
                "- Evidências ausentes: "
                + (
                    str(
                        linha[
                            "evidencias_ausentes"
                        ]
                    )
                    or "nenhuma registrada"
                )
            ),
            "",
        ])

    caminho_md.write_text(
        "\n".join(md)
        + "\n",
        encoding="utf-8",
    )

    prom = [
        "# HELP veritassec_achados_total Total de achados processados.",
        "# TYPE veritassec_achados_total gauge",
        f"veritassec_achados_total {total}",
        "",
        "# HELP veritassec_llm_chamadas_total Chamadas reais aos modelos.",
        "# TYPE veritassec_llm_chamadas_total gauge",
        f"veritassec_llm_chamadas_total {total_llm}",
        "",
        "# HELP veritassec_fallbacks_total Fallbacks determinísticos.",
        "# TYPE veritassec_fallbacks_total gauge",
        f"veritassec_fallbacks_total {total_fallback}",
        "",
        "# HELP veritassec_evidencia_dinamica_total Achados com evidência dinâmica.",
        "# TYPE veritassec_evidencia_dinamica_total gauge",
        f"veritassec_evidencia_dinamica_total {dinamicos}",
        "",
        "# HELP veritassec_oraculo_total Achados com evidência de oráculo.",
        "# TYPE veritassec_oraculo_total gauge",
        f"veritassec_oraculo_total {oraculos}",
        "",
        "# HELP veritassec_hipoteses_confirmadas_total Hipóteses confirmadas.",
        "# TYPE veritassec_hipoteses_confirmadas_total gauge",
        f"veritassec_hipoteses_confirmadas_total {confirmados}",
    ]

    for estado, qtd in sorted(
        estados.items()
    ):
        prom.extend([
            "",
            (
                'veritassec_estado_final_total'
                f'{{estado="{estado}"}} {qtd}'
            ),
        ])

    caminho_prom.write_text(
        "\n".join(prom)
        + "\n",
        encoding="utf-8",
    )

    grafico_estados = (
        diretorio
        / f"{prefixo}_grafico_classificacao_final.png"
    )

    grafico_scr = (
        diretorio
        / f"{prefixo}_grafico_sustentacao_scr.png"
    )

    grafico_motivos = (
        diretorio
        / f"{prefixo}_grafico_motivos_termino.png"
    )

    grafico_modos = (
        diretorio
        / f"{prefixo}_grafico_raciocinio_llm.png"
    )

    grafico_llm = (
        diretorio
        / f"{prefixo}_grafico_chamadas_llm.png"
    )

    _grafico_contagem(
        contador=classificacoes,
        titulo=(
            "Classificação final dos achados"
        ),
        ylabel="Quantidade de achados",
        caminho=grafico_estados,
    )

    _grafico_contagem(
        contador=sustentacao,
        titulo=(
            "Sustentação do Security Code Review"
        ),
        ylabel="Quantidade de achados",
        caminho=grafico_scr,
    )

    _grafico_contagem(
        contador=motivos,
        titulo=(
            "Motivos de término da investigação"
        ),
        ylabel="Quantidade de achados",
        caminho=grafico_motivos,
    )

    _grafico_contagem(
        contador=modos,
        titulo=(
            "Modo de raciocínio por achado"
        ),
        ylabel="Quantidade de achados",
        caminho=grafico_modos,
    )

    _grafico_llm(
        linhas,
        grafico_llm,
    )

    arquivos = [
        caminho_json,
        caminho_csv,
        caminho_md,
        caminho_prom,
        grafico_estados,
        grafico_scr,
        grafico_motivos,
        grafico_modos,
        grafico_llm,
    ]

    sha = (
        diretorio
        / "SHA256SUMS.txt"
    )

    sha.write_text(
        "\n".join(
            (
                f"{_hash(arquivo)}  "
                f"{arquivo.name}"
            )
            for arquivo in arquivos
        )
        + "\n",
        encoding="utf-8",
    )

    return {
        "diretorio":
            str(
                diretorio
            ),

        "arquivos": [
            str(
                arquivo
            )
            for arquivo in arquivos
        ],

        "sha256sums":
            str(
                sha
            ),

        "metricas": {
            "total_achados":
                total,

            "chamadas_llm_reais":
                total_llm,

            "fallbacks_deterministicos":
                total_fallback,

            "evidencia_dinamica":
                dinamicos,

            "evidencia_oraculo":
                oraculos,

            "hipoteses_confirmadas":
                confirmados,
        },
    }



def _classificar_veredito(
    resultado,
):
    vm = (
        resultado.get(
            "veredito_multivariado",
            {},
        )
        or {}
    )

    classe = vm.get(
        "classificacao_final"
    )

    if classe in {
        "VERDADEIRO_POSITIVO",
        "FALSO_POSITIVO",
        "INCONCLUSIVO",
    }:

        return (
            classe,

            str(
                vm.get(
                    "justificativa_classificacao",
                    "",
                )
            ),

            list(
                vm.get(
                    "evidencias_ausentes",
                    [],
                )
                or []
            ),
        )

    return (
        _classificar_veredito_base_integral(
            resultado
        )
    )
