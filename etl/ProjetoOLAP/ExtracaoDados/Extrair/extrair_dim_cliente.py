import pandas as pd

from conexoes import conectar_sql_server


def extrair_dim_cliente(data_controle=None):

    sql = """
        SELECT
            c.CustomerID,

            CASE
                WHEN c.PersonID IS NOT NULL
                    THEN CONCAT(p.FirstName, ' ', p.LastName)

                WHEN c.StoreID IS NOT NULL
                    THEN s.Name

                ELSE 'Não informado'
            END AS NomeCliente,

            CASE
                WHEN c.PersonID IS NOT NULL
                    THEN 'Pessoa'

                WHEN c.StoreID IS NOT NULL
                    THEN 'Empresa'

                ELSE 'Não informado'
            END AS TipoCliente,

            c.ModifiedDate

        FROM Sales.Customer c

        LEFT JOIN Person.Person p
            ON c.PersonID = p.BusinessEntityID

        LEFT JOIN Sales.Store s
            ON c.StoreID = s.BusinessEntityID
    """

    parametros = None

    if data_controle is not None:
        sql += """
            WHERE c.ModifiedDate > ?
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

    df = extrair_dim_cliente()

    print(df.head())

    print("\nQuantidade de registros:")
    print(len(df))

    print("\nColunas:")
    print(df.columns)