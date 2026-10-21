-- ============================================================
-- Projeto OLAP e ETL - AdventureWorks2016
-- Consultas dos 10 KPIs do Data Warehouse
-- Modelo: dw.fato_venda + dimensões
-- ============================================================


-- ============================================================
-- KPI 1 - RECEITA DE VENDAS
-- Soma o valor total das vendas após os descontos.
-- Fonte no DW: dw.fato_venda.valor_receita
-- ============================================================

SELECT
    SUM(valor_receita) AS receita_vendas
FROM dw.fato_venda;


-- ============================================================
-- KPI 2 - QUANTIDADE TOTAL DE ITENS VENDIDOS
-- Soma a quantidade de unidades vendidas.
-- ============================================================

SELECT
    SUM(quantidade) AS quantidade_itens_vendidos
FROM dw.fato_venda;


-- ============================================================
-- KPI 3 - QUANTIDADE DE PEDIDOS
-- Conta os pedidos distintos.
-- sales_order_id é mantido na fato como dimensão degenerada.
-- ============================================================

SELECT
    COUNT(DISTINCT sales_order_id) AS quantidade_pedidos
FROM dw.fato_venda;


-- ============================================================
-- KPI 4 - TICKET MÉDIO
-- Calcula a receita média por pedido.
--
-- Fórmula:
-- Receita total / Quantidade de pedidos
-- ============================================================

SELECT
    SUM(valor_receita)
    / NULLIF(COUNT(DISTINCT sales_order_id), 0) AS ticket_medio
FROM dw.fato_venda;


-- ============================================================
-- KPI 5 - DESCONTO TOTAL CONCEDIDO
-- Soma o valor monetário dos descontos concedidos.
-- ============================================================

SELECT
    SUM(valor_desconto) AS desconto_total
FROM dw.fato_venda;


-- ============================================================
-- KPI 6 - PERCENTUAL DE DESCONTO SOBRE O VALOR BRUTO
-- Mede quanto do valor bruto total foi concedido em descontos.
--
-- Fórmula:
-- (Desconto total / Valor bruto total) * 100
--
-- Observação:
-- O cálculo é ponderado pelo valor das vendas e, portanto,
-- representa melhor o impacto financeiro global dos descontos
-- do que uma média simples dos percentuais por item.
-- ============================================================

SELECT
    (
        SUM(valor_desconto)
        / NULLIF(SUM(valor_bruto_item), 0)
    ) * 100 AS percentual_desconto_sobre_valor_bruto
FROM dw.fato_venda;


-- ============================================================
-- KPI 7 - MARGEM BRUTA
-- Soma a margem bruta das vendas.
--
-- Regra previamente aplicada pela ETL:
-- margem_bruta = valor_receita - custo_total
-- ============================================================

SELECT
    SUM(margem_bruta) AS margem_bruta
FROM dw.fato_venda;


-- ============================================================
-- KPI 8 - MARGEM BRUTA PERCENTUAL
-- Mede a margem bruta em relação à receita.
--
-- Fórmula:
-- (Margem bruta / Receita) * 100
-- ============================================================

SELECT
    (
        SUM(margem_bruta)
        / NULLIF(SUM(valor_receita), 0)
    ) * 100 AS margem_bruta_percentual
FROM dw.fato_venda;


-- ============================================================
-- KPI 9 - RECEITA POR PRODUTO
-- Mostra a receita gerada por produto.
-- A consulta utiliza a surrogate key sk_produto.
-- ============================================================

SELECT
    p.sk_produto,
    p.product_id_oltp,
    p.nome_produto,
    p.nome_categoria,
    p.nome_subcategoria,
    SUM(f.valor_receita) AS receita_produto
FROM dw.fato_venda AS f
INNER JOIN dw.dim_produto AS p
    ON f.sk_produto = p.sk_produto
GROUP BY
    p.sk_produto,
    p.product_id_oltp,
    p.nome_produto,
    p.nome_categoria,
    p.nome_subcategoria
ORDER BY
    receita_produto DESC;


-- ============================================================
-- KPI 10 - RECEITA POR TERRITÓRIO
-- Mostra a receita gerada por território de vendas.
-- A consulta utiliza a surrogate key sk_territorio.
-- ============================================================

SELECT
    t.sk_territorio,
    t.territory_id_oltp,
    t.nome_territorio,
    t.codigo_pais,
    t.grupo_territorial,
    SUM(f.valor_receita) AS receita_territorio
FROM dw.fato_venda AS f
INNER JOIN dw.dim_territorio AS t
    ON f.sk_territorio = t.sk_territorio
GROUP BY
    t.sk_territorio,
    t.territory_id_oltp,
    t.nome_territorio,
    t.codigo_pais,
    t.grupo_territorial
ORDER BY
    receita_territorio DESC;
