from conexoes import conectar_postgres


def carregar_dim_territorio(df_novos, df_alterados):

    conexao = conectar_postgres()
    cursor = conexao.cursor()

    inseridos = 0
    atualizados = 0

    # ========================================
    # INSERT - TERRITÓRIOS NOVOS
    # ========================================

    sql_insert = """
        INSERT INTO dw.dim_territorio (
            territory_id,
            nome_territorio,
            pais,
            grupo,
            data_alteracao_origem
        )
        VALUES (
            %s, %s, %s, %s, %s
        )
    """

    for _, linha in df_novos.iterrows():

        cursor.execute(
            sql_insert,
            (
                int(linha["TerritoryID"]),
                linha["NomeTerritorio"],
                linha["Pais"],
                linha["Grupo"],
                linha["ModifiedDate"]
            )
        )

        inseridos += 1

    # ========================================
    # UPDATE - TERRITÓRIOS ALTERADOS
    # ========================================

    sql_update = """
        UPDATE dw.dim_territorio
        SET
            nome_territorio = %s,
            pais = %s,
            grupo = %s,
            data_alteracao_origem = %s
        WHERE territory_id = %s
    """

    for _, linha in df_alterados.iterrows():

        cursor.execute(
            sql_update,
            (
                linha["NomeTerritorio"],
                linha["Pais"],
                linha["Grupo"],
                linha["ModifiedDate"],
                int(linha["TerritoryID"])
            )
        )

        atualizados += 1

    conexao.commit()

    cursor.close()
    conexao.close()

    print(f"Territórios inseridos: {inseridos}")
    print(f"Territórios atualizados: {atualizados}")