from __future__ import annotations

import csv
import hashlib
import json

from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _serializar(valor: Any) -> Any:
    if isinstance(valor, dict):
        return {
            str(k): _serializar(v)
            for k, v in valor.items()
        }

    if isinstance(valor, (list, tuple, set)):
        return [
            _serializar(v)
            for v in valor
        ]

    if isinstance(
        valor,
        (str, int, float, bool, type(None)),
    ):
        return valor

    if hasattr(valor, "model_dump"):
        try:
            return _serializar(
                valor.model_dump(
                    mode="json"
                )
            )
        except Exception:
            pass

    if hasattr(valor, "__dict__"):
        return _serializar(
            vars(valor)
        )

    return str(valor)


def _veredito(resultado: dict[str, Any]) -> str:
    candidatos = []

    fund = resultado.get(
        "fundamentacao_tecnica"
    )

    if isinstance(fund, dict):
        candidatos.append(
            fund.get("veredito")
        )

    v = resultado.get("veredito")

    if isinstance(v, dict):
        candidatos.extend([
            v.get("classe"),
            v.get("estado"),
        ])
    else:
        candidatos.append(v)

    candidatos.extend([
        resultado.get("veredito_final"),
        resultado.get("estado_final"),
    ])

    for valor in candidatos:
        s = (
            str(valor or "")
            .strip()
            .lower()
            .replace("_", " ")
            .replace("-", " ")
        )

        if (
            "verdadeiro positivo" in s
            or s in {"vp", "confirmado"}
        ):
            return "VERDADEIRO_POSITIVO"

        if (
            "falso positivo" in s
            or s in {"fp", "refutado"}
        ):
            return "FALSO_POSITIVO"

        if (
            "inconclus" in s
            or "evidencia insuficiente" in s
            or "evidência insuficiente" in s
        ):
            return "INCONCLUSIVO"

    return "INCONCLUSIVO"


# VERITASSEC_XAI_EXPORTACAO_INTEGRADA_V1
# Nao modifica classificacoes nem inventa evidencias.
def _texto_relatorio(valor: Any, limite: int = 18000) -> str:
    if valor is None or valor == "" or valor == {} or valor == []:
        return "NÃO DISPONÍVEL NA EXECUÇÃO"
    if isinstance(valor, (dict, list)):
        texto = json.dumps(_serializar(valor), ensure_ascii=False, indent=2)
    else:
        texto = str(valor)
    return texto[:limite] + ("\n[CONTEÚDO TRUNCADO]" if len(texto)>limite else "")


def _campos_explicacao(resultado: dict[str, Any]) -> list[tuple[str, Any]]:
    vm = resultado.get("veredito_multivariado")
    vm = vm if isinstance(vm, dict) else {}
    xai = resultado.get("explicabilidade_xai")
    fund = resultado.get("fundamentacao_tecnica")
    return [
        ("Classificação registrada", resultado.get("classificacao_final") or vm.get("classificacao_final")),
        ("Justificativa da classificação", resultado.get("justificativa_classificacao") or vm.get("justificativa_classificacao")),
        ("Fundamentação técnica", fund),
        ("Explicabilidade XAI", xai),
        ("Evidências ausentes", resultado.get("evidencias_ausentes_classificacao") or vm.get("evidencias_ausentes")),
        ("Plano de aquisição", resultado.get("plano_aquisicao_evidencia")),
        ("Evidências adquiridas", resultado.get("aquisicao_evidencia")),
        ("Avaliação do Security Oracle", resultado.get("avaliacao_security_oracle_zap")),
        ("Trilha dos agentes", resultado.get("trilha")),
    ]


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            b = f.read(1024 * 1024)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def gerar_exportacao_operacional(
    *,
    resultados: list[dict[str, Any]],
    diretorio: str | Path,
    projeto: str,
    sarif: str,
) -> dict[str, Any]:

    from docx import Document
    from docx.shared import Pt

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    raiz = (
        Path(diretorio)
        .expanduser()
        .resolve()
    )

    raiz.mkdir(
        parents=True,
        exist_ok=True,
    )

    linhas = []

    for indice, item in enumerate(resultados):
        item = _serializar(item)

        achado = item.get(
            "achado",
            {}
        )

        resultado = item.get(
            "resultado",
            {}
        )

        linhas.append({
            "indice": indice,
            "id": (
                achado.get("id")
                or achado.get("fingerprint")
                or ""
            ),
            "regra": (
                achado.get("regra")
                or achado.get("ruleId")
                or ""
            ),
            "arquivo": (
                achado.get("uri_sarif")
                or achado.get("arquivo")
                or ""
            ),
            "linha": (
                achado.get("linha")
                or achado.get("linha_inicio")
                or ""
            ),
            "veredito": _veredito(resultado),
            "resultado": resultado,
        })

    if not linhas:
        raise ValueError(
            "Execucao sem resultados."
        )

    csv_resultados = (
        raiz
        / "resultados.csv"
    )

    with csv_resultados.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "indice",
                "id",
                "regra",
                "arquivo",
                "linha",
                "veredito",
                "justificativa_classificacao",
                "xai_disponivel",
            ],
            delimiter=";",
        )
        w.writeheader()
        for x in linhas:
            resultado = x["resultado"]
            vm = resultado.get("veredito_multivariado")
            vm = vm if isinstance(vm, dict) else {}
            w.writerow({
                **{k: x.get(k, "") for k in ("indice", "id", "regra", "arquivo", "linha", "veredito")},
                "justificativa_classificacao": resultado.get("justificativa_classificacao") or vm.get("justificativa_classificacao") or "",
                "xai_disponivel": isinstance(resultado.get("explicabilidade_xai"), dict) and bool(resultado["explicabilidade_xai"]),
            })

    csv_evid = (
        raiz
        / "evidencias.csv"
    )

    with csv_evid.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as f:
        w = csv.writer(
            f,
            delimiter=";",
        )
        w.writerow([
            "indice",
            "id",
            "resultado_estruturado",
        ])
        for x in linhas:
            w.writerow([
                x["indice"],
                x["id"],
                json.dumps(
                    x["resultado"],
                    ensure_ascii=False,
                    default=str,
                ),
            ])

    dist = Counter(
        x["veredito"]
        for x in linhas
    )

    metricas = (
        raiz
        / "metricas.json"
    )

    metricas.write_text(
        json.dumps(
            {
                "ground_truth_usado": False,
                "distribuicao_vereditos": dict(dist),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    fig = plt.figure(
        figsize=(8, 5)
    )
    ax = fig.add_subplot(111)

    labels = list(dist.keys())
    valores = [
        dist[k]
        for k in labels
    ]

    ax.bar(
        range(len(labels)),
        valores,
    )
    ax.set_xticks(
        range(len(labels))
    )
    ax.set_xticklabels(
        labels,
        rotation=25,
        ha="right",
    )
    ax.set_ylabel("Quantidade")
    ax.set_title(
        "Distribuição dos vereditos"
    )
    fig.tight_layout()

    graficos = []

    for ext in ("png", "svg"):
        p = raiz / f"grafico-vereditos.{ext}"
        fig.savefig(
            p,
            dpi=160,
        )
        graficos.append(str(p))

    plt.close(fig)

    doc = Document()

    doc.styles[
        "Normal"
    ].font.name = "Arial"

    doc.styles[
        "Normal"
    ].font.size = Pt(10)

    p = doc.add_paragraph()
    r = p.add_run(
        "VeritasSec — Relatório da Execução"
    )
    r.bold = True
    r.font.size = Pt(16)

    for chave, valor in (
        (
            "Data/hora UTC",
            datetime.now(
                timezone.utc
            ).isoformat(),
        ),
        ("Projeto", projeto),
        ("SARIF", sarif),
        ("Total", len(linhas)),
    ):
        p = doc.add_paragraph()
        p.add_run(
            chave + ": "
        ).bold = True
        p.add_run(
            str(valor)
        )

    for x in linhas:
        doc.add_heading(
            f"Achado {x['indice'] + 1}",
            level=2,
        )
        for chave in (
            "id",
            "regra",
            "arquivo",
            "linha",
            "veredito",
        ):
            p = doc.add_paragraph()
            p.add_run(
                chave + ": "
            ).bold = True
            p.add_run(
                str(x[chave])
            )
        for titulo, valor in _campos_explicacao(x["resultado"]):
            doc.add_heading(titulo, level=3)
            doc.add_paragraph(_texto_relatorio(valor))

    docx = (
        raiz
        / "relatorio-veritassec.docx"
    )

    doc.save(docx)
    Document(docx)

    # VERITASSEC_RELATORIO_XAI_MARKDOWN_V2
    markdown = raiz / "relatorio-veritassec.md"
    partes_md = [
        "# VeritasSec — Relatório da Execução",
        "",
        f"Total de achados: {len(linhas)}",
        "",
        "As evidências abaixo são registros do pipeline, não confirmação automática de explorabilidade.",
        "",
    ]
    for achado_exportado in linhas:
        partes_md.append(f"## Achado {achado_exportado['indice'] + 1}")
        for chave in ("id", "regra", "arquivo", "linha", "veredito"):
            partes_md.append(f"**{chave}:** {_texto_relatorio(achado_exportado[chave])}")
        for titulo, valor in _campos_explicacao(achado_exportado["resultado"]):
            partes_md.extend([
                "", f"### {titulo}", "",
                "```json" if isinstance(valor, (dict, list)) else "```text",
                _texto_relatorio(valor), "```", "",
            ])
        partes_md.append("---")
    markdown.write_text("\n".join(partes_md) + "\n", encoding="utf-8")

    manifesto = {
        "total": len(linhas),
        "ground_truth_usado": False,
        "csv_resultados": str(csv_resultados),
        "csv_evidencias": str(csv_evid),
        "metricas": str(metricas),
        "graficos": graficos,
        "docx": str(docx),
        "markdown": str(markdown),
    }

    (
        raiz
        / "manifesto.json"
    ).write_text(
        json.dumps(
            manifesto,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    arquivos = [
        p
        for p in raiz.rglob("*")
        if (
            p.is_file()
            and p.name
            != "SHA256SUMS.txt"
        )
    ]

    with (
        raiz
        / "SHA256SUMS.txt"
    ).open(
        "w",
        encoding="utf-8",
    ) as f:
        for p in sorted(arquivos):
            f.write(
                _sha256(p)
                + "  "
                + str(
                    p.relative_to(raiz)
                )
                + "\n"
            )

    return manifesto
