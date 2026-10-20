from conexoes import conectar_postgres
import pandas as pd

def carregar_dim_produto(df_novos, df_alterados):

    conexao = conectar_postgres()
    cursor = conexao.cursor()

    inseridos = 0
    atualizados = 0

    # =========================================================
    # INSERT - PRODUTOS NOVOS
    # =========================================================

    sql_insert = """
        INSERT INTO dw.dim_produto (
            product_id,
            nome_produto,
            product_number,
            cor,
            tamanho,
            nome_subcategoria,
            nome_categoria,
            preco_lista,
            data_alteracao_origem
        )
        VALUES (
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s
        )
    """

    for _, linha in df_novos.iterrows():

        cursor.execute(
            sql_insert,
            (
                int(linha["ProductID"]),
                linha["NomeProduto"],
                linha["ProductNumber"],
                linha["Color"] if pd.notna(linha["Color"]) else "Não informado",
                linha["Size"] if pd.notna(linha["Size"]) else "Não informado",
                linha["NomeSubcategoria"],
                linha["NomeCategoria"],
                float(linha["ListPrice"]),
                linha["ModifiedDate"]
            )
        )

        inseridos += 1

    # =========================================================
    # UPDATE - PRODUTOS ALTERADOS
    # =========================================================

    sql_update = """
        UPDATE dw.dim_produto
        SET
            nome_produto = %s,
            product_number = %s,
            cor = %s,
            tamanho = %s,
            nome_subcategoria = %s,
            nome_categoria = %s,
            preco_lista = %s,
            data_alteracao_origem = %s
        WHERE product_id = %s
    """

    for _, linha in df_alterados.iterrows():

        cursor.execute(
            sql_update,
            (
                linha["NomeProduto"],
                linha["ProductNumber"],
                linha["Color"] if pd.notna(linha["Color"]) else "Não informado",
                linha["Size"] if pd.notna(linha["Size"]) else "Não informado",
                linha["NomeSubcategoria"],
                linha["NomeCategoria"],
                float(linha["ListPrice"]),
                linha["ModifiedDate"],
                int(linha["ProductID"])
            )
        )

        atualizados += 1

    conexao.commit()

    cursor.close()
    conexao.close()

    print(f"Produtos inseridos: {inseridos}")
    print(f"Produtos atualizados: {atualizados}")