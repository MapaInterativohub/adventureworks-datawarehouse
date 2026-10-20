import pandas as pd

from conexoes import conectar_postgres


def buscar_chaves_dimensoes():

    conexao = conectar_postgres()

    df_produto = pd.read_sql(
        """
        SELECT
            produto_key,
            product_id
        FROM dw.dim_produto
        """,
        conexao
    )

    df_cliente = pd.read_sql(
        """
        SELECT
            cliente_key,
            customer_id
        FROM dw.dim_cliente
        """,
        conexao
    )

    df_territorio = pd.read_sql(
        """
        SELECT
            territorio_key,
            territory_id
        FROM dw.dim_territorio
        """,
        conexao
    )

    df_data = pd.read_sql(
        """
        SELECT
            data_key,
            data
        FROM dw.dim_data
        """,
        conexao
    )

    conexao.close()

    return (
        df_produto,
        df_cliente,
        df_territorio,
        df_data
    )