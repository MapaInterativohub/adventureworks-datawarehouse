import pandas as pd

from conexoes import conectar_sql_server


def extrair_dim_territorio(data_controle=None):

    sql = """
        SELECT
            TerritoryID,
            Name AS NomeTerritorio,
            CountryRegionCode AS Pais,
            [Group] AS Grupo,
            ModifiedDate
        FROM Sales.SalesTerritory
    """

    parametros = None

    if data_controle is not None:
        sql += """
            WHERE ModifiedDate > ?
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

    df = extrair_dim_territorio()

    print(df.head())

    print("\nQuantidade de registros:")
    print(len(df))

    print("\nColunas:")
    print(df.columns)