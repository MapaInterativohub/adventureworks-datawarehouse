from conexoes import conectar_postgres


def carregar_fato_vendas(df_novos, df_alterados):

    conexao = conectar_postgres()
    cursor = conexao.cursor()

    # ========================================
    # INSERT
    # ========================================

    sql_insert = """
        INSERT INTO dw.fato_vendas (
            data_key,
            produto_key,
            cliente_key,
            territorio_key,
            sales_order_id,
            sales_order_detail_id,
            quantidade,
            preco_unitario,
            desconto_percentual,
            valor_bruto,
            valor_desconto,
            receita,
            custo_total,
            margem_bruta,
            data_alteracao_origem
        )
        VALUES (
            %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s
        )
    """

    inseridos = 0

    for _, linha in df_novos.iterrows():

        cursor.execute(sql_insert, (
            int(linha["data_key"]),
            int(linha["produto_key"]),
            int(linha["cliente_key"]),
            int(linha["territorio_key"]),
            int(linha["sales_order_id"]),
            int(linha["sales_order_detail_id"]),
            int(linha["quantidade"]),
            float(linha["preco_unitario"]),
            float(linha["desconto_percentual"]),
            float(linha["valor_bruto"]),
            float(linha["valor_desconto"]),
            float(linha["receita"]),

            None if linha["custo_total"] != linha["custo_total"]
            else float(linha["custo_total"]),

            None if linha["margem_bruta"] != linha["margem_bruta"]
            else float(linha["margem_bruta"]),

            linha["data_alteracao_origem"]
        ))

        inseridos += 1

    # ========================================
    # UPDATE
    # ========================================

    sql_update = """
        UPDATE dw.fato_vendas
        SET
            data_key = %s,
            produto_key = %s,
            cliente_key = %s,
            territorio_key = %s,
            quantidade = %s,
            preco_unitario = %s,
            desconto_percentual = %s,
            valor_bruto = %s,
            valor_desconto = %s,
            receita = %s,
            custo_total = %s,
            margem_bruta = %s,
            data_alteracao_origem = %s
        WHERE
            sales_order_id = %s
            AND sales_order_detail_id = %s
    """

    atualizados = 0

    for _, linha in df_alterados.iterrows():

        cursor.execute(sql_update, (
            int(linha["data_key"]),
            int(linha["produto_key"]),
            int(linha["cliente_key"]),
            int(linha["territorio_key"]),
            int(linha["quantidade"]),
            float(linha["preco_unitario"]),
            float(linha["desconto_percentual"]),
            float(linha["valor_bruto"]),
            float(linha["valor_desconto"]),
            float(linha["receita"]),

            None if linha["custo_total"] != linha["custo_total"]
            else float(linha["custo_total"]),

            None if linha["margem_bruta"] != linha["margem_bruta"]
            else float(linha["margem_bruta"]),

            linha["data_alteracao_origem"],

            int(linha["sales_order_id"]),
            int(linha["sales_order_detail_id"])
        ))

        atualizados += 1

    # ========================================
    # COMMIT
    # ========================================

    conexao.commit()

    cursor.close()
    conexao.close()

    print(f"Vendas inseridas: {inseridos}")
    print(f"Vendas atualizadas: {atualizados}")