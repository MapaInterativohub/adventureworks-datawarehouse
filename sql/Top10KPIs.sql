-- ============================================================
-- KPI 1 - RECEITA DE VENDAS
-- Soma o valor total das vendas realizadas.
-- ============================================================

SELECT
    SUM(receita) AS receita_vendas
FROM dw.fato_vendas;


-- ============================================================
-- KPI 2 - QUANTIDADE TOTAL DE ITENS VENDIDOS
-- Soma a quantidade de produtos vendidos.
-- ============================================================

SELECT
    SUM(quantidade) AS quantidade_itens_vendidos
FROM dw.fato_vendas;


-- ============================================================
-- KPI 3 - QUANTIDADE DE PEDIDOS
-- Conta a quantidade de pedidos distintos realizados.
-- ============================================================

SELECT
    COUNT(DISTINCT sales_order_id) AS quantidade_pedidos
FROM dw.fato_vendas;


-- ============================================================
-- KPI 4 - TICKET MÉDIO
-- Calcula a receita média por pedido.
-- Fórmula:
-- Receita total / Quantidade de pedidos
-- ============================================================

SELECT
    SUM(receita) /
    NULLIF(COUNT(DISTINCT sales_order_id), 0) AS ticket_medio
FROM dw.fato_vendas;


-- ============================================================
-- KPI 5 - DESCONTO TOTAL CONCEDIDO
-- Soma o valor total dos descontos concedidos nas vendas.
-- ============================================================

SELECT
    SUM(valor_desconto) AS desconto_total
FROM dw.fato_vendas;


-- ============================================================
-- KPI 6 - PERCENTUAL MÉDIO DE DESCONTO
-- Calcula o percentual de desconto em relação ao valor bruto.
-- Fórmula:
-- (Desconto total / Valor bruto total) * 100
-- ============================================================

SELECT
    (
        SUM(valor_desconto) /
        NULLIF(SUM(valor_bruto), 0)
    ) * 100 AS percentual_medio_desconto
FROM dw.fato_vendas;


-- ============================================================
-- KPI 7 - MARGEM BRUTA
-- Calcula o valor total da margem bruta das vendas.
-- Fórmula:
-- Receita - Custo total
-- ============================================================

SELECT
    SUM(margem_bruta) AS margem_bruta
FROM dw.fato_vendas;


-- ============================================================
-- KPI 8 - MARGEM BRUTA PERCENTUAL
-- Calcula o percentual da margem bruta em relação à receita.
-- Fórmula:
-- (Margem bruta / Receita) * 100
-- ============================================================

SELECT
    (
        SUM(margem_bruta) /
        NULLIF(SUM(receita), 0)
    ) * 100 AS margem_bruta_percentual
FROM dw.fato_vendas;


-- ============================================================
-- KPI 9 - RECEITA POR PRODUTO
-- Mostra quanto cada produto gerou de receita.
-- Os produtos são ordenados da maior para a menor receita.
-- ============================================================

SELECT
    p.produto_key,
    p.product_id,
    p.nome_produto,
    p.nome_categoria,
    p.nome_subcategoria,
    SUM(f.receita) AS receita
FROM dw.fato_vendas f
INNER JOIN dw.dim_produto p
    ON f.produto_key = p.produto_key
GROUP BY
    p.produto_key,
    p.product_id,
    p.nome_produto,
    p.nome_categoria,
    p.nome_subcategoria
ORDER BY
    receita DESC;


-- ============================================================
-- KPI 10 - RECEITA POR TERRITÓRIO
-- Mostra quanto cada território gerou de receita.
-- Os territórios são ordenados da maior para a menor receita.
-- ============================================================

SELECT
    t.territorio_key,
    t.territory_id,
    t.nome_territorio,
    t.pais,
    t.grupo,
    SUM(f.receita) AS receita
FROM dw.fato_vendas f
INNER JOIN dw.dim_territorio t
    ON f.territorio_key = t.territorio_key
GROUP BY
    t.territorio_key,
    t.territory_id,
    t.nome_territorio,
    t.pais,
    t.grupo
ORDER BY
    receita DESC;