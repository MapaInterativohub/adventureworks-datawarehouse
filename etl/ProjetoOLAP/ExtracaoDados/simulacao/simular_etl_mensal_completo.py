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


# ============================================================
# CONFIGURAÇÃO
# ============================================================

DATA_INICIO = datetime(2011, 6, 1)
DATA_FIM = datetime(2014, 1, 31, 23, 59, 59)


# ============================================================
# GERAR PERÍODOS MENSAIS
# ============================================================

def gerar_periodos_mensais(
    data_inicio,
    data_fim
):

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


# ============================================================
# EXTRAIR VENDAS DO MÊS
# ============================================================

def extrair_vendas_mes(
    data_inicio,
    data_fim
):

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

            sod.OrderQty * sod.UnitPrice
                AS ValorBruto,

            sod.OrderQty
                * sod.UnitPrice
                * sod.UnitPriceDiscount
                AS ValorDesconto,

            sod.LineTotal
                AS Receita,

            pch.StandardCost,

            sod.OrderQty
                * pch.StandardCost
                AS CustoTotal,

            CASE
                WHEN soh.ModifiedDate > sod.ModifiedDate
                    THEN soh.ModifiedDate
                ELSE sod.ModifiedDate
            END AS ModifiedDate

        FROM Sales.SalesOrderDetail sod

        INNER JOIN Sales.SalesOrderHeader soh
            ON sod.SalesOrderID =
               soh.SalesOrderID

        OUTER APPLY
        (
            SELECT TOP 1

                pch.StandardCost

            FROM Production.ProductCostHistory pch

            WHERE
                pch.ProductID =
                sod.ProductID

                AND pch.StartDate <=
                    soh.OrderDate

                AND
                (
                    pch.EndDate IS NULL

                    OR pch.EndDate >=
                       soh.OrderDate
                )

            ORDER BY
                pch.StartDate DESC

        ) pch

        WHERE
            soh.OrderDate >= ?

            AND soh.OrderDate <= ?

        ORDER BY
            soh.OrderDate,

            sod.SalesOrderID,

            sod.SalesOrderDetailID
    """

    conexao = conectar_sql_server()

    df = pd.read_sql(
        sql,
        conexao,
        params=(
            data_inicio,
            data_fim
        )
    )

    conexao.close()

    return df


# ============================================================
# SIMULAR ALTERAÇÃO
# ============================================================

def simular_alteracao_venda(
    df_vendas,
    executar=False
):

    """
    Simula uma alteração em memória.

    O AdventureWorks não é alterado.

    A alteração só será feita quando
    executar=True.
    """

    if not executar:
        return df_vendas

    if df_vendas.empty:
        return df_vendas

    df = df_vendas.copy()

    indice = df.index[0]

    # --------------------------------------------------------
    # Alterar desconto
    # --------------------------------------------------------

    df.loc[
        indice,
        "UnitPriceDiscount"
    ] = 0.10

    # --------------------------------------------------------
    # Recalcular valor bruto
    # --------------------------------------------------------

    df.loc[
        indice,
        "ValorBruto"
    ] = (
        df.loc[indice, "OrderQty"]
        *
        df.loc[indice, "UnitPrice"]
    )

    # --------------------------------------------------------
    # Recalcular desconto
    # --------------------------------------------------------

    df.loc[
        indice,
        "ValorDesconto"
    ] = (
        df.loc[indice, "ValorBruto"]
        *
        df.loc[indice, "UnitPriceDiscount"]
    )

    # --------------------------------------------------------
    # Recalcular receita
    # --------------------------------------------------------

    df.loc[
        indice,
        "Receita"
    ] = (
        df.loc[indice, "ValorBruto"]
        -
        df.loc[indice, "ValorDesconto"]
    )

    # --------------------------------------------------------
    # Simular nova data de alteração
    # --------------------------------------------------------

    df.loc[
        indice,
        "ModifiedDate"
    ] = pd.Timestamp.now().floor("s")

    print()
    print("*** ALTERAÇÃO SIMULADA ***")

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


# ============================================================
# GARANTIR DATAS NO DW
# ============================================================

def carregar_datas_necessarias(
    data_inicio,
    data_fim
):

    print()
    print("Verificando dimensão de datas...")

    # --------------------------------------------------------
    # Extrair calendário original
    # --------------------------------------------------------

    df_datas = extrair_dim_data()

    # --------------------------------------------------------
    # Transformar
    # --------------------------------------------------------

    df_datas = transformar_dim_data(
        df_datas
    )

    # --------------------------------------------------------
    # Filtrar período
    # --------------------------------------------------------

    df_datas = df_datas[
        (
            df_datas["data"]
            >= data_inicio.date()
        )
        &
        (
            df_datas["data"]
            <= data_fim.date()
        )
    ].copy()

    if df_datas.empty:

        print(
            "Nenhuma data encontrada."
        )

        return

    # --------------------------------------------------------
    # Buscar datas existentes
    # --------------------------------------------------------

    conexao = conectar_postgres()

    cursor = conexao.cursor()

    cursor.execute(
        """
        SELECT
            data_key

        FROM dw.dim_data

        WHERE
            data >= %s
            AND data <= %s
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

    # --------------------------------------------------------
    # Identificar novas
    # --------------------------------------------------------

    df_datas_novas = df_datas[
        ~df_datas["data_key"].isin(
            datas_existentes
        )
    ].copy()

    print(
        f"Datas necessárias: "
        f"{len(df_datas)}"
    )

    print(
        f"Datas novas: "
        f"{len(df_datas_novas)}"
    )

    # --------------------------------------------------------
    # Carregar
    # --------------------------------------------------------

    if not df_datas_novas.empty:

        carregar_dim_data(
            df_datas_novas
        )

        print(
            "Novas datas carregadas."
        )

    else:

        print(
            "As datas já existem no DW."
        )


# ============================================================
# PROCESSAR PRODUTOS
# ============================================================

def processar_produtos(
    df_vendas
):

    produtos_necessarios = set(
        df_vendas["ProductID"]
        .dropna()
    )

    if not produtos_necessarios:
        return

    # --------------------------------------------------------
    # Buscar produtos no DW
    # --------------------------------------------------------

    conexao = conectar_postgres()

    df_dw = pd.read_sql(
        """
        SELECT
            product_id

        FROM dw.dim_produto
        """,
        conexao
    )

    conexao.close()

    produtos_dw = set(
        df_dw["product_id"]
        .dropna()
    )

    produtos_faltantes = (
        produtos_necessarios
        - produtos_dw
    )

    print(
        f"Produtos necessários: "
        f"{len(produtos_necessarios)}"
    )

    print(
        f"Produtos faltantes: "
        f"{len(produtos_faltantes)}"
    )

    if not produtos_faltantes:

        print(
            "Todos os produtos já estão no DW."
        )

        return

    # --------------------------------------------------------
    # Buscar produtos na origem
    # --------------------------------------------------------

    df = extrair_dim_produto()

    df = df[
        df["ProductID"].isin(
            produtos_faltantes
        )
    ].copy()

    if df.empty:
        return

    print(
        f"Produtos carregados: "
        f"{len(df)}"
    )

    # --------------------------------------------------------
    # IMPORTANTE:
    # carregar_dim_produto recebe
    # dados no formato ORIGINAL.
    # --------------------------------------------------------

    df_vazio = (
        df.iloc[0:0]
        .copy()
    )

    carregar_dim_produto(
        df,
        df_vazio
    )
    print(f"Produtos carregados: {len(df)}")

# ============================================================
# PROCESSAR CLIENTES
# ============================================================

def processar_clientes(df_vendas):
    """
    Garante que todos os clientes presentes nas vendas
    do mês estejam carregados na dimensão de clientes.

    IMPORTANTE:
    O carregar_dim_cliente() recebe os dados no formato
    original da origem, portanto NÃO devemos passar
    df_transformado para ele.
    """

    clientes_necessarios = (
        df_vendas["CustomerID"]
        .dropna()
        .astype(int)
        .unique()
        .tolist()
    )

    print(f"Clientes necessários: {len(clientes_necessarios)}")

    if not clientes_necessarios:
        print("Nenhum cliente necessário.")
        return

    conexao = conectar_postgres()

    df_dw = pd.read_sql(
        """
        SELECT customer_id
        FROM dw.dim_cliente
        """,
        conexao
    )

    conexao.close()

    clientes_existentes = set(
        df_dw["customer_id"].astype(int).tolist()
    )

    clientes_faltantes = [
        cliente_id
        for cliente_id in clientes_necessarios
        if cliente_id not in clientes_existentes
    ]

    print(f"Clientes faltantes: {len(clientes_faltantes)}")

    if not clientes_faltantes:
        print("Todos os clientes já estão no DW.")
        return

    # Busca os clientes diretamente na origem
    conexao = conectar_sql_server()

    placeholders = ",".join(
        ["?"] * len(clientes_faltantes)
    )

    sql = f"""
        SELECT
            c.CustomerID,
            c.PersonID,
            c.StoreID,
            c.TerritoryID,
            c.ModifiedDate,

            CASE
                WHEN c.StoreID IS NOT NULL THEN 'Empresa'
                WHEN c.PersonID IS NOT NULL THEN 'Pessoa'
                ELSE 'Outro'
            END AS TipoCliente,

            COALESCE(
                p.FirstName + ' ' + p.LastName,
                s.Name,
                'Cliente sem nome'
            ) AS NomeCliente

        FROM Sales.Customer c

        LEFT JOIN Person.Person p
            ON c.PersonID = p.BusinessEntityID

        LEFT JOIN Sales.Store s
            ON c.StoreID = s.BusinessEntityID

        WHERE c.CustomerID IN ({placeholders})
    """

    df = pd.read_sql(
        sql,
        conexao,
        params=clientes_faltantes
    )

    conexao.close()

    if df.empty:
        print("Nenhum cliente encontrado na origem.")
        return

    print(f"Clientes encontrados na origem: {len(df)}")

    # NÃO transformar aqui.
    # O loader espera CustomerID, PersonID, StoreID, etc.
    df_vazio = df.iloc[0:0].copy()

    carregar_dim_cliente(
        df,
        df_vazio
    )

    print(f"Clientes carregados: {len(df)}")

# ============================================================
# PROCESSAR TERRITÓRIOS
# ============================================================

def processar_territorios(
    df_vendas
):

    territorios_necessarios = set(
        df_vendas["TerritoryID"]
        .dropna()
    )

    if not territorios_necessarios:
        return

    # --------------------------------------------------------
    # Buscar no DW
    # --------------------------------------------------------

    conexao = conectar_postgres()

    df_dw = pd.read_sql(
        """
        SELECT
            territory_id

        FROM dw.dim_territorio
        """,
        conexao
    )

    conexao.close()

    territorios_dw = set(
        df_dw["territory_id"]
        .dropna()
    )

    territorios_faltantes = (
        territorios_necessarios
        - territorios_dw
    )

    print(
        f"Territórios necessários: "
        f"{len(territorios_necessarios)}"
    )

    print(
        f"Territórios faltantes: "
        f"{len(territorios_faltantes)}"
    )

    if not territorios_faltantes:

        print(
            "Todos os territórios já estão no DW."
        )

        return

    # --------------------------------------------------------
    # Extrair
    # --------------------------------------------------------

    df = extrair_dim_territorio()

    df = df[
        df["TerritoryID"].isin(
            territorios_faltantes
        )
    ].copy()

    if df.empty:
        return

    print(
        f"Territórios carregados: "
        f"{len(df)}"
    )

    df_transformado = transformar_dim_territorio(
        df
    )

    df_vazio = (
        df_transformado
        .iloc[0:0]
        .copy()
    )

    carregar_dim_territorio(
        df,
        df_vazio
    )

    print(f"Territórios carregados: {len(df)}")


# ============================================================
# PROCESSAR DIMENSÕES
# ============================================================

def processar_dimensoes(
    df_vendas,
    data_inicio,
    data_fim
):

    print()
    print("Processando datas...")

    carregar_datas_necessarias(
        data_inicio,
        data_fim
    )

    print()
    print("Processando produtos...")

    processar_produtos(
        df_vendas
    )

    print()
    print("Processando clientes...")

    processar_clientes(
        df_vendas
    )

    print()
    print("Processando territórios...")

    processar_territorios(
        df_vendas
    )


# ============================================================
# PROCESSAR FATO
# ============================================================

def processar_fato(
    df_vendas
):

    # --------------------------------------------------------
    # Buscar chaves
    # --------------------------------------------------------

    print()
    print(
        "Buscando chaves das dimensões..."
    )

    (
        df_produto,
        df_cliente,
        df_territorio,
        df_data
    ) = buscar_chaves_dimensoes()

    # --------------------------------------------------------
    # Transformar
    # --------------------------------------------------------

    print()
    print(
        "Transformando vendas..."
    )

    df_transformado = transformar_fato_vendas(
        df_vendas,
        df_produto,
        df_cliente,
        df_territorio,
        df_data
    )

    # --------------------------------------------------------
    # Validar chaves
    # --------------------------------------------------------

    erros = False

    if df_transformado[
        "produto_key"
    ].isna().any():

        print(
            "ERRO: existem produtos sem chave."
        )

        erros = True

    if df_transformado[
        "cliente_key"
    ].isna().any():

        print(
            "ERRO: existem clientes sem chave."
        )

        erros = True

    if df_transformado[
        "territorio_key"
    ].isna().any():

        print(
            "ERRO: existem territórios sem chave."
        )

        erros = True

    if df_transformado[
        "data_key"
    ].isna().any():

        print(
            "ERRO: existem datas sem chave."
        )

        erros = True

    if erros:

        print()
        print(
            "Carga da fato cancelada."
        )

        return 0, 0

    # --------------------------------------------------------
    # Buscar vendas existentes
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Se DW vazio
    # --------------------------------------------------------

    if df_existentes.empty:

        df_novas = (
            df_transformado
            .copy()
        )

        df_alteradas = (
            df_transformado
            .iloc[0:0]
            .copy()
        )

    else:

        # ----------------------------------------------------
        # Chaves
        # ----------------------------------------------------

        chaves_dw = set(
            zip(
                df_existentes[
                    "sales_order_id"
                ],
                df_existentes[
                    "sales_order_detail_id"
                ]
            )
        )

        chaves_origem = list(
            zip(
                df_transformado[
                    "sales_order_id"
                ],
                df_transformado[
                    "sales_order_detail_id"
                ]
            )
        )

        # ----------------------------------------------------
        # NOVAS
        # ----------------------------------------------------

        df_novas = df_transformado[
            [
                chave not in chaves_dw
                for chave in chaves_origem
            ]
        ].copy()

        # ----------------------------------------------------
        # EXISTENTES
        # ----------------------------------------------------

        df_existentes_origem = (
            df_transformado[
                [
                    chave in chaves_dw
                    for chave in chaves_origem
                ]
            ]
            .copy()
        )

        # ----------------------------------------------------
        # ALTERADAS
        # ----------------------------------------------------

        if not df_existentes_origem.empty:

            df_comparacao = (
                df_existentes_origem.merge(
                    df_existentes,

                    on=[
                        "sales_order_id",
                        "sales_order_detail_id"
                    ],

                    how="left",

                    suffixes=(
                        "",
                        "_dw"
                    )
                )
            )

            df_comparacao[
                "data_alteracao_origem"
            ] = pd.to_datetime(
                df_comparacao[
                    "data_alteracao_origem"
                ]
            )

            df_comparacao[
                "data_alteracao_origem_dw"
            ] = pd.to_datetime(
                df_comparacao[
                    "data_alteracao_origem_dw"
                ]
            )

            df_alteradas = (
                df_comparacao[
                    df_comparacao[
                        "data_alteracao_origem"
                    ]
                    >
                    df_comparacao[
                        "data_alteracao_origem_dw"
                    ]
                ]
                .copy()
            )

        else:

            df_alteradas = (
                df_transformado
                .iloc[0:0]
                .copy()
            )

    # --------------------------------------------------------
    # Colunas da fato
    # --------------------------------------------------------

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

        df_alteradas = (
            df_alteradas[
                colunas_fato
            ]
            .copy()
        )

    # --------------------------------------------------------
    # Resultado
    # --------------------------------------------------------

    print()
    print(
        f"Vendas novas: "
        f"{len(df_novas)}"
    )

    print(
        f"Vendas existentes: "
        f"{len(df_transformado) - len(df_novas)}"
    )

    print(
        f"Vendas alteradas: "
        f"{len(df_alteradas)}"
    )

    # --------------------------------------------------------
    # Carregar
    # --------------------------------------------------------

    if (
        not df_novas.empty
        or
        not df_alteradas.empty
    ):

        carregar_fato_vendas(
            df_novas,
            df_alteradas
        )

    else:

        print(
            "Nenhuma venda nova ou alterada para carregar."
        )

    return (
        len(df_novas),
        len(df_alteradas)
    )


# ============================================================
# EXECUTAR UM MÊS
# ============================================================

def executar_mes(
    data_inicio,
    data_fim
):

    print()
    print("=" * 70)

    print(
        f"PROCESSANDO: "
        f"{data_inicio.strftime('%m/%Y')}"
    )

    print("=" * 70)

    # --------------------------------------------------------
    # 1. EXTRAÇÃO
    # --------------------------------------------------------

    print()
    print(
        "Extraindo vendas..."
    )

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

        return 0, 0

    # --------------------------------------------------------
    # 2. DIMENSÕES
    # --------------------------------------------------------

    processar_dimensoes(
        df_vendas,
        data_inicio,
        data_fim
    )

    # --------------------------------------------------------
    # 3. FATO
    # --------------------------------------------------------

    novas, alteradas = processar_fato(
        df_vendas
    )

    print()
    print(
        f"Resumo {data_inicio.strftime('%m/%Y')}:"
    )

    print(
        f"  Extraídas: {len(df_vendas)}"
    )

    print(
        f"  Inseridas: {novas}"
    )

    print(
        f"  Atualizadas: {alteradas}"
    )

    return novas, alteradas


# ============================================================
# EXECUÇÃO PRINCIPAL
# ============================================================

def main():

    print()
    print("=" * 70)
    print(
        "SIMULAÇÃO COMPLETA DO ETL MENSAL"
    )
    print("=" * 70)
    print()

    # --------------------------------------------------------
    # Gerar meses
    # --------------------------------------------------------

    periodos = gerar_periodos_mensais(
        DATA_INICIO,
        DATA_FIM
    )

    print(
        f"Períodos gerados: "
        f"{len(periodos)}"
    )

    print(
        f"Início: "
        f"{DATA_INICIO.strftime('%d/%m/%Y')}"
    )

    print(
        f"Fim: "
        f"{DATA_FIM.strftime('%d/%m/%Y')}"
    )

    # --------------------------------------------------------
    # Contadores
    # --------------------------------------------------------

    total_extraidas = 0

    total_inseridas = 0

    total_atualizadas = 0

    meses_processados = 0

    # ========================================================
    # LOOP
    # ========================================================

    for periodo in periodos:

        inicio = periodo["inicio"]

        fim = periodo["fim"]

        novas, alteradas = executar_mes(
            inicio,
            fim
        )

        # ----------------------------------------------------
        # Reextrair somente para contabilização
        # ----------------------------------------------------

        df_mes = extrair_vendas_mes(
            inicio,
            fim
        )

        total_extraidas += len(
            df_mes
        )

        total_inseridas += novas

        total_atualizadas += alteradas

        meses_processados += 1

    # ========================================================
    # RESULTADO FINAL
    # ========================================================

    print()
    print("=" * 70)
    print(
        "SIMULAÇÃO ETL FINALIZADA"
    )
    print("=" * 70)

    print()

    print(
        f"Meses processados: "
        f"{meses_processados}"
    )

    print(
        f"Total de vendas extraídas: "
        f"{total_extraidas}"
    )

    print(
        f"Total de vendas inseridas: "
        f"{total_inseridas}"
    )

    print(
        f"Total de vendas atualizadas: "
        f"{total_atualizadas}"
    )

    print()
    print("=" * 70)


# ============================================================
# INICIAR
# ============================================================

if __name__ == "__main__":
    main()