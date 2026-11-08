# Importa pandas para análise de dados
import os

import pandas as pd

# Importa matplotlib para gráficos
import matplotlib.pyplot as plt

# Importa Path para gerenciar arquivos
from pathlib import Path


# Caminho do dataset
CAMINHO_DATASET = Path("dados/dataset_veritassec.csv")

# Pasta externa de saída dos resultados
DIRETORIO_SAIDAS = Path(
    os.getenv(
        "VERITASSEC_SAIDAS_DIR",
        str(Path.home() / "Documentos" / "Projetos" / "VeritasSec-Agent-Saidas"),
    )
)
PASTA_RESULTADOS = DIRETORIO_SAIDAS / "resultados"
PASTA_RESULTADOS.mkdir(parents=True, exist_ok=True)


def carregar_dataset():
    print("📥 Carregando dataset...")
    return pd.read_csv(CAMINHO_DATASET)


def taxa_falso_positivo(df):
    total = len(df)
    falsos = len(df[df["classificacao"] == "falso_positivo"])
    taxa = (falsos / total) * 100

    print(f"📊 Taxa de falso positivo: {taxa:.2f}%")
    return taxa


def distribuicao_classificacao(df):
    contagem = df["classificacao"].value_counts()

    plt.figure()
    contagem.plot(kind="bar")
    plt.title("Distribuição de Classificação")
    plt.xlabel("Classificação")
    plt.ylabel("Quantidade")

    caminho = PASTA_RESULTADOS / "classificacao.png"
    plt.savefig(caminho)
    plt.close()

    print(f"📊 Gráfico salvo: {caminho}")


def distribuicao_severidade(df):
    contagem = df["severidade"].value_counts()

    plt.figure()
    contagem.plot(kind="bar")
    plt.title("Distribuição de Severidade")
    plt.xlabel("Severidade")
    plt.ylabel("Quantidade")

    caminho = PASTA_RESULTADOS / "severidade.png"
    plt.savefig(caminho)
    plt.close()


def distribuicao_risco(df):
    plt.figure()
    df["risco"].plot(kind="hist", bins=10)

    plt.title("Distribuição de Risco")
    plt.xlabel("Pontuação de Risco")
    plt.ylabel("Frequência")

    caminho = PASTA_RESULTADOS / "risco.png"
    plt.savefig(caminho)
    plt.close()


def confianca_media(df):
    media = df["confianca"].mean()
    print(f"📊 Confiança média: {media:.2f}")
    return media


def analise_consenso(df):
    contagem = df["consenso"].value_counts()

    plt.figure()
    contagem.plot(kind="bar")

    plt.title("Consenso entre modelos")
    plt.xlabel("Tipo de consenso")
    plt.ylabel("Quantidade")

    caminho = PASTA_RESULTADOS / "consenso.png"
    plt.savefig(caminho)
    plt.close()


def gerar_resumo(df, taxa_fp, confianca):
    caminho = PASTA_RESULTADOS / "resumo.txt"

    with open(caminho, "w") as f:
        f.write("=== RESULTADO ESTATÍSTICO VERITASSEC ===\n\n")

        f.write(f"Total de amostras: {len(df)}\n")
        f.write(f"Taxa de falso positivo: {taxa_fp:.2f}%\n")
        f.write(f"Confiança média: {confianca:.2f}\n\n")

        f.write("Distribuição de severidade:\n")
        f.write(str(df["severidade"].value_counts()))
        f.write("\n\n")

        f.write("Distribuição de classificação:\n")
        f.write(str(df["classificacao"].value_counts()))
        f.write("\n")

    print(f"📄 Resumo salvo: {caminho}")


def main():
    df = carregar_dataset()

    taxa_fp = taxa_falso_positivo(df)
    distribuicao_classificacao(df)
    distribuicao_severidade(df)
    distribuicao_risco(df)

    confianca = confianca_media(df)
    analise_consenso(df)

    gerar_resumo(df, taxa_fp, confianca)

    print("\n✅ Análise estatística concluída!")


if __name__ == "__main__":
    main()