from Extrair.extrair_dim_produto import extrair_dim_produto

from buscar_controle_etl import (
    buscar_ultima_execucao,
    atualizar_ultima_execucao
)

from identificar_incremental_produto import (
    identificar_incremental_produto
)

from carregar_dim_produto import (
    carregar_dim_produto
)


# ============================================================
# 1. BUSCAR DATA DE CONTROLE
# ============================================================

data_controle = buscar_ultima_execucao(
    "dim_produto"
)

print("================================")
print("DATA DE CONTROLE")
print("================================")

print(data_controle)


# ============================================================
# 2. EXTRAIR
# ============================================================

df = extrair_dim_produto(
    data_controle
)

print("\n================================")
print("EXTRAÇÃO")
print("================================")

print(f"Registros extraídos: {len(df)}")


# ============================================================
# 3. VERIFICAR SE EXISTEM DADOS
# ============================================================

if df.empty:

    print("\nNenhum produto novo ou alterado.")

else:

    # ========================================================
    # 4. IDENTIFICAR NOVOS E ALTERADOS
    # ========================================================

    df_novos, df_alterados = identificar_incremental_produto(
        df,
        data_controle
    )

    print("\n================================")
    print("INCREMENTAL")
    print("================================")

    print(f"Produtos novos: {len(df_novos)}")
    print(f"Produtos alterados: {len(df_alterados)}")


    # ========================================================
    # 5. CARREGAR
    # ========================================================

    if len(df_novos) > 0 or len(df_alterados) > 0:

        carregar_dim_produto(
            df_novos,
            df_alterados
        )


        # ====================================================
        # 6. ATUALIZAR DATA DE CONTROLE
        # ====================================================

        maior_data = df["ModifiedDate"].max()

        atualizar_ultima_execucao(
            "dim_produto",
            maior_data
        )

        print("\n================================")
        print("CONTROLE ATUALIZADO")
        print("================================")

        print(f"Nova data de controle: {maior_data}")

    else:

        print("\nNenhum registro para carregar.")