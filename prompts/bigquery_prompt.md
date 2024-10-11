All the answers are required to be in {story_lang}.
## Prompt para Criação de Tabela DW no BigQuery a Partir de Sugestão (Saúde)

**Instruções para o Modelo:**

1. **Recebimento da Sugestão:**
   - Receba a sugestão de tabela DW gerada anteriormente para o contexto de saúde, incluindo:
      - Nome da tabela
      - Dimensões (com seus atributos e tipos de dados)
      - Fatos (com suas métricas e tipos de dados)
      - Exemplos de dados (opcional)

2. **Criação do Dataset no BigQuery:**
   - Utilize o comando `gcloud` para criar um novo dataset no BigQuery, caso ainda não exista:
     ```bash
     gcloud bigquery datasets create [NOME_DO_DATASET] --location=[LOCALIZAÇÃO]
     ```
     - Substitua `[NOME_DO_DATASET]` por um nome relevante para o contexto de saúde (ex: `dados_saude`).
     - Substitua `[LOCALIZAÇÃO]` pela localização geográfica do dataset (ex: `southamerica-east1`).

3. **Criação das Tabelas de Dimensão:**
   - Para cada dimensão na sugestão, gere um comando SQL `CREATE TABLE` para criar a tabela correspondente no BigQuery:
     ```sql
     CREATE TABLE [NOME_DO_DATASET].[NOME_DA_DIMENSÃO] (
         [ID_DIMENSÃO] [TIPO_DE_DADO] PRIMARY KEY,
         [ATRIBUTO1] [TIPO_DE_DADO],
         [ATRIBUTO2] [TIPO_DE_DADO],
         ...
     );
     ```
     - Substitua `[NOME_DO_DATASET]` pelo nome do dataset criado.
     - Substitua `[NOME_DA_DIMENSÃO]` pelo nome da dimensão (ex: `Paciente`, `Profissional_Saude`, `Procedimento_Medico`).
     - Substitua `[ID_DIMENSÃO]` pelo nome do atributo chave primária da dimensão (ex: `ID_Paciente`, `ID_Profissional`, `ID_Procedimento`).
     - Substitua `[TIPO_DE_DADO]` pelo tipo de dado apropriado para cada atributo (ex: `INTEGER`, `STRING`, `DATE`, `FLOAT`).

4. **Criação da Tabela de Fato:**
   - Gere um comando SQL `CREATE TABLE` para criar a tabela de fato no BigQuery:
     ```sql
     CREATE TABLE [NOME_DO_DATASET].[NOME_DA_TABELA_FATO] (
         [ID_FATO] [TIPO_DE_DADO] PRIMARY KEY,
         [FK_DIMENSÃO1] [TIPO_DE_DADO] REFERENCES [NOME_DO_DATASET].[NOME_DA_DIMENSÃO1]([ID_DIMENSÃO1]),
         [FK_DIMENSÃO2] [TIPO_DE_DADO] REFERENCES [NOME_DO_DATASET].[NOME_DA_DIMENSÃO2]([ID_DIMENSÃO2]),
         ...
         [METRICA1] [TIPO_DE_DADO],
         [METRICA2] [TIPO_DE_DADO],
         ...
     );
     ```
     - Substitua `[NOME_DA_TABELA_FATO]` pelo nome da tabela de fato (ex: `Fato_Consulta`).
     - Substitua `[FK_DIMENSÃO]` pelos nomes das chaves estrangeiras que se referem às dimensões (ex: `FK_Paciente`, `FK_Profissional`).
     - Substitua `[METRICA]` pelos nomes das métricas (ex: `Duracao_Consulta`, `Custo_Procedimento`).

5. **Inserção de Dados (Opcional)**
   - Se a sugestão incluir exemplos de dados, gere comandos SQL `INSERT INTO` para inserir esses dados nas tabelas criadas.

**Exemplo de Prompt (Saúde):**

```
Sugestão de Tabela DW:

Nome da Tabela: Fato_Consulta

Dimensões:
- Paciente (ID_Paciente INTEGER, Nome STRING, Data_Nascimento DATE)
- Profissional_Saude (ID_Profissional INTEGER, Nome STRING, Especialidade STRING)
- Procedimento_Medico (ID_Procedimento INTEGER, Descricao STRING)

Fatos:
- Data_Consulta DATE
- Duracao_Consulta INTEGER
- Custo_Procedimento FLOAT

Crie as tabelas no BigQuery e gere os comandos SQL necessários.
```

Dados: