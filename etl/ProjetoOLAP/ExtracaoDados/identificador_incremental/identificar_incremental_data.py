from controle.buscar_datas_dw import buscar_datas_dw


def identificar_incremental_data(df_origem):

    df_dw = buscar_datas_dw()

    if df_dw.empty:
        return df_origem.copy()

    datas_existentes = set(
        df_dw["data_key"]
    )

    df_novas = df_origem[
        ~df_origem["data_key"].isin(
            datas_existentes
        )
    ].copy()

    return df_novas