from conexoes import conectar_postgres


def carregar_dim_data(df):

    conexao = conectar_postgres()

    cursor = conexao.cursor()

    sql = """
        INSERT INTO dw.dim_data (
            data_key,
            data,
            dia,
            mes,
            nome_mes,
            trimestre,
            ano,
            dia_semana,
            nome_dia_semana
        )
        VALUES (
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s
        )
    """

    for _, linha in df.iterrows():

        cursor.execute(
            sql,
            (
                linha["data_key"],
                linha["data"],
                linha["dia"],
                linha["mes"],
                linha["nome_mes"],
                linha["trimestre"],
                linha["ano"],
                linha["dia_semana"],
                linha["nome_dia_semana"]
            )
        )

    conexao.commit()

    cursor.close()
    conexao.close()

    print("Dim_Data carregada com sucesso!")


if __name__ == "__main__":

    from Extrair.extrair_dim_data import extrair_dim_data
    from transformacao.transformar_dim_data import transformar_dim_data

    print("Extraindo datas...")

    df = extrair_dim_data()

    print(f"Datas extraídas: {len(df)}")

    print("Transformando datas...")

    df = transformar_dim_data(df)

    print(f"Datas transformadas: {len(df)}")

    print("Carregando datas...")

    carregar_dim_data(df)