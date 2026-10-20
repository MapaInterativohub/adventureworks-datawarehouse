import pandas as pd

from conexoes import conectar_sql_server


def extrair_dim_data():

    sql = """
        SELECT
            MIN(OrderDate) AS DataInicial,
            MAX(OrderDate) AS DataFinal
        FROM Sales.SalesOrderHeader
    """

    conexao = conectar_sql_server()

    df_datas = pd.read_sql(sql, conexao)

    conexao.close()

    data_inicial = pd.to_datetime(
        df_datas["DataInicial"].iloc[0]
    )

    data_final = pd.to_datetime(
        df_datas["DataFinal"].iloc[0]
    )

    datas = pd.date_range(
        start=data_inicial,
        end=data_final,
        freq="D"
    )

    df = pd.DataFrame({
        "data": datas
    })

    df["data_key"] = (
        df["data"]
        .dt.strftime("%Y%m%d")
        .astype(int)
    )

    df["dia"] = df["data"].dt.day

    df["mes"] = df["data"].dt.month

    df["nome_mes"] = df["data"].dt.month_name()

    df["trimestre"] = df["data"].dt.quarter

    df["ano"] = df["data"].dt.year

    df["dia_semana"] = (
        df["data"].dt.dayofweek + 1
    )

    df["nome_dia_semana"] = (
        df["data"].dt.day_name()
    )

    return df[
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


if __name__ == "__main__":

    df = extrair_dim_data()

    print(df.head(10))

    print("\nQuantidade de registros:")
    print(len(df))

    print("\nData inicial:")
    print(df["data"].min())

    print("\nData final:")
    print(df["data"].max())

    print("\nColunas:")
    print(df.columns)