import pandas as pd
from conexoes import conectar_sql_server


def extrair_fato_vendas(data_controle=None):

    sql = """
        SELECT
            soh.OrderDate,
            sod.ProductID,
            soh.CustomerID,
            soh.TerritoryID,
            sod.SalesOrderID,
            sod.SalesOrderDetailID,
            sod.OrderQty,
            sod.UnitPrice,
            sod.UnitPriceDiscount,

            sod.OrderQty * sod.UnitPrice AS ValorBruto,

            sod.OrderQty * sod.UnitPrice * sod.UnitPriceDiscount
                AS ValorDesconto,

            sod.LineTotal AS Receita,

            pch.StandardCost,

            sod.OrderQty * pch.StandardCost AS CustoTotal,

            CASE
                WHEN soh.ModifiedDate > sod.ModifiedDate
                    THEN soh.ModifiedDate
                ELSE sod.ModifiedDate
            END AS ModifiedDate

        FROM Sales.SalesOrderDetail sod

        INNER JOIN Sales.SalesOrderHeader soh
            ON sod.SalesOrderID = soh.SalesOrderID

        OUTER APPLY
        (
            SELECT TOP 1
                pch.StandardCost
            FROM Production.ProductCostHistory pch
            WHERE pch.ProductID = sod.ProductID
              AND pch.StartDate <= soh.OrderDate
              AND (
                    pch.EndDate IS NULL
                    OR pch.EndDate >= soh.OrderDate
                  )
            ORDER BY pch.StartDate DESC
        ) pch
    """

    parametros = None

    if data_controle is not None:

        sql += """
            WHERE
                CASE
                    WHEN soh.ModifiedDate > sod.ModifiedDate
                        THEN soh.ModifiedDate
                    ELSE sod.ModifiedDate
                END > ?
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


# ========================================
# TESTE DA EXTRAÇÃO
# ========================================

if __name__ == "__main__":

    df = extrair_fato_vendas()

    print("================================")
    print("EXTRAÇÃO DA FATO VENDAS")
    print("================================")

    print(f"Registros extraídos: {len(df)}")

    print("\n================================")
    print("COLUNAS")
    print("================================")

    print(df.columns.tolist())

    print("\n================================")
    print("PRIMEIROS REGISTROS")
    print("================================")

    print(df.head())

    print("\n================================")
    print("MAIOR MODIFIEDDATE")
    print("================================")

    print(df["ModifiedDate"].max())