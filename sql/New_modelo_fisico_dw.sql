-- ============================================================
-- DATA WAREHOUSE - ADVENTUREWORKS 2016
-- Projeto OLAP / ETL
-- ============================================================


-- ============================================================
-- 1. CRIAÇÃO DO SCHEMA
-- ============================================================

CREATE SCHEMA IF NOT EXISTS dw;


-- ============================================================
-- 2. DIMENSÃO DATA
-- ============================================================

CREATE TABLE IF NOT EXISTS dw.dim_data (
    data_key INTEGER PRIMARY KEY,
    data DATE NOT NULL,
    dia INTEGER NOT NULL,
    mes INTEGER NOT NULL,
    nome_mes VARCHAR(20) NOT NULL,
    trimestre INTEGER NOT NULL,
    ano INTEGER NOT NULL,
    dia_semana INTEGER NOT NULL,
    nome_dia_semana VARCHAR(20) NOT NULL
);


-- ============================================================
-- 3. DIMENSÃO PRODUTO
-- ============================================================

CREATE TABLE IF NOT EXISTS dw.dim_produto (
    produto_key INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_id INTEGER NOT NULL UNIQUE,
    nome_produto VARCHAR(200),
    product_number VARCHAR(50),
    cor VARCHAR(50),
    tamanho VARCHAR(50),
    nome_subcategoria VARCHAR(100),
    nome_categoria VARCHAR(100),
    preco_lista NUMERIC(18,4),
    data_alteracao_origem TIMESTAMP
);


-- ============================================================
-- 4. DIMENSÃO CLIENTE
-- ============================================================

CREATE TABLE IF NOT EXISTS dw.dim_cliente (
    cliente_key INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id INTEGER NOT NULL UNIQUE,
    nome_cliente VARCHAR(200),
    tipo_cliente VARCHAR(50),
    territorio_id INTEGER,
    data_alteracao_origem TIMESTAMP
);


-- ============================================================
-- 5. DIMENSÃO TERRITÓRIO
-- ============================================================

CREATE TABLE IF NOT EXISTS dw.dim_territorio (
    territorio_key INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    territory_id INTEGER NOT NULL UNIQUE,

    nome_territorio VARCHAR(100),

    pais VARCHAR(100),

    grupo VARCHAR(100),

    data_alteracao_origem TIMESTAMP
);


-- ============================================================
-- 6. TABELA FATO VENDAS
-- ============================================================

CREATE TABLE IF NOT EXISTS dw.fato_vendas (
    venda_key INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    -- Chaves das dimensões
    data_key INTEGER NOT NULL,
    produto_key INTEGER NOT NULL,
    cliente_key INTEGER NOT NULL,
    territorio_key INTEGER NOT NULL,

    -- Chaves da origem
    sales_order_id INTEGER NOT NULL,
    sales_order_detail_id INTEGER NOT NULL,

    -- Quantidades
    quantidade INTEGER NOT NULL,

    -- Valores
    preco_unitario NUMERIC(18,4) NOT NULL,
    desconto_percentual NUMERIC(18,4) NOT NULL,
    valor_bruto NUMERIC(18,4) NOT NULL,
    valor_desconto NUMERIC(18,4) NOT NULL,
    receita NUMERIC(18,4) NOT NULL,

    -- Custos e margem
    custo_total NUMERIC(18,4),
    margem_bruta NUMERIC(18,4),

    -- Controle de alteração da origem
    data_alteracao_origem TIMESTAMP,

    -- Evita duplicidade de uma linha da venda
    CONSTRAINT uk_fato_venda
        UNIQUE (
            sales_order_id,
            sales_order_detail_id
        )
);


-- ============================================================
-- 7. FOREIGN KEYS
-- ============================================================

ALTER TABLE dw.fato_vendas
DROP CONSTRAINT IF EXISTS fk_fato_data;

ALTER TABLE dw.fato_vendas
ADD CONSTRAINT fk_fato_data
FOREIGN KEY (data_key)
REFERENCES dw.dim_data(data_key);


ALTER TABLE dw.fato_vendas
DROP CONSTRAINT IF EXISTS fk_fato_produto;

ALTER TABLE dw.fato_vendas
ADD CONSTRAINT fk_fato_produto
FOREIGN KEY (produto_key)
REFERENCES dw.dim_produto(produto_key);


ALTER TABLE dw.fato_vendas
DROP CONSTRAINT IF EXISTS fk_fato_cliente;

ALTER TABLE dw.fato_vendas
ADD CONSTRAINT fk_fato_cliente
FOREIGN KEY (cliente_key)
REFERENCES dw.dim_cliente(cliente_key);


ALTER TABLE dw.fato_vendas
DROP CONSTRAINT IF EXISTS fk_fato_territorio;

ALTER TABLE dw.fato_vendas
ADD CONSTRAINT fk_fato_territorio
FOREIGN KEY (territorio_key)
REFERENCES dw.dim_territorio(territorio_key);


-- ============================================================
-- 8. CONTROLE DO ETL
-- ============================================================

CREATE TABLE IF NOT EXISTS dw.controle_etl (
    processo VARCHAR(100) PRIMARY KEY,
    ultima_execucao TIMESTAMP NOT NULL
);


-- ============================================================
-- 9. CONTROLES INICIAIS DO ETL
-- ============================================================

INSERT INTO dw.controle_etl (
    processo,
    ultima_execucao
)
VALUES
    ('dim_produto', '1900-01-01'),
    ('dim_cliente', '1900-01-01'),
    ('dim_territorio', '1900-01-01'),
    ('dim_data', '1900-01-01'),
    ('fato_vendas', '1900-01-01')
ON CONFLICT (processo)
DO NOTHING;


-- ============================================================
-- 10. ÍNDICES
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_fato_data
ON dw.fato_vendas(data_key);

CREATE INDEX IF NOT EXISTS idx_fato_produto
ON dw.fato_vendas(produto_key);

CREATE INDEX IF NOT EXISTS idx_fato_cliente
ON dw.fato_vendas(cliente_key);

CREATE INDEX IF NOT EXISTS idx_fato_territorio
ON dw.fato_vendas(territorio_key);

CREATE INDEX IF NOT EXISTS idx_fato_pedido
ON dw.fato_vendas(sales_order_id);

CREATE INDEX IF NOT EXISTS idx_fato_data_alteracao
ON dw.fato_vendas(data_alteracao_origem);

CREATE INDEX IF NOT EXISTS idx_produto_alteracao
ON dw.dim_produto(data_alteracao_origem);

CREATE INDEX IF NOT EXISTS idx_cliente_alteracao
ON dw.dim_cliente(data_alteracao_origem);

CREATE INDEX IF NOT EXISTS idx_territorio_alteracao
ON dw.dim_territorio(data_alteracao_origem);


-- ============================================================
-- 11. VERIFICAÇÃO DA ESTRUTURA
-- ============================================================

SELECT
    table_schema,
    table_name
FROM information_schema.tables
WHERE table_schema = 'dw'
ORDER BY table_name;


-- ============================================================
-- 12. VERIFICAÇÃO DA DIMENSÃO TERRITÓRIO
-- ============================================================

SELECT
    column_name,
    data_type
FROM information_schema.columns
WHERE table_schema = 'dw'
  AND table_name = 'dim_territorio'
ORDER BY ordinal_position;