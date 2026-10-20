from Extrair.extrair_fato_vendas import extrair_fato_vendas
from buscar_controle_etl import buscar_ultima_execucao, atualizar_ultima_execucao
from identificador_incremental.identificar_incremental_fato import identificar_incremental_fato
from transformacao.transformar_fato_vendas import transformar_fato_vendas
from buscar_chaves_dimensoes import buscar_chaves_dimensoes
from carregar_fato_vendas import carregar_fato_vendas


# ========================================
# 1. DATA DE CONTROLE
# ========================================

data_controle = buscar_ultima_execucao("fato_vendas")

print("================================")
print("DATA DE CONTROLE")
print("================================")

print(data_controle)


# ========================================
# 2. EXTRAÇÃO
# ========================================

df = extrair_fato_vendas(data_controle)

print("\n================================")
print("EXTRAÇÃO")
print("================================")

print(f"Registros extraídos: {len(df)}")


# ========================================
# 3. IDENTIFICAÇÃO INCREMENTAL
# ========================================

if df.empty:

    print("\nNenhuma venda nova ou alterada.")

else:

    df_novos, df_alterados = identificar_incremental_fato(
        df,
        data_controle
    )

    print("\n================================")
    print("INCREMENTAL")
    print("================================")

    print(f"Vendas novas: {len(df_novos)}")
    print(f"Vendas alteradas: {len(df_alterados)}")


    # ========================================
    # 4. TRANSFORMAÇÃO
    # ========================================

    if len(df_novos) > 0 or len(df_alterados) > 0:

        (
            df_produto,
            df_cliente,
            df_territorio,
            df_data
        ) = buscar_chaves_dimensoes()

        df_novos = transformar_fato_vendas(
            df_novos,
            df_produto,
            df_cliente,
            df_territorio,
            df_data
        )

        df_alterados = transformar_fato_vendas(
            df_alterados,
            df_produto,
            df_cliente,
            df_territorio,
            df_data
        )


        # ========================================
        # 5. CARGA
        # ========================================

        carregar_fato_vendas(
            df_novos,
            df_alterados
        )


        # ========================================
        # 6. ATUALIZAR CONTROLE
        # ========================================

        maior_data = df["ModifiedDate"].max()

        atualizar_ultima_execucao(
            "fato_vendas",
            maior_data
        )

        print("\n================================")
        print("CONTROLE ATUALIZADO")
        print("================================")

        print(f"Nova data de controle: {maior_data}")

    else:

        print("\nNenhum registro para carregar.")