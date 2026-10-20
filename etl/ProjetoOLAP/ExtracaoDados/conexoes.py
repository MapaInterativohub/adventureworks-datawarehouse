import pyodbc
import psycopg2


def conectar_sql_server():
    conexao = pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=localhost;"
        "DATABASE=AdventureWorks2016;"
        "Trusted_Connection=yes;"
    )

    return conexao

def conectar_postgres():

    conexao = psycopg2.connect(
        host="localhost",
        port="5432",
        database="postgres",
        user="postgres",
        password="1234"
    )

    return conexao


if __name__ == "__main__":

    conexao = conectar_postgres()

    print("Conexão realizada com sucesso!")

    conexao.close()