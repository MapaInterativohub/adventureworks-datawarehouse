import pandas as pd

from conexoes import conectar_postgres


def buscar_clientes_dw():

    conexao = conectar_postgres()

    df = pd.read_sql(
        """
        SELECT
            customer_id,
            data_alteracao_origem
        FROM dw.dim_cliente
        """,
        conexao
    )

    conexao.close()

    return df


def identificar_incremental_cliente(df_origem, data_controle):

    df_dw = buscar_clientes_dw()

    if df_dw.empty:

        df_novos = df_origem.copy()
        df_alterados = df_origem.iloc[0:0].copy()

        return df_novos, df_alterados

    clientes_existentes = set(
        df_dw["customer_id"]
    )

    # Clientes que ainda não existem no DW
    df_novos = df_origem[
        ~df_origem["CustomerID"].isin(clientes_existentes)
    ].copy()

    # Clientes que já existem no DW
    df_alterados = df_origem[
        df_origem["CustomerID"].isin(clientes_existentes)
    ].copy()

    df_alterados["ModifiedDate"] = pd.to_datetime(
        df_alterados["ModifiedDate"]
    )

    data_controle = pd.to_datetime(
        data_controle
    )

    # Somente clientes modificados depois
    # da última execução
    df_alterados = df_alterados[
        df_alterados["ModifiedDate"] > data_controle
    ].copy()

    return df_novos, df_alterados