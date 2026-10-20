import pandas as pd


def transformar_dim_produto(df):

    df = df.copy()

    df = df.rename(columns={
        "ProductID": "product_id",
        "NomeProduto": "nome_produto",
        "ProductNumber": "product_number",
        "Color": "cor",
        "Size": "tamanho",
        "NomeSubcategoria": "nome_subcategoria",
        "NomeCategoria": "nome_categoria",
        "ListPrice": "preco_lista",
        "ModifiedDate": "data_alteracao_origem"
    })

    df["cor"] = df["cor"].fillna("Não informado")

    df["tamanho"] = df["tamanho"].fillna("Não informado")

    df["nome_subcategoria"] = df["nome_subcategoria"].fillna(
        "Não informado"
    )

    df["nome_categoria"] = df["nome_categoria"].fillna(
        "Não informado"
    )

    df["preco_lista"] = pd.to_numeric(
        df["preco_lista"],
        errors="coerce"
    )

    df["data_alteracao_origem"] = pd.to_datetime(
        df["data_alteracao_origem"],
        errors="coerce"
    )

    df = df.dropna(subset=["product_id"])

    df["product_id"] = df["product_id"].astype(int)

    df = df.drop_duplicates(
        subset=["product_id"]
    )

    df = df[[
        "product_id",
        "nome_produto",
        "product_number",
        "cor",
        "tamanho",
        "nome_subcategoria",
        "nome_categoria",
        "preco_lista",
        "data_alteracao_origem"
    ]]

    return df