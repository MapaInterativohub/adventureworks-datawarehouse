import pandas as pd


def transformar_fato_vendas(
    df_vendas,
    df_produto,
    df_cliente,
    df_territorio,
    df_data
):

    df = df_vendas.copy()

    # ==========================================
    # 0. CONVERTER IDS PARA O MESMO TIPO
    # ==========================================

    df["ProductID"] = pd.to_numeric(
        df["ProductID"],
        errors="coerce"
    ).astype("Int64")

    df["CustomerID"] = pd.to_numeric(
        df["CustomerID"],
        errors="coerce"
    ).astype("Int64")

    df["TerritoryID"] = pd.to_numeric(
        df["TerritoryID"],
        errors="coerce"
    ).astype("Int64")

    df_produto = df_produto.copy()
    df_cliente = df_cliente.copy()
    df_territorio = df_territorio.copy()

    df_produto["product_id"] = pd.to_numeric(
        df_produto["product_id"],
        errors="coerce"
    ).astype("Int64")

    df_cliente["customer_id"] = pd.to_numeric(
        df_cliente["customer_id"],
        errors="coerce"
    ).astype("Int64")

    df_territorio["territory_id"] = pd.to_numeric(
        df_territorio["territory_id"],
        errors="coerce"
    ).astype("Int64")

    # ==========================================
    # 1. DATA
    # ==========================================

    df["OrderDate"] = pd.to_datetime(
        df["OrderDate"]
    )

    df["data_key"] = (
        df["OrderDate"]
        .dt.strftime("%Y%m%d")
        .astype(int)
    )

    # ==========================================
    # 2. PRODUTO
    # ==========================================

    df = df.merge(
        df_produto,
        left_on="ProductID",
        right_on="product_id",
        how="left"
    )

    # ==========================================
    # 3. CLIENTE
    # ==========================================

    df = df.merge(
        df_cliente,
        left_on="CustomerID",
        right_on="customer_id",
        how="left"
    )

    # ==========================================
    # 4. TERRITÓRIO
    # ==========================================

    df = df.merge(
        df_territorio,
        left_on="TerritoryID",
        right_on="territory_id",
        how="left"
    )

    # ==========================================
    # 5. VALIDAR DATA
    # ==========================================

    df = df.merge(
        df_data,
        on="data_key",
        how="left",
        suffixes=("", "_dim")
    )

    # ==========================================
    # 6. RENOMEAR COLUNAS
    # ==========================================

    df = df.rename(columns={

        "SalesOrderID":
            "sales_order_id",

        "SalesOrderDetailID":
            "sales_order_detail_id",

        "OrderQty":
            "quantidade",

        "UnitPrice":
            "preco_unitario",

        "UnitPriceDiscount":
            "desconto_percentual",

        "ValorBruto":
            "valor_bruto",

        "ValorDesconto":
            "valor_desconto",

        "Receita":
            "receita",

        "CustoTotal":
            "custo_total",

        "ModifiedDate":
            "data_alteracao_origem"

    })

    # ==========================================
    # 7. MARGEM BRUTA
    # ==========================================

    df["margem_bruta"] = (
        df["receita"] -
        df["custo_total"]
    )

    # ==========================================
    # 8. SELECIONAR CAMPOS DA FATO
    # ==========================================

    df = df[
        [
            "data_key",
            "produto_key",
            "cliente_key",
            "territorio_key",
            "sales_order_id",
            "sales_order_detail_id",
            "quantidade",
            "preco_unitario",
            "desconto_percentual",
            "valor_bruto",
            "valor_desconto",
            "receita",
            "custo_total",
            "margem_bruta",
            "data_alteracao_origem"
        ]
    ]

    return df