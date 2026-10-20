import pandas as pd

from conexoes import conectar_postgres


def buscar_produtos_dw():

    conexao = conectar_postgres()

    df = pd.read_sql(
        """
        SELECT
            product_id,
            data_alteracao_origem
        FROM dw.dim_produto
        """,
        conexao
    )

    conexao.close()

    return df


def identificar_incremental_produto(
    df_origem,
    data_controle
):

    df_dw = buscar_produtos_dw()

    # Caso a dimensão esteja vazia
    if df_dw.empty:

        df_novos = df_origem.copy()
        df_alterados = df_origem.iloc[0:0].copy()

        return df_novos, df_alterados

    # Produtos que já existem no DW
    produtos_existentes = set(
        df_dw["product_id"]
    )

    # -----------------------------
    # PRODUTOS NOVOS
    # -----------------------------

    df_novos = df_origem[
        ~df_origem["ProductID"].isin(
            produtos_existentes
        )
    ].copy()

    # -----------------------------
    # PRODUTOS ALTERADOS
    # -----------------------------

    df_alterados = df_origem[
        df_origem["ProductID"].isin(
            produtos_existentes
        )
    ].copy()

    df_alterados["ModifiedDate"] = pd.to_datetime(
        df_alterados["ModifiedDate"]
    )

    data_controle = pd.to_datetime(
        data_controle
    )

    df_alterados = df_alterados[
        df_alterados["ModifiedDate"] > data_controle
    ].copy()

    return df_novos, df_alterados