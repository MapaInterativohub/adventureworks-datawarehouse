# Projeto de Análise e Fluxo de Dados — OLAP e ETL

Projeto acadêmico desenvolvido na disciplina **Projeto de Análise e Fluxo de Dados — OLAP e ETL**, com foco em **modelagem multidimensional, Data Warehouse, ETL incremental e indicadores analíticos** utilizando a base **AdventureWorks2016**.

O projeto utiliza o processo de **vendas** como escopo analítico principal. A partir da análise do banco OLTP AdventureWorks, foi definido um **Star Schema** com uma tabela fato no nível de item de pedido e três dimensões analíticas.

---

## Objetivo

Construir um Data Warehouse a partir do banco **AdventureWorks2016**, aplicando os seguintes conceitos:

- análise de um modelo OLTP;
- definição de indicadores de negócio;
- modelagem multidimensional em **Star Schema**;
- implementação do Data Warehouse no **PostgreSQL**;
- desenvolvimento de uma **ETL incremental em Python**;
- validação dos indicadores por meio de consultas SQL.

---

## Arquitetura do projeto

```text
AdventureWorks2016
SQL Server
      |
      | Extração
      v
Python
ETL Incremental
      |
      | Transformação
      v
Python
      |
      | Carga
      v
PostgreSQL
adventureworks_dw
      |
      v
Star Schema
      |
      v
Consultas SQL / KPIs
```

### Tecnologias

- **SQL Server** — banco de origem AdventureWorks2016
- **SQL Server Management Studio (SSMS)** — exploração do OLTP
- **Python** — ETL
- **PostgreSQL** — Data Warehouse
- **DBeaver** — administração e validação do PostgreSQL
- **Git / GitHub** — versionamento do projeto
- **Draw.io / diagrams.net** — diagrama do Star Schema

---

## Escopo analítico

Embora o AdventureWorks contenha diferentes áreas de negócio, como produção, compras, pessoas e recursos humanos, este projeto delimita o Data Warehouse ao processo de **vendas**.

A escolha foi realizada porque os indicadores definidos concentram-se em:

- receita;
- quantidade vendida;
- pedidos;
- descontos;
- custos;
- margens;
- produtos;
- territórios;
- análise temporal.

---

## Granularidade

A granularidade definida para a tabela fato é:

> **1 registro da `fato_venda` = 1 item de pedido de venda**

A principal origem transacional é:

```text
Sales.SalesOrderDetail
```

O pedido é identificado na fato por:

```text
sales_order_id
```

como uma **dimensão degenerada**.

O item é rastreado por:

```text
sales_order_detail_id
```

---

## Star Schema

O modelo multidimensional possui uma tabela fato e três dimensões:

```text
                     DIM_TEMPO
                         |
                         |
DIM_PRODUTO ------ FATO_VENDA ------ DIM_TERRITORIO
```

### `dw.fato_venda`

Representa os itens dos pedidos de venda.

Principais campos:

```text
sk_venda
sales_order_id
sales_order_detail_id

sk_tempo
sk_produto
sk_territorio

quantidade
preco_unitario
percentual_desconto_item
valor_receita

valor_bruto_item
valor_desconto
custo_unitario_aplicado
origem_custo
custo_total
margem_bruta
```

### `dw.dim_produto`

Consolida informações provenientes de:

```text
Production.Product
Production.ProductSubcategory
Production.ProductCategory
```

Principais atributos:

```text
sk_produto
product_id_oltp
nome_produto
numero_produto
cor
tamanho
nome_subcategoria
nome_categoria
preco_lista
```

A hierarquia analítica é:

```text
Categoria
   |
Subcategoria
   |
Produto
```

### `dw.dim_tempo`

Dimensão de calendário utilizada para análises temporais.

Principais atributos:

```text
sk_tempo
data_completa
dia
mes
nome_mes
trimestre
ano
dia_semana
nome_dia_semana
semana_ano
fim_de_semana
```

Intervalo inicial previsto:

```text
31/05/2011 até 30/06/2014
```

### `dw.dim_territorio`

Origem principal:

```text
Sales.SalesTerritory
```

Principais atributos:

```text
sk_territorio
territory_id_oltp
nome_territorio
codigo_pais
grupo_territorial
```

---

## Indicadores do projeto

Foram selecionados 10 KPIs para análise do processo de vendas.

1. **Receita de vendas**
2. **Quantidade total de itens vendidos**
3. **Quantidade de pedidos**
4. **Ticket médio**
5. **Desconto total concedido**
6. **Percentual médio de desconto**
7. **Margem bruta**
8. **Margem bruta percentual**
9. **Receita por produto**
10. **Receita por território**

### Ticket médio

A fórmula adotada no Data Warehouse é:

```text
SUM(valor_receita)
-------------------------------
COUNT(DISTINCT sales_order_id)
```

Essa decisão mantém o cálculo compatível com a granularidade de item da tabela fato.

---

## Regras de transformação

### Valor bruto do item

```text
valor_bruto_item =
quantidade * preco_unitario
```

### Valor do desconto

```text
valor_desconto =
quantidade
* preco_unitario
* percentual_desconto_item
```

### Valor da receita

```text
valor_receita =
Sales.SalesOrderDetail.LineTotal
```

### Custo

O custo do produto deve considerar a data da venda.

A ETL deverá:

1. procurar o custo vigente em `Production.ProductCostHistory`;
2. caso não exista custo histórico correspondente, utilizar `Production.Product.StandardCost` como fallback.

```text
ProductCostHistory.StandardCost
            |
            | se não encontrado
            v
Product.StandardCost
```

A origem será registrada na fato como:

```text
HISTORICO
FALLBACK_ATUAL
```

### Custo total

```text
custo_total =
quantidade * custo_unitario_aplicado
```

### Margem bruta

```text
margem_bruta =
valor_receita - custo_total
```

### Produto sem classificação

Produtos sem subcategoria ou categoria devem ser carregados como:

```text
Não classificado
```

### Membros técnicos

As dimensões Produto e Território possuem membro técnico:

```text
sk = -1
```

utilizado para registros não informados ou chaves dimensionais não resolvidas.

---

## ETL incremental

A ETL será implementada em **Python** e deverá processar apenas registros novos ou modificados.

O campo principal para controle incremental é:

```text
ModifiedDate
```

Tabelas relevantes:

```text
Sales.SalesOrderDetail
Sales.SalesOrderHeader

Production.Product
Production.ProductSubcategory
Production.ProductCategory
Production.ProductCostHistory

Sales.SalesTerritory
```

A estratégia incremental deverá considerar que alterações em tabelas complementares podem exigir reprocessamento de dados já carregados.

Exemplos:

- alteração em `SalesOrderHeader` pode mudar tempo ou território;
- alteração em `ProductCostHistory` pode alterar custo e margem;
- alteração em categoria ou subcategoria pode atualizar vários produtos.

A ETL deve ser **reexecutável sem gerar duplicidades**.

---

## Ordem de carga

A ordem recomendada é:

```text
1. DimTempo
2. DimProduto
3. DimTerritorio
4. FatoVenda
```

As dimensões devem ser carregadas antes da tabela fato para garantir a resolução das chaves substitutas.

---

## Modelo físico PostgreSQL

O banco do Data Warehouse é:

```text
adventureworks_dw
```

O schema utilizado é:

```text
dw
```

Estrutura:

```text
adventureworks_dw
└── dw
    ├── dim_tempo
    ├── dim_produto
    ├── dim_territorio
    └── fato_venda
```

O script de criação do modelo físico está em:

```text
sql/01_modelo_fisico_dw_postgresql.sql
```

O DDL contém:

- `PRIMARY KEY`;
- `FOREIGN KEY`;
- `NOT NULL`;
- `UNIQUE`;
- `CHECK`;
- valores padrão;
- membros técnicos;
- índices;
- comentários de documentação.

---

## Estrutura sugerida do repositório

```text
.
├── README.md
├── .gitignore
├── .env.example
├── requirements.txt
│
├── sql/
│   ├── 01_modelo_fisico_dw_postgresql.sql
│   ├── 02_validacoes_modelo_fisico.sql
│   ├── 03_validacoes_carga.sql
│   └── 04_kpis.sql
│
├── etl/
│   ├── main.py
│   ├── extract.py
│   ├── transform.py
│   └── load.py
│
└── docs/
    ├── star_schema/
    │   ├── star_schema.png
    │   └── star_schema.drawio
    │
    ├── dicionario_dados/
    └── relatorios/
```

---

## Configuração do ambiente

### 1. Criar ambiente Python

```bash
python -m venv .venv
```

### 2. Ativar o ambiente

Windows:

```bash
.venv\Scripts\activate
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

---

## Variáveis de ambiente

As credenciais não devem ser armazenadas diretamente no código.

Exemplo de `.env.example`:

```env
SQLSERVER_HOST=localhost
SQLSERVER_DATABASE=AdventureWorks2016
SQLSERVER_USER=
SQLSERVER_PASSWORD=

POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DATABASE=adventureworks_dw
POSTGRES_USER=postgres
POSTGRES_PASSWORD=
```

O arquivo real `.env` deve permanecer fora do Git.

---

## Criando o Data Warehouse

Após criar o banco PostgreSQL:

```sql
CREATE DATABASE adventureworks_dw;
```

execute:

```text
sql/01_modelo_fisico_dw_postgresql.sql
```

no banco `adventureworks_dw`.

Depois valide:

```sql
SELECT
    table_schema,
    table_name
FROM information_schema.tables
WHERE table_schema = 'dw'
ORDER BY table_name;
```

Resultado esperado:

```text
dw | dim_produto
dw | dim_tempo
dw | dim_territorio
dw | fato_venda
```

---

## Valores de referência para validação

Após a carga histórica completa, os seguintes valores podem ser usados como referência para conferência.

### Quantidades

```text
SalesOrderDetail / FatoVenda:
121.317 itens

DimProduto:
504 produtos + membro técnico -1

DimTempo:
1.127 dias de calendário
```

### Valores financeiros aproximados

```text
Valor bruto:
110.373.889,3134

Desconto total:
527.507,9262

Valor da receita:
109.846.381,399888
```

Esses valores devem ser comparados com os resultados obtidos após a ETL.

---

## Consultas dos KPIs

As consultas finais dos indicadores deverão ser mantidas em:

```text
sql/04_kpis.sql
```

Exemplos:

### Receita de vendas

```sql
SELECT
    SUM(valor_receita) AS receita_vendas
FROM dw.fato_venda;
```

### Quantidade de itens vendidos

```sql
SELECT
    SUM(quantidade) AS itens_vendidos
FROM dw.fato_venda;
```

### Quantidade de pedidos

```sql
SELECT
    COUNT(DISTINCT sales_order_id) AS quantidade_pedidos
FROM dw.fato_venda;
```

### Ticket médio

```sql
SELECT
    SUM(valor_receita)
    / NULLIF(COUNT(DISTINCT sales_order_id), 0)
        AS ticket_medio
FROM dw.fato_venda;
```

---

## Arquivos que não devem ser versionados

Não enviar para o GitHub:

```text
.env
*.backup
*.bak
.venv/
venv/
__pycache__/
*.pyc
```

O backup `adventureworks_dw.backup` pode ser compartilhado separadamente para facilitar a restauração do DW, mas o repositório deve ser capaz de reconstruir sua estrutura através do script SQL.

---

## Documentação

A documentação do projeto deverá conter, entre outros itens:

- análise do AdventureWorks OLTP;
- definição e justificativa dos KPIs;
- definição da granularidade;
- modelagem da tabela fato;
- modelagem das dimensões;
- Star Schema;
- dicionário de dados;
- mapeamento OLTP → DW;
- estratégia de ETL incremental;
- implementação do Data Warehouse;
- consultas SQL dos indicadores.

---

## Status atual

```text
Análise do AdventureWorks                 ✅
Definição dos KPIs                        ✅
Definição da granularidade                ✅
Modelagem da FatoVenda                    ✅
Modelagem das dimensões                   ✅
Star Schema conceitual                    ✅
Dicionário de dados                       ✅
Mapeamento OLTP → DW                      ✅
Validação do mapeamento                   ✅
Modelo físico PostgreSQL                  ✅
Criação do Data Warehouse                 ✅
PKs / FKs / UNIQUE / CHECK / índices      ✅
ETL incremental em Python                 🚧
Carga das dimensões                       🚧
Carga da FatoVenda                        🚧
Validação dos 10 KPIs                     🚧
Artigo final                              🚧
```

---

## Referências

- Microsoft — AdventureWorks Sample Databases
- AdventureWorks2016
- PostgreSQL
- Python
- DBeaver
- Star Schema / Modelagem Multidimensional
- Guia de Elaboração de Trabalhos Acadêmicos do UniSales

---

## Integrantes

- Integrante 1
- Integrante 2
- Integrante 3
- Integrante 4

> Substituir pelos nomes dos integrantes antes da entrega final.
