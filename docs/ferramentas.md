# Registro de Ferramentas do Projeto

## 1. Objetivo

Este documento registra as ferramentas, tecnologias e versões utilizadas no
projeto individual de Data Warehouse baseado no AdventureWorks.

O registro tem como finalidade facilitar a reprodução do ambiente,
a documentação técnica e a elaboração do artigo acadêmico.

---

## 2. Sistema Operacional

| Item | Versão / Informação |
|---|---|
| Sistema Operacional | Windows |
| Versão do Windows | 10.0.26200.9550 |
| Arquitetura | 64 bits |

O Windows é utilizado como sistema operacional principal e hospeda o SQL Server,
SQL Server Management Studio, Docker Desktop e ferramentas de desenvolvimento.

---

## 3. Windows Subsystem for Linux

| Item | Versão |
|---|---|
| WSL | 3.0.1.0 |
| Kernel Linux | 6.18.40.1-1 |
| WSLg | 1.0.79 |
| MSRDC | 1.2.7214 |
| Direct3D | 1.611.1-81528511 |
| DXCore | 10.0.26100.1-240331-1435.ge-release |
| Distribuição Linux | Ubuntu |
| Versão WSL da distribuição | WSL 2 |

O WSL foi utilizado para disponibilizar um ambiente Linux compatível com
Docker e Apache Airflow.

Validação realizada com:

```powershell
wsl --version
```

e:

```powershell
wsl -l -v
```

Resultado principal:

```text
Ubuntu          VERSION 2
docker-desktop  VERSION 2
```

---

## 4. Docker

| Ferramenta | Versão |
|---|---|
| Docker Engine / CLI | 29.9.1 |
| Docker Compose | 5.6.0 |
| Docker Desktop | 4.96.0 |

O Docker será utilizado para executar os serviços necessários ao projeto,
principalmente Apache Airflow e PostgreSQL.

A instalação foi validada através do container oficial:

```powershell
docker run hello-world
```

Resultado:

```text
Hello from Docker!
```

O teste confirmou a comunicação entre o Docker Client e o Docker Engine,
o download de imagens e a execução de containers.

---

## 5. Banco de Dados de Origem

| Ferramenta | Finalidade | Versão |
|---|---|---|
| Microsoft SQL Server | Banco OLTP de origem | A confirmar |
| SQL Server Management Studio (SSMS) | Administração e exploração do AdventureWorks | A confirmar |

Banco utilizado:

```text
AdventureWorks2016
```

O SQL Server contém o banco transacional AdventureWorks utilizado como
fonte da ETL.

---

## 6. Banco de Dados Analítico

| Ferramenta | Finalidade | Versão prevista |
|---|---|---|
| PostgreSQL | Data Warehouse | PostgreSQL 16 |

Banco previsto:

```text
adventureworks_dw
```

Schema principal:

```text
dw
```

O PostgreSQL será executado em container Docker.

Status atual:

```text
Configuração pendente - Fase 3
```

---

## 7. Orquestração

| Ferramenta | Finalidade | Versão prevista |
|---|---|---|
| Apache Airflow | Orquestração da ETL | 3.3.1 |

A versão utilizada será baseada no ambiente disponibilizado pelo professor
no diretório:

```text
unisales.etl.20262-main/aula.etl.2
```

O ambiente utiliza:

```text
LocalExecutor
```

e possui serviços separados para:

- Airflow API Server;
- Scheduler;
- DAG Processor;
- Triggerer;
- banco de metadados PostgreSQL.

Status atual:

```text
Configuração pendente - Fase 3
```

---

## 8. Desenvolvimento e Versionamento

| Ferramenta | Finalidade | Versão |
|---|---|---|
| Git | Controle de versão | A confirmar |
| GitHub | Hospedagem do repositório | Serviço web |
| Visual Studio Code | Desenvolvimento e edição de arquivos | A confirmar |
| PowerShell | Execução de comandos no Windows | Ambiente do Windows |

Repositório principal:

```text
Phablinhoobscuro/adventureworks-datawarehouse
```

---

## 9. Linguagens e tecnologias previstas

| Tecnologia | Utilização |
|---|---|
| Python | ETL e tasks do Airflow |
| SQL | Criação do DW, transformações e KPIs |
| YAML | Configuração do Docker Compose |
| Markdown | Documentação do projeto |
| Docker | Containerização |
| PostgreSQL | Data Warehouse |
| SQL Server | Banco OLTP |
| Apache Airflow | Orquestração |

As versões do Python e das bibliotecas serão registradas quando a ETL for
integrada ao ambiente definitivo.

---

## 10. Materiais reutilizados

Além das ferramentas instaladas, o projeto utiliza dois conjuntos de materiais
fornecidos ou autorizados para reutilização.

### Projeto anterior

```text
Phablinhoobscuro/-AdventureWorks
```

Componentes reutilizáveis:

- Star Schema;
- modelo físico PostgreSQL;
- ETL Python;
- ETL incremental;
- consultas dos KPIs;
- documentação técnica.

### Material disponibilizado pelo professor

```text
Jamesasj/unisales.etl.20262
```

Diretório principal:

```text
aula.etl.2
```

Componentes utilizados como referência:

- Docker Compose;
- Apache Airflow;
- PostgreSQL;
- configuração por `.env`;
- estrutura de DAGs;
- uso de `@dag`;
- uso de `@task`;
- `SQLExecuteQueryOperator`.

---

## 11. Status do ambiente

| Componente | Status |
|---|---|
| Windows | Configurado |
| WSL | Configurado |
| Ubuntu / WSL 2 | Configurado |
| Docker Desktop | Configurado |
| Docker Engine | Validado |
| Docker Compose | Validado |
| GitHub | Configurado |
| Repositório local | Configurado |
| SQL Server / AdventureWorks | Disponível |
| PostgreSQL DW | Pendente |
| Apache Airflow | Pendente |
| Conexões Airflow | Pendente |

---

## 12. Atualizações futuras

Este documento deverá ser atualizado sempre que uma nova ferramenta ou versão
for incorporada ao ambiente.

Ainda deverão ser registrados:

- versão do Git;
- versão do Visual Studio Code;
- versão do SQL Server;
- versão do SSMS;
- versão do Python;
- bibliotecas Python utilizadas;
- PostgreSQL após implantação;
- Apache Airflow após implantação.
