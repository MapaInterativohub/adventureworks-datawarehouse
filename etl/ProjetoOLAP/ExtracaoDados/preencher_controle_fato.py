import pandas as pd

from conexoes import conectar_sql_server
from conexoes import conectar_postgres


# ========================================
# 1. BUSCAR MODIFIEDDATE DA ORIGEM
# ========================================

def buscar_datas_origem():

    sql = """
        SELECT
            sod.SalesOrderID,
            sod.SalesOrderDetailID,

            CASE
                WHEN soh.ModifiedDate > sod.ModifiedDate
                    THEN soh.ModifiedDate
                ELSE sod.ModifiedDate
            END AS ModifiedDate

        FROM Sales.SalesOrderDetail sod

        INNER JOIN Sales.SalesOrderHeader soh
            ON sod.SalesOrderID = soh.SalesOrderID
    """

    conexao = conectar_sql_server()

    df = pd.read_sql(
        sql,
        conexao
    )

    conexao.close()

    return df


# ========================================
# 2. ATUALIZAR POSTGRESQL
# ========================================

def preencher_controle():

    df = buscar_datas_origem()

    print("================================")
    print("ORIGEM")
    print("================================")

    print(f"Registros encontrados: {len(df)}")

    conexao = conectar_postgres()
    cursor = conexao.cursor()

    sql = """
        UPDATE dw.fato_vendas
        SET data_alteracao_origem = %s
        WHERE
            sales_order_id = %s
            AND sales_order_detail_id = %s
    """

    atualizados = 0

    for _, linha in df.iterrows():

        cursor.execute(
            sql,
            (
                linha["ModifiedDate"],
                int(linha["SalesOrderID"]),
                int(linha["SalesOrderDetailID"])
            )
        )

        atualizados += cursor.rowcount

    conexao.commit()

    cursor.close()
    conexao.close()

    print("\n================================")
    print("ATUALIZAÇÃO")
    print("================================")

    print(f"Registros atualizados: {atualizados}")


# ========================================
# EXECUÇÃO
# ========================================

if __name__ == "__main__":

    preencher_controle()