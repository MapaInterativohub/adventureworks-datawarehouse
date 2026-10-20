from Extrair.extrair_dim_cliente import extrair_dim_cliente

from buscar_controle_etl import (
    buscar_ultima_execucao,
    atualizar_ultima_execucao
)

from identificador_incremental.identificar_incremental_cliente import (
    identificar_incremental_cliente
)

from carregar_dim_cliente import (
    carregar_dim_cliente
)


# ========================================
# DATA DE CONTROLE
# ========================================

data_controle = buscar_ultima_execucao("dim_cliente")

print("================================")
print("DATA DE CONTROLE")
print("================================")
print(data_controle)


# ========================================
# EXTRAÇÃO
# ========================================

df = extrair_dim_cliente(data_controle)

print("\n================================")
print("EXTRAÇÃO")
print("================================")
print(f"Registros extraídos: {len(df)}")


if df.empty:

    print("\nNenhum cliente novo ou alterado.")

else:

    # ========================================
    # IDENTIFICAÇÃO
    # ========================================

    df_novos, df_alterados = identificar_incremental_cliente(
        df,
        data_controle
    )

    print("\n================================")
    print("INCREMENTAL")
    print("================================")

    print(f"Clientes novos: {len(df_novos)}")
    print(f"Clientes alterados: {len(df_alterados)}")


    # ========================================
    # CARGA
    # ========================================

    if len(df_novos) > 0 or len(df_alterados) > 0:

        carregar_dim_cliente(
            df_novos,
            df_alterados
        )

        # ========================================
        # ATUALIZA CONTROLE
        # ========================================

        maior_data = df["ModifiedDate"].max()

        atualizar_ultima_execucao(
            "dim_cliente",
            maior_data
        )

        print("\n================================")
        print("CONTROLE ATUALIZADO")
        print("================================")
        print(f"Nova data de controle: {maior_data}")

    else:

        print("\nNenhum registro para carregar.")