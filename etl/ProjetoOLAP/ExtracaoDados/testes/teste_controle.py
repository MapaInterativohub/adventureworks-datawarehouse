from buscar_controle_etl import buscar_ultima_execucao


data = buscar_ultima_execucao("dim_produto")

print("Última execução da dim_produto:")
print(data)