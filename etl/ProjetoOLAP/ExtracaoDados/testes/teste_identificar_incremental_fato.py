from Extrair.extrair_fato_vendas import extrair_fato_vendas
from buscar_controle_etl import buscar_ultima_execucao
from identificador_incremental.identificar_incremental_fato import identificar_incremental_fato


# ========================================
# BUSCAR DATA DE CONTROLE
# ========================================

data_controle = buscar_ultima_execucao("fato_vendas")

print("================================")
print("DATA DE CONTROLE")
print("================================")

print(data_controle)


# ========================================
# EXTRAÇÃO
# ========================================

df = extrair_fato_vendas(data_controle)

print("\n================================")
print("EXTRAÇÃO")
print("================================")

print(f"Registros extraídos: {len(df)}")


# ========================================
# IDENTIFICAÇÃO INCREMENTAL
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

    print("\n================================")
    print("RESULTADO")
    print("================================")

    if len(df_novos) > 0:
        print("Existem vendas novas.")

    if len(df_alterados) > 0:
        print("Existem vendas alteradas.")

    if len(df_novos) == 0 and len(df_alterados) == 0:
        print("Nenhuma alteração encontrada.")