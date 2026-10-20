import pandas as pd

from conexoes import conectar_postgres


def carregar_dim_cliente(df_novos, df_alterados):

    conexao = conectar_postgres()
    cursor = conexao.cursor()

    inseridos = 0
    atualizados = 0

    # ========================================
    # INSERT - CLIENTES NOVOS
    # ========================================

    sql_insert = """
        INSERT INTO dw.dim_cliente (
            customer_id,
            nome_cliente,
            tipo_cliente,
            data_alteracao_origem
        )
        VALUES (
            %s, %s, %s, %s
        )
    """

    for _, linha in df_novos.iterrows():

        cursor.execute(
            sql_insert,
            (
                int(linha["CustomerID"]),
                linha["NomeCliente"],
                linha["TipoCliente"],
                linha["ModifiedDate"]
            )
        )

        inseridos += 1

    # ========================================
    # UPDATE - CLIENTES ALTERADOS
    # ========================================

    sql_update = """
        UPDATE dw.dim_cliente
        SET
            nome_cliente = %s,
            tipo_cliente = %s,
            data_alteracao_origem = %s
        WHERE customer_id = %s
    """

    for _, linha in df_alterados.iterrows():

        cursor.execute(
            sql_update,
            (
                linha["NomeCliente"],
                linha["TipoCliente"],
                linha["ModifiedDate"],
                int(linha["CustomerID"])
            )
        )

        atualizados += 1

    # ========================================
    # COMMIT
    # ========================================

    conexao.commit()

    cursor.close()
    conexao.close()

    print(f"Clientes inseridos: {inseridos}")
    print(f"Clientes atualizados: {atualizados}")