import pandas as pd
from conexoes import conectar_postgres


def buscar_vendas_dw():

    conexao = conectar_postgres()

    df = pd.read_sql(
        """
        SELECT
            sales_order_id,
            sales_order_detail_id,
            data_alteracao_origem
        FROM dw.fato_vendas
        """,
        conexao
    )

    conexao.close()

    return df


def identificar_incremental_fato(df_origem, data_controle):

    df_dw = buscar_vendas_dw()

    # Se a fato estiver vazia, todos os registros são novos
    if df_dw.empty:

        df_novos = df_origem.copy()

        df_alterados = df_origem.iloc[0:0].copy()

        return df_novos, df_alterados

    # Criar uma chave composta:
    # SalesOrderID + SalesOrderDetailID

    chave_origem = (
        df_origem["SalesOrderID"].astype(str)
        + "-"
        + df_origem["SalesOrderDetailID"].astype(str)
    )

    chave_dw = (
        df_dw["sales_order_id"].astype(str)
        + "-"
        + df_dw["sales_order_detail_id"].astype(str)
    )

    # Registros novos
    df_novos = df_origem[
        ~chave_origem.isin(chave_dw)
    ].copy()

    # Registros que já existem
    df_alterados = df_origem[
        chave_origem.isin(chave_dw)
    ].copy()

    # Converter datas
    df_alterados["ModifiedDate"] = pd.to_datetime(
        df_alterados["ModifiedDate"]
    )

    data_controle = pd.to_datetime(data_controle)

    # Somente registros alterados depois
    # da última execução
    df_alterados = df_alterados[
        df_alterados["ModifiedDate"] > data_controle
    ].copy()

    return df_novos, df_alterados