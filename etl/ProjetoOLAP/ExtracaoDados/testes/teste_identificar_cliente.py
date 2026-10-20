from Extrair.extrair_dim_cliente import extrair_dim_cliente

from buscar_controle_etl import buscar_ultima_execucao

from identificador_incremental.identificar_incremental_cliente import identificar_incremental_cliente


# Busca a última execução da dim_cliente
data_controle = buscar_ultima_execucao("dim_cliente")

print("================================")
print("DATA DE CONTROLE")
print("================================")
print(data_controle)


# Extrai somente registros posteriores
# à data de controle
df = extrair_dim_cliente(data_controle)

print("\n================================")
print("EXTRAÇÃO")
print("================================")
print(f"Registros extraídos: {len(df)}")


if df.empty:

    print("\nNenhum cliente novo ou alterado.")

else:

    df_novos, df_alterados = identificar_incremental_cliente(
        df,
        data_controle
    )

    print("\n================================")
    print("INCREMENTAL")
    print("================================")

    print(f"Clientes novos: {len(df_novos)}")
    print(f"Clientes alterados: {len(df_alterados)}")