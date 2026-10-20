from Extrair.extrair_dim_territorio import (
    extrair_dim_territorio
)

from buscar_controle_etl import (
    buscar_ultima_execucao
)

from identificador_incremental.identificar_incremental_territorio import (
    identificar_incremental_territorio
)


data_controle = buscar_ultima_execucao(
    "dim_territorio"
)

print("================================")
print("DATA DE CONTROLE")
print("================================")
print(data_controle)


df = extrair_dim_territorio(
    data_controle
)

print("\n================================")
print("EXTRAÇÃO")
print("================================")
print(f"Registros extraídos: {len(df)}")


if df.empty:

    print("\nNenhum território novo ou alterado.")

else:

    df_novos, df_alterados = (
        identificar_incremental_territorio(
            df,
            data_controle
        )
    )

    print("\n================================")
    print("INCREMENTAL")
    print("================================")

    print(
        f"Territórios novos: {len(df_novos)}"
    )

    print(
        f"Territórios alterados: {len(df_alterados)}"
    )