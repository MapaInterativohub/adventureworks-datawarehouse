import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

from conexoes import (
    conectar_sql_server,
    conectar_postgres
)

from Extrair.extrair_dim_produto import extrair_dim_produto
from Extrair.extrair_dim_cliente import extrair_dim_cliente
from Extrair.extrair_dim_territorio import extrair_dim_territorio
from Extrair.extrair_dim_data import extrair_dim_data
from Extrair.extrair_fato_vendas import extrair_fato_vendas

from transformacao.transformar_dim_produto import transformar_dim_produto
from transformacao.transformar_dim_cliente import transformar_dim_cliente
from transformacao.transformar_dim_territorio import transformar_dim_territorio
from transformacao.transformar_dim_data import transformar_dim_data
from transformacao.transformar_fato_vendas import transformar_fato_vendas

from carregamento.carregar_dim_produto import carregar_dim_produto
from carregamento.carregar_dim_cliente import carregar_dim_cliente
from carregamento.carregar_dim_territorio import carregar_dim_territorio
from carregamento.carregar_dim_data import carregar_dim_data
from carregamento.carregar_fato_vendas import carregar_fato_vendas

from controle.buscar_chaves_dimensoes import buscar_chaves_dimensoes


# ==========================================
# GERAR PERÍODOS MENSAIS
# ==========================================

def gerar_periodos_mensais(data_inicio, data_fim):

    periodos = []

    data_atual = data_inicio

    while data_atual <= data_fim:

        inicio = data_atual

        fim = (
            data_atual
            + relativedelta(months=1)
            - relativedelta(seconds=1)
        )

        if fim > data_fim:
            fim = data_fim

        periodos.append({
            "inicio": inicio,
            "fim": fim
        })

        data_atual = (
            data_atual
            + relativedelta(months=1)
        )

    return periodos


# ==========================================
# EXTRAIR VENDAS DO MÊS
# ==========================================

def extrair_vendas_mes(data_inicio, data_fim):

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

            sod.OrderQty * sod.UnitPrice
                * sod.UnitPriceDiscount AS ValorDesconto,

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

        WHERE soh.OrderDate >= ?
          AND soh.OrderDate <= ?
    """

    conexao = conectar_sql_server()

    df = pd.read_sql(
        sql,
        conexao,
        params=(data_inicio, data_fim)
    )

    conexao.close()

    return df


# ==========================================
# GARANTIR DATAS NO DW
# ==========================================

def carregar_datas_necessarias(data_inicio, data_fim):

    print("\nVerificando dimensão de datas...")

    df_datas = extrair_dim_data()

    df_datas = transformar_dim_data(
        df_datas
    )

    df_datas = df_datas[
        (df_datas["data"] >= data_inicio.date())
        &
        (df_datas["data"] <= data_fim.date())
    ].copy()

    if df_datas.empty:

        print("Nenhuma data encontrada.")

        return

    conexao = conectar_postgres()

    cursor = conexao.cursor()

    cursor.execute(
        """
        SELECT data_key
        FROM dw.dim_data
        WHERE data BETWEEN %s AND %s
        """,
        (
            data_inicio.date(),
            data_fim.date()
        )
    )

    datas_existentes = {
        linha[0]
        for linha in cursor.fetchall()
    }

    cursor.close()
    conexao.close()

    df_datas_novas = df_datas[
        ~df_datas["data_key"].isin(datas_existentes)
    ].copy()

    print(
        f"Datas necessárias: "
        f"{len(df_datas)}"
    )

    print(
        f"Datas novas: "
        f"{len(df_datas_novas)}"
    )

    if not df_datas_novas.empty:

        carregar_dim_data(
            df_datas_novas
        )

    else:

        print(
            "As datas já existem no DW."
        )



# ==========================================
# SIMULAR ALTERAÇÃO DE UMA VENDA
# ==========================================

def simular_alteracao_venda(df_vendas):
    """
    Simula uma alteração em memória, sem alterar
    a base AdventureWorks.
    """

    if df_vendas.empty:
        return df_vendas

    df = df_vendas.copy()

    indice = df.index[0]

    # Simula alteração do desconto
    df.loc[indice, "UnitPriceDiscount"] = 0.10

    # Recalcula os valores da venda
    df.loc[indice, "ValorBruto"] = (
        df.loc[indice, "OrderQty"]
        * df.loc[indice, "UnitPrice"]
    )

    df.loc[indice, "ValorDesconto"] = (
        df.loc[indice, "ValorBruto"]
        * df.loc[indice, "UnitPriceDiscount"]
    )

    df.loc[indice, "Receita"] = (
        df.loc[indice, "ValorBruto"]
        - df.loc[indice, "ValorDesconto"]
    )

    # Data futura para representar alteração na origem
    df.loc[indice, "ModifiedDate"] = pd.Timestamp.now().floor("s")

    print("\n*** ALTERAÇÃO SIMULADA ***")
    print(
        f"Venda: "
        f"{int(df.loc[indice, 'SalesOrderID'])}/"
        f"{int(df.loc[indice, 'SalesOrderDetailID'])}"
    )
    print(
        f"Novo desconto: "
        f"{df.loc[indice, 'UnitPriceDiscount']}"
    )
    print(
        f"Novo ModifiedDate: "
        f"{df.loc[indice, 'ModifiedDate']}"
    )

    return df


# ==========================================
# EXECUTAR UM MÊS
# ==========================================

def executar_mes(data_inicio, data_fim):

    print("\n========================================")
    print(
        f"PROCESSANDO: "
        f"{data_inicio.strftime('%m/%Y')}"
    )
    print("========================================")


    # ======================================
    # 1. EXTRAIR VENDAS
    # ======================================

    print("\nExtraindo vendas...")

    df_vendas = extrair_vendas_mes(
        data_inicio,
        data_fim
    )

    print(
        f"Vendas extraídas: "
        f"{len(df_vendas)}"
    )

    if df_vendas.empty:

        print(
            "Nenhuma venda neste período."
        )

        return


    # ======================================
    # 1.1 SIMULAR ALTERAÇÃO
    # ======================================

    df_vendas = simular_alteracao_venda(
        df_vendas
    )


    # ======================================
    # 2. GARANTIR DATAS
    # ======================================

    carregar_datas_necessarias(
        data_inicio,
        data_fim
    )


    # ======================================
    # 3. BUSCAR CHAVES DAS DIMENSÕES
    # ======================================

    print(
        "\nBuscando chaves das dimensões..."
    )

    (
        df_produto,
        df_cliente,
        df_territorio,
        df_data
    ) = buscar_chaves_dimensoes()


    # ======================================
    # 4. VERIFICAR DIMENSÕES
    # ======================================

    produtos_necessarios = set(
        df_vendas["ProductID"]
    )

    clientes_necessarios = set(
        df_vendas["CustomerID"]
    )

    territorios_necessarios = set(
        df_vendas["TerritoryID"]
    )


    produtos_dw = set(
        df_produto["product_id"]
    )

    clientes_dw = set(
        df_cliente["customer_id"]
    )

    territorios_dw = set(
        df_territorio["territory_id"]
    )


    produtos_faltantes = (
        produtos_necessarios
        - produtos_dw
    )

    clientes_faltantes = (
        clientes_necessarios
        - clientes_dw
    )

    territorios_faltantes = (
        territorios_necessarios
        - territorios_dw
    )


    # ======================================
    # 5. PRODUTOS FALTANTES
    # ======================================

    if produtos_faltantes:

        print(
            f"\nProdutos faltantes: "
            f"{len(produtos_faltantes)}"
        )

        ids = ",".join(
            str(int(x))
            for x in produtos_faltantes
        )

        sql = f"""
            SELECT
                p.ProductID,
                p.Name AS NomeProduto,
                p.ProductNumber,
                p.Color,
                p.Size,
                ps.Name AS NomeSubcategoria,
                pc.Name AS NomeCategoria,
                p.ListPrice,
                p.ModifiedDate
            FROM Production.Product p

            LEFT JOIN Production.ProductSubcategory ps
                ON p.ProductSubcategoryID =
                   ps.ProductSubcategoryID

            LEFT JOIN Production.ProductCategory pc
                ON ps.ProductCategoryID =
                   pc.ProductCategoryID

            WHERE p.ProductID IN ({ids})
        """

        conexao = conectar_sql_server()

        df = pd.read_sql(
            sql,
            conexao
        )

        conexao.close()

        carregar_dim_produto(
            df,
            df.iloc[0:0].copy()
        )

    else:

        print(
            "Todos os produtos já estão no DW."
        )


    # ======================================
    # 6. CLIENTES FALTANTES
    # ======================================

    if clientes_faltantes:

        print(
            f"\nClientes faltantes: "
            f"{len(clientes_faltantes)}"
        )

        ids = ",".join(
            str(int(x))
            for x in clientes_faltantes
        )

        sql = f"""
            SELECT
                c.CustomerID,

                CASE
                    WHEN c.PersonID IS NOT NULL
                        THEN CONCAT(
                            p.FirstName,
                            ' ',
                            p.LastName
                        )

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
                ON c.PersonID =
                   p.BusinessEntityID

            LEFT JOIN Sales.Store s
                ON c.StoreID =
                   s.BusinessEntityID

            WHERE c.CustomerID IN ({ids})
        """

        conexao = conectar_sql_server()

        df = pd.read_sql(
            sql,
            conexao
        )

        conexao.close()

        carregar_dim_cliente(
            df,
            df.iloc[0:0].copy()
        )

    else:

        print(
            "Todos os clientes já estão no DW."
        )


    # ======================================
    # 7. TERRITÓRIOS FALTANTES
    # ======================================

    if territorios_faltantes:

        print(
            f"\nTerritórios faltantes: "
            f"{len(territorios_faltantes)}"
        )

        ids = ",".join(
            str(int(x))
            for x in territorios_faltantes
        )

        sql = f"""
            SELECT
                TerritoryID,
                Name AS NomeTerritorio,
                CountryRegionCode AS Pais,
                [Group] AS Grupo,
                ModifiedDate

            FROM Sales.SalesTerritory

            WHERE TerritoryID IN ({ids})
        """

        conexao = conectar_sql_server()

        df = pd.read_sql(
            sql,
            conexao
        )

        conexao.close()

        carregar_dim_territorio(
            df,
            df.iloc[0:0].copy()
        )

    else:

        print(
            "Todos os territórios já estão no DW."
        )


    # ======================================
    # 8. ATUALIZAR CHAVES
    # ======================================

    (
        df_produto,
        df_cliente,
        df_territorio,
        df_data
    ) = buscar_chaves_dimensoes()


    # ======================================
    # 9. TRANSFORMAR FATO
    # ======================================

    print(
        "\nTransformando vendas..."
    )

    df_vendas = transformar_fato_vendas(
        df_vendas,
        df_produto,
        df_cliente,
        df_territorio,
        df_data
    )


    # ======================================
    # 10. VALIDAR CHAVES
    # ======================================

    erro = False

    if df_vendas["produto_key"].isna().any():
        print(
            "ERRO: produto sem chave."
        )
        erro = True

    if df_vendas["cliente_key"].isna().any():
        print(
            "ERRO: cliente sem chave."
        )
        erro = True

    if df_vendas["territorio_key"].isna().any():
        print(
            "ERRO: território sem chave."
        )
        erro = True

    if df_vendas["data_key"].isna().any():
        print(
            "ERRO: data sem chave."
        )
        erro = True


    if erro:

        print(
            "\nCarga cancelada."
        )

        return


    # ======================================
    # 11. VERIFICAR VENDAS JÁ EXISTENTES
    # ======================================

    conexao = conectar_postgres()

    df_existentes = pd.read_sql(
        """
        SELECT
            sales_order_id,
            sales_order_detail_id,
            data_alteracao_origem
        FROM dw.fato_vendas
        """,
        conexao
    )

    conexao.close()


    # ======================================
    # 11.1 CHAVES EXISTENTES
    # ======================================

    chaves_existentes = set(
        zip(
            df_existentes["sales_order_id"],
            df_existentes["sales_order_detail_id"]
        )
    )

    chaves_origem = list(
        zip(
            df_vendas["sales_order_id"],
            df_vendas["sales_order_detail_id"]
        )
    )


    # ======================================
    # 11.2 VENDAS NOVAS
    # ======================================

    df_novas = df_vendas[
        [
            chave not in chaves_existentes
            for chave in chaves_origem
        ]
    ].copy()


    # ======================================
    # 11.3 VENDAS EXISTENTES
    # ======================================

    df_existentes_origem = df_vendas[
        [
            chave in chaves_existentes
            for chave in chaves_origem
        ]
    ].copy()


    # ======================================
    # 11.4 VENDAS ALTERADAS
    # ======================================

    if not df_existentes_origem.empty:

        df_comparacao = df_existentes_origem.merge(
            df_existentes,
            on=[
                "sales_order_id",
                "sales_order_detail_id"
            ],
            how="left",
            suffixes=("", "_dw")
        )

        df_comparacao["data_alteracao_origem"] = pd.to_datetime(
            df_comparacao["data_alteracao_origem"]
        )

        df_comparacao["data_alteracao_origem_dw"] = pd.to_datetime(
            df_comparacao["data_alteracao_origem_dw"]
        )

        df_alteradas = df_comparacao[
            df_comparacao["data_alteracao_origem"]
            >
            df_comparacao["data_alteracao_origem_dw"]
        ].copy()

    else:

        df_alteradas = df_vendas.iloc[
            0:0
        ].copy()


    # ======================================
    # 11.5 COLUNAS DA FATO
    # ======================================

    colunas_fato = [
        "data_key",
        "produto_key",
        "cliente_key",
        "territorio_key",
        "sales_order_id",
        "sales_order_detail_id",
        "quantidade",
        "preco_unitario",
        "desconto_percentual",
        "valor_bruto",
        "valor_desconto",
        "receita",
        "custo_total",
        "margem_bruta",
        "data_alteracao_origem"
    ]

    if not df_alteradas.empty:
        df_alteradas = df_alteradas[
            colunas_fato
        ].copy()


    # ======================================
    # 12. CARGA
    # ======================================

    print(
        f"\nVendas novas: "
        f"{len(df_novas)}"
    )

    print(
        f"Vendas existentes: "
        f"{len(df_vendas) - len(df_novas)}"
    )


    if not df_novas.empty or not df_alteradas.empty:

        carregar_fato_vendas(
            df_novas,
            df_alteradas
        )

    else:

        print(
            "Nenhuma venda nova ou alterada para carregar."
        )


# ==========================================
# EXECUÇÃO
# ==========================================

if __name__ == "__main__":

    data_inicio = datetime(
        2011,
        6,
        1
    )

    data_fim = datetime(
        2011,
        6,
        30,
        23,
        59,
        59
    )


    executar_mes(
        data_inicio,
        data_fim
    )

    print("\n========================================")
    print("SIMULAÇÃO DO MÊS FINALIZADA")
    print("========================================")