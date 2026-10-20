import pandas as pd

from conexoes import conectar_sql_server


def extrair_dim_produto(data_controle=None):

    sql = """
        SELECT
            p.ProductID,
            p.Name AS NomeProduto,
            p.ProductNumber,
            p.Color,
            p.Size,
            ps.Name AS NomeSubcategoria,
            pc.Name AS NomeCategoria,
            p.ListPrice,
            p.ModifiedDate
        FROM Production.Product p

        LEFT JOIN Production.ProductSubcategory ps
            ON p.ProductSubcategoryID = ps.ProductSubcategoryID

        LEFT JOIN Production.ProductCategory pc
            ON ps.ProductCategoryID = pc.ProductCategoryID
    """

    parametros = None

    # Se existir uma data de controle,
    # busca somente produtos modificados depois dela.
    if data_controle is not None:

        sql += """
            WHERE p.ModifiedDate > ?
        """

        parametros = (data_controle,)

    conexao = conectar_sql_server()

    df = pd.read_sql(
        sql,
        conexao,
        params=parametros
    )

    conexao.close()

    return df


if __name__ == "__main__":

    df = extrair_dim_produto()

    print(df.head())

    print("\nQuantidade de registros:")
    print(len(df))

    print("\nColunas:")
    print(df.columns)