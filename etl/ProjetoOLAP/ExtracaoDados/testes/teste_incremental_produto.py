from Extrair.extrair_dim_produto import extrair_dim_produto
from buscar_controle_etl import buscar_ultima_execucao


data_controle = buscar_ultima_execucao("dim_produto")

print("Data de controle:")
print(data_controle)

df = extrair_dim_produto(data_controle)

print("\nProdutos encontrados:")
print(len(df))

print("\nPrimeiros registros:")
print(
    df[
        [
            "ProductID",
            "NomeProduto",
            "ModifiedDate"
        ]
    ].head(10)
)