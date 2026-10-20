import pandas as pd

from conexoes import conectar_postgres


def buscar_datas_dw():

    conexao = conectar_postgres()

    df = pd.read_sql(
        """
        SELECT
            data_key
        FROM dw.dim_data
        """,
        conexao
    )

    conexao.close()

    return df