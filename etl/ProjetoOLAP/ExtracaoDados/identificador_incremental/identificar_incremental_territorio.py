import pandas as pd

from conexoes import conectar_postgres


def buscar_territorios_dw():

    conexao = conectar_postgres()

    df = pd.read_sql(
        """
        SELECT
            territory_id,
            data_alteracao_origem
        FROM dw.dim_territorio
        """,
        conexao
    )

    conexao.close()

    return df


def identificar_incremental_territorio(
    df_origem,
    data_controle
):

    df_dw = buscar_territorios_dw()

    if df_dw.empty:

        df_novos = df_origem.copy()
        df_alterados = df_origem.iloc[0:0].copy()

        return df_novos, df_alterados

    territorios_existentes = set(
        df_dw["territory_id"]
    )

    # ========================================
    # TERRITÓRIOS NOVOS
    # ========================================

    df_novos = df_origem[
        ~df_origem["TerritoryID"].isin(
            territorios_existentes
        )
    ].copy()

    # ========================================
    # TERRITÓRIOS EXISTENTES
    # ========================================

    df_alterados = df_origem[
        df_origem["TerritoryID"].isin(
            territorios_existentes
        )
    ].copy()

    df_alterados["ModifiedDate"] = pd.to_datetime(
        df_alterados["ModifiedDate"]
    )

    data_controle = pd.to_datetime(
        data_controle
    )

    # Somente territórios modificados
    # depois da última execução
    df_alterados = df_alterados[
        df_alterados["ModifiedDate"] > data_controle
    ].copy()

    return df_novos, df_alterados