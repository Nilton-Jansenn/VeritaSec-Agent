"""
Módulo: exportador_complementares.py

Responsabilidade:
-----------------
Exportar achados complementares classificados pela LLM em:

- JSON;
- CSV;
- Markdown;
- gráficos PNG.

Regra metodológica:
-------------------
Achados complementares NÃO são achados SAST.

Eles representam sinais contextuais, exposições, red flags ou más práticas
identificadas por varredura complementar e avaliadas pela LLM em pipeline
inferencial próprio.
"""

from pathlib import Path
from collections import Counter
import csv
import json
import logging
from typing import Any

import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)


def _valor_seguro(valor: Any) -> str:
    """
    Converte valores para representação segura em CSV/Markdown.
    """

    if valor is None:
        return ""

    if isinstance(valor, (dict, list)):
        return json.dumps(
            valor,
            ensure_ascii=False,
            default=str,
        )

    texto = str(valor)

    return texto.replace("\n", " ").replace("\r", " ").strip()


def _contar_por_campo(
    achados_complementares: list[dict],
    campo: str,
    valor_padrao: str,
) -> Counter:
    """
    Conta ocorrências por campo.
    """

    contador = Counter()

    for achado in achados_complementares:
        valor = achado.get(campo) or valor_padrao
        contador[str(valor)] += 1

    return contador


def _gerar_grafico_barras(
    contador: Counter,
    titulo: str,
    eixo_x: str,
    eixo_y: str,
    caminho_saida: Path,
) -> None:
    """
    Gera gráfico de barras simples com rótulo de quantidade.

    Observação:
    -----------
    Não define cor manualmente para manter compatibilidade visual padrão
    do matplotlib.
    """

    if not contador:
        return

    itens_ordenados = sorted(
        contador.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    labels = [item[0] for item in itens_ordenados]
    valores = [item[1] for item in itens_ordenados]

    largura = max(8, len(labels) * 1.6)

    plt.figure(figsize=(largura, 5))
    barras = plt.bar(labels, valores)

    plt.title(titulo)
    plt.xlabel(eixo_x)
    plt.ylabel(eixo_y)
    plt.xticks(rotation=30, ha="right")

    for barra in barras:
        altura = barra.get_height()

        plt.text(
            barra.get_x() + barra.get_width() / 2,
            altura,
            str(int(altura)),
            ha="center",
            va="bottom",
        )

    plt.tight_layout()
    plt.savefig(caminho_saida, dpi=150)
    plt.close()


def exportar_complementares_classificados(
    achados_complementares: list[dict],
    diretorio_saida: Path,
) -> None:
    """
    Exporta complementares classificados pela LLM.

    Arquivos gerados:
    -----------------
    - complementares_classificados.json
    - complementares_classificados.csv
    - complementares_classificados.md
    - grafico_complementares_por_classificacao.png
    - grafico_complementares_por_risco.png
    - grafico_complementares_por_tipo_semantico.png
    """

    if not achados_complementares:
        logger.info("Nenhum complementar classificado para exportar.")
        return

    diretorio_saida.mkdir(
        parents=True,
        exist_ok=True,
    )

    caminho_json = diretorio_saida / "complementares_classificados.json"
    caminho_csv = diretorio_saida / "complementares_classificados.csv"
    caminho_md = diretorio_saida / "complementares_classificados.md"

    caminho_png_classificacao = (
        diretorio_saida / "grafico_complementares_por_classificacao.png"
    )

    caminho_png_risco = diretorio_saida / "grafico_complementares_por_risco.png"

    caminho_png_tipo = diretorio_saida / "grafico_complementares_por_tipo_semantico.png"

    with open(caminho_json, "w", encoding="utf-8") as arquivo_json:
        json.dump(
            achados_complementares,
            arquivo_json,
            ensure_ascii=False,
            indent=2,
            default=str,
        )

    campos_csv = [
        "id_execucao",
        "identificador_achado",
        "origem_achado",
        "tipo",
        "tipo_semantico",
        "arquivo",
        "linha",
        "descricao",
        "classificacao_llm",
        "risco_llm",
        "confianca_llm",
        "classificado_por_llm",
        "observacao_metodologica",
    ]

    with open(caminho_csv, "w", encoding="utf-8", newline="") as arquivo_csv:
        escritor = csv.DictWriter(
            arquivo_csv,
            fieldnames=campos_csv,
            extrasaction="ignore",
        )

        escritor.writeheader()

        for complementar in achados_complementares:
            escritor.writerow(
                {campo: _valor_seguro(complementar.get(campo)) for campo in campos_csv}
            )

    contador_classificacao = _contar_por_campo(
        achados_complementares,
        "classificacao_llm",
        "nao_classificado",
    )

    contador_risco = _contar_por_campo(
        achados_complementares,
        "risco_llm",
        "risco_nao_inferido",
    )

    contador_tipo = _contar_por_campo(
        achados_complementares,
        "tipo_semantico",
        "evidencia_contextual",
    )

    total_classificados = sum(
        1 for achado in achados_complementares if achado.get("classificacao_llm")
    )

    total_nao_classificados = len(achados_complementares) - total_classificados

    _gerar_grafico_barras(
        contador=contador_classificacao,
        titulo="Complementares por classificação da LLM",
        eixo_x="Classificação",
        eixo_y="Quantidade",
        caminho_saida=caminho_png_classificacao,
    )

    _gerar_grafico_barras(
        contador=contador_risco,
        titulo="Complementares por risco inferido pela LLM",
        eixo_x="Risco",
        eixo_y="Quantidade",
        caminho_saida=caminho_png_risco,
    )

    _gerar_grafico_barras(
        contador=contador_tipo,
        titulo="Complementares por tipo semântico",
        eixo_x="Tipo semântico",
        eixo_y="Quantidade",
        caminho_saida=caminho_png_tipo,
    )

    with open(caminho_md, "w", encoding="utf-8") as arquivo_md:
        arquivo_md.write("# Achados complementares classificados pela LLM\n\n")

        arquivo_md.write("## Resumo metodológico\n\n")
        arquivo_md.write(
            "Os achados complementares não são achados SAST. "
            "Eles representam sinais contextuais, exposições, red flags "
            "ou más práticas identificadas por varredura complementar do projeto "
            "e posteriormente avaliadas pela LLM em pipeline inferencial próprio.\n\n"
        )

        arquivo_md.write(
            "Esses itens não devem ser interpretados automaticamente como "
            "vulnerabilidades confirmadas. A classificação representa inferência "
            "contextual da LLM e deve ser analisada separadamente dos achados "
            "originados do SARIF/SAST.\n\n"
        )

        arquivo_md.write("## Totais\n\n")
        arquivo_md.write(f"- Total de complementares: {len(achados_complementares)}\n")
        arquivo_md.write(f"- Complementares classificados: {total_classificados}\n")
        arquivo_md.write(
            f"- Complementares não classificados: {total_nao_classificados}\n\n"
        )

        arquivo_md.write("## Distribuição por classificação\n\n")
        for classe, total in sorted(
            contador_classificacao.items(),
            key=lambda item: item[1],
            reverse=True,
        ):
            arquivo_md.write(f"- {classe}: {total}\n")

        arquivo_md.write("\n## Distribuição por risco\n\n")
        for risco, total in sorted(
            contador_risco.items(),
            key=lambda item: item[1],
            reverse=True,
        ):
            arquivo_md.write(f"- {risco}: {total}\n")

        arquivo_md.write("\n## Distribuição por tipo semântico\n\n")
        for tipo, total in sorted(
            contador_tipo.items(),
            key=lambda item: item[1],
            reverse=True,
        ):
            arquivo_md.write(f"- {tipo}: {total}\n")

        arquivo_md.write("\n## Gráficos gerados\n\n")
        arquivo_md.write("- grafico_complementares_por_classificacao.png\n")
        arquivo_md.write("- grafico_complementares_por_risco.png\n")
        arquivo_md.write("- grafico_complementares_por_tipo_semantico.png\n\n")

        arquivo_md.write("## Tabela resumida\n\n")
        arquivo_md.write(
            "| Arquivo | Linha | Tipo semântico | Classificação LLM | Risco LLM | Confiança |\n"
        )
        arquivo_md.write("|---|---:|---|---|---|---:|\n")

        for achado in achados_complementares:
            arquivo_md.write(
                "| "
                f"{_valor_seguro(achado.get('arquivo'))} | "
                f"{_valor_seguro(achado.get('linha'))} | "
                f"{_valor_seguro(achado.get('tipo_semantico'))} | "
                f"{_valor_seguro(achado.get('classificacao_llm'))} | "
                f"{_valor_seguro(achado.get('risco_llm'))} | "
                f"{_valor_seguro(achado.get('confianca_llm'))} "
                "|\n"
            )

    logger.info(
        (
            "Complementares classificados exportados. "
            "json=%s csv=%s md=%s graficos=[%s, %s, %s] total=%s"
        ),
        caminho_json,
        caminho_csv,
        caminho_md,
        caminho_png_classificacao,
        caminho_png_risco,
        caminho_png_tipo,
        len(achados_complementares),
    )
