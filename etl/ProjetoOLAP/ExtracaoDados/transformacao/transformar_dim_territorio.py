import pandas as pd


def transformar_dim_territorio(df):

    df = df.copy()

    # Padroniza os nomes das colunas
    df = df.rename(columns={
        "TerritoryID": "territory_id",
        "NomeTerritorio": "nome_territorio",
        "Pais": "pais",
        "Grupo": "grupo"
    })

    # Trata valores nulos
    df["nome_territorio"] = (
        df["nome_territorio"]
        .fillna("Não informado")
    )

    df["pais"] = (
        df["pais"]
        .fillna("Não informado")
    )

    df["grupo"] = (
        df["grupo"]
        .fillna("Não informado")
    )

    # Garante que TerritoryID seja inteiro
    df["territory_id"] = pd.to_numeric(
        df["territory_id"],
        errors="coerce"
    )

    # Remove registros sem TerritoryID
    df = df.dropna(
        subset=["territory_id"]
    )

    df["territory_id"] = (
        df["territory_id"]
        .astype(int)
    )

    # Remove possíveis duplicidades
    df = df.drop_duplicates(
        subset=["territory_id"]
    )

    # Seleciona somente as colunas da dimensão
    df = df[
        [
            "territory_id",
            "nome_territorio",
            "pais",
            "grupo"
        ]
    ]

    return df