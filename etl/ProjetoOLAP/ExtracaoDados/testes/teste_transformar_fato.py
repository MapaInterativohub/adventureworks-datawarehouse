from Extrair.extrair_fato_vendas import extrair_fato_vendas
from buscar_chaves_dimensoes import buscar_chaves_dimensoes
from transformacao.transformar_fato_vendas import transformar_fato_vendas


# ========================================
# EXTRAÇÃO
# ========================================

df_vendas = extrair_fato_vendas()

print("================================")
print("EXTRAÇÃO")
print("================================")

print(f"Registros: {len(df_vendas)}")


# ========================================
# BUSCAR CHAVES DAS DIMENSÕES
# ========================================

(
    df_produto,
    df_cliente,
    df_territorio,
    df_data
) = buscar_chaves_dimensoes()


# ========================================
# TRANSFORMAÇÃO
# ========================================

df_fato = transformar_fato_vendas(
    df_vendas,
    df_produto,
    df_cliente,
    df_territorio,
    df_data
)


# ========================================
# RESULTADO
# ========================================

print("\n================================")
print("TRANSFORMAÇÃO")
print("================================")

print(f"Registros transformados: {len(df_fato)}")

print("\nColunas:")
print(df_fato.columns.tolist())

print("\nPrimeiros registros:")
print(df_fato.head())

print("\nData de alteração:")
print(df_fato["data_alteracao_origem"].min())
print(df_fato["data_alteracao_origem"].max())