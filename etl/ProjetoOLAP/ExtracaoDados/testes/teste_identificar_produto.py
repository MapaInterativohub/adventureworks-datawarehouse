from Extrair.extrair_dim_produto import extrair_dim_produto

from buscar_controle_etl import buscar_ultima_execucao

from identificar_incremental_produto import (
    identificar_incremental_produto
)


# -----------------------------------------
# 1. Busca a última execução
# -----------------------------------------

data_controle = buscar_ultima_execucao(
    "dim_produto"
)

print("Data de controle:")
print(data_controle)


# -----------------------------------------
# 2. Extrai os dados
# -----------------------------------------

df = extrair_dim_produto(
    data_controle
)

print("\nRegistros extraídos:")
print(len(df))


# -----------------------------------------
# 3. Identifica novos e alterados
# -----------------------------------------

df_novos, df_alterados = identificar_incremental_produto(
    df,
    data_controle
)


# -----------------------------------------
# 4. Resultado
# -----------------------------------------

print("\n==============================")
print("RESULTADO INCREMENTAL")
print("==============================")


print("\nProdutos novos:")
print(len(df_novos))


print("\nProdutos alterados:")
print(len(df_alterados))


print("\nProdutos novos:")
print(
    df_novos[
        [
            "ProductID",
            "NomeProduto",
            "ModifiedDate"
        ]
    ].head(10)
)


print("\nProdutos alterados:")
print(
    df_alterados[
        [
            "ProductID",
            "NomeProduto",
            "ModifiedDate"
        ]
    ].head(10)
)