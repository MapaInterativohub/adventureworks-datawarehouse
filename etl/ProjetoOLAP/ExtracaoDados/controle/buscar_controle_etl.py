from conexoes import conectar_postgres


def buscar_ultima_execucao(processo):

    conexao = conectar_postgres()
    cursor = conexao.cursor()

    sql = """
        SELECT ultima_execucao
        FROM dw.controle_etl
        WHERE processo = %s
    """

    cursor.execute(sql, (processo,))

    resultado = cursor.fetchone()

    cursor.close()
    conexao.close()

    if resultado is None:
        return None

    return resultado[0]


def atualizar_ultima_execucao(processo, data_execucao):

    conexao = conectar_postgres()
    cursor = conexao.cursor()

    sql = """
        UPDATE dw.controle_etl
        SET ultima_execucao = %s
        WHERE processo = %s
    """

    cursor.execute(sql, (
        data_execucao,
        processo
    ))

    conexao.commit()

    cursor.close()
    conexao.close()