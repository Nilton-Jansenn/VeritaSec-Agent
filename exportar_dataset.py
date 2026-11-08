import psycopg2
import pandas as pd
from aplicacao.nucleo.configuracoes import configuracoes


def exportar_dataset():
    conn = psycopg2.connect(configuracoes.URI_POSTGRES)

    query = "SELECT * FROM dataset_analise"

    df = pd.read_sql(query, conn)

    df.to_csv("dataset_veritassec.csv", index=False)

    print("Dataset exportado com sucesso!")


if __name__ == "__main__":
    exportar_dataset()