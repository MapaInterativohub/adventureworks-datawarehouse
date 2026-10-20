import pandas as pd


def transformar_dim_cliente(df):

    df = df.copy()

    # Padroniza os nomes das colunas
    df = df.rename(columns={
        "CustomerID": "customer_id",
        "NomeCliente": "nome_cliente",
        "TipoCliente": "tipo_cliente"
    })

    # Trata valores nulos
    df["nome_cliente"] = (
        df["nome_cliente"]
        .fillna("Não informado")
    )

    df["tipo_cliente"] = (
        df["tipo_cliente"]
        .fillna("Não informado")
    )

    # Garante que CustomerID seja inteiro
    df["customer_id"] = pd.to_numeric(
        df["customer_id"],
        errors="coerce"
    )

    # Remove registros sem CustomerID
    df = df.dropna(
        subset=["customer_id"]
    )

    df["customer_id"] = (
        df["customer_id"]
        .astype(int)
    )

    # Remove clientes duplicados
    df = df.drop_duplicates(
        subset=["customer_id"]
    )

    # Seleciona somente as colunas da dimensão
    df = df[
        [
            "customer_id",
            "nome_cliente",
            "tipo_cliente"
        ]
    ]

    return df