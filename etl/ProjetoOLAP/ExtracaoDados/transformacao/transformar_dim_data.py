import pandas as pd


def transformar_dim_data(df):

    df = df.copy()

    # Garante que a coluna data seja do tipo DATE
    df["data"] = pd.to_datetime(
        df["data"]
    ).dt.date

    # Garante que DataKey seja inteiro
    df["data_key"] = pd.to_numeric(
        df["data_key"],
        errors="coerce"
    )

    # Remove datas inválidas
    df = df.dropna(
        subset=["data_key", "data"]
    )

    df["data_key"] = (
        df["data_key"]
        .astype(int)
    )

    # Garante que os campos numéricos sejam inteiros
    colunas_inteiras = [
        "dia",
        "mes",
        "trimestre",
        "ano",
        "dia_semana"
    ]

    for coluna in colunas_inteiras:
        df[coluna] = pd.to_numeric(
            df[coluna],
            errors="coerce"
        )

        df[coluna] = df[coluna].astype(int)

    # Trata valores nulos dos nomes
    df["nome_mes"] = (
        df["nome_mes"]
        .fillna("Não informado")
    )

    df["nome_dia_semana"] = (
        df["nome_dia_semana"]
        .fillna("Não informado")
    )

    # Remove datas duplicadas
    df = df.drop_duplicates(
        subset=["data_key"]
    )

    # Ordena pela data
    df = df.sort_values(
        by="data"
    )

    # Seleciona somente as colunas da dimensão
    df = df[
        [
            "data_key",
            "data",
            "dia",
            "mes",
            "nome_mes",
            "trimestre",
            "ano",
            "dia_semana",
            "nome_dia_semana"
        ]
    ]

    return df