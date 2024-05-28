from utils_vertex import * 
from utils_streamlit import reset_st_state
import streamlit as st


def load_models(model_name):
    if model_name == "gemini-experimental":
        model = model_experimental
    elif model_name == "gemini-1.5-pro-001":
        model = model_gemini_pro_15
    else:
        model = model_gemini_flash
    return model 


if reset := st.button("Reset Demo State"):
    reset_st_state()

if 'response' not in st.session_state:
    st.session_state['response'] = 'init'


st.subheader("Generate a User Story")
# Story premise
model_name = st.radio(
      label="Model:",
      options=["gemini-experimental", "gemini-1.5-pro-001", "gemini-1.5-flash-001"],
      captions=["Gemini Pro Experimental", "Gemini Pro 1.5", "Gemini Flash 1.5"],
      key="model_name",
      index=0,
      horizontal=True)

model = load_models(model_name)


persona_name = st.text_input(
    "Persona: \n\n", key="persona_name", value="Breno Cabral"
)
persona_type = st.text_input(
    "Tipo de persona? \n\n", key="persona_type", value="Customer"
)



user_story = st.selectbox ('Selecione um tema:', [
			'[Consumo] Como cliente, quero visualizar meu histórico de consumo de energia para entender meus padrões de uso.',
            '[Troca] Como cliente, quero trocar minha titularidade da conta de energia',
			'[Alertas] Como cliente, quero receber alertas sobre interrupções de energia programadas para me planejar.',
			'[Adesão] Como cliente, quero solicitar um novo ponto de fornecimento de energia de forma rápida e fácil.',
			'[Portal] Como cliente, quero acessar um portal online para gerenciar minha conta de energia e realizar pagamentos.',
            '[Atendimento] Como cliente, quero entrar em contato com um representante de atendimento para tirar dúvidas e resolver problemas.',
            '[Transparência] Como cliente, quero receber informações claras e transparentes sobre tarifas, prazos e condições do serviço.',
            '[Ouvidoria] Como cliente, quero ter acesso a um canal de comunicação para registrar reclamações e sugestões.'

            ], 
            key="user_story", 

            )

length_of_story = st.radio(
    "Select the length of the story: \n\n",
    ["Short", "Long"],
    key="length_of_story",
    horizontal=True,
)

story_lang = st.radio(
    "Select the language to be used for the story generation: \n\n",
    ["Portuguese", "Spanish", "English"],
    key="story_lang",
    horizontal=True,
)

prompt = f"""Write a {length_of_story} User story based on the following premise: \n
      persona_name: {persona_name} \n
      persona_type: {persona_type} \n
      user_story: {user_story} \n
      First start by giving the user Story an Summary: [concise, memorable, human-readable story title] 
    User Story Format example:
        As a: [{persona_type}]
        I want to: [Action or Goal]
        So that: [Benefit or Value]
        Additional Context: [Optional details about the scenario, environment, or specific requirements]
        Acceptance Criteria: [Specific, measurable conditions that must be met for the story to be considered complete]
            *   **Scenario**: \n
                    [concise, human-readable user scenario]
            *   **Given**: \n
                    [Initial context]
            *   **and Given**: \n
                    [Additional Given context]
            *   **and Given** \n
                    [additional Given context statements as needed]
            *   **When**: \n
                    [Event occurs]
            *   **Then**: \n
                    [Expected outcome]
All the answers are required to be in {story_lang} and to stick to the persona. 
      """

generate_t2t = st.button("Generate my story", key="generate_t2t")
if generate_t2t and prompt:
    with st.spinner("Generating your story using Gemini ..."):
        first_tab1, first_tab2= st.tabs(["Story", "Prompt"])
        with first_tab1:
            responseStory = sendPrompt(prompt, model)
            if responseStory:
                st.write("Your story:")
                st.markdown(responseStory)
                st.session_state["response"] = responseStory
        with first_tab2:
            st.text(prompt)
        


promptTasks = f"""All the answers are required to be in {story_lang} and to stick to the persona. 
Divida a história de usuário em tarefas o mais granular possível. 
O objetivo de fragmentar uma história de usuário é criar uma lista de tarefas que possam ser concluídas dentro de um sprint. 
Portanto, é importante dividir a história em tarefas mínimas que ainda agreguem valor ao usuário final. 
Isso facilita o acompanhamento do progresso e garante que a equipe se mantenha no caminho certo.
Crie uma tabela com as tasks como índice da tabela com a descrição da task. 
""" + st.session_state["response"]

st.divider()
generate_Tasks = st.button("Gerar a lista de tasks a partir user story", key="generate_Tasks")
if generate_Tasks and promptTasks:
    with st.spinner("Generating your story using Gemini Pro ..."):
        first_tab1, first_tab2= st.tabs(["Tasks", "Prompt"])
        with first_tab1:
            responseTasks = sendPrompt(promptTasks, model)
            if responseTasks:
                st.write("Your Tasks:")
                st.markdown(responseTasks)
                st.session_state["response"] = responseTasks
        with first_tab2:
            st.text(promptTasks)

promptSnippets = f"""Análise da User Story:

Exemplo:
User Story: "Como médico, quero poder acompanhar o histórico de consultas dos meus pacientes, incluindo datas, diagnósticos, procedimentos realizados e medicamentos prescritos."

Tasks:
- Acessar o prontuário eletrônico do paciente.
- Visualizar lista de consultas anteriores com detalhes.
- Adicionar novas informações sobre a consulta atual.

Gere uma sugestão de tabela DW para armazenar os dados necessários para atender a essa user story.
Fim exemplo:

Leia atentamente a descrição da user story de varejo fornecida.
Identifique as tasks (ou atividades) que compõem a user story.
Extraia os principais substantivos e verbos das tasks, pois eles podem indicar dimensões e fatos relevantes para a tabela DW.


Modelagem Dimensional:

Crie uma lista de dimensões candidatas com base nos substantivos identificados. Exemplos de dimensões comuns em saúde:
Paciente
Profissional de Saúde (Médico, Enfermeiro, etc.)
Instituição de Saúde (Hospital, Clínica, etc.)
Tempo (Data, Hora, Dia da Semana, Mês, Ano)
Procedimento Médico
Medicamento
Diagnóstico
Plano de Saúde
[Coloque sempre em formato de tabela]

Modelagem de Fatos:
Identifique os fatos (eventos mensuráveis) a partir dos verbos das tasks. 
Exemplos de fatos em saúde:
Consulta Médica
Internação
Exame
Cirurgia
Prescrição de Medicamento

Determine as métricas (valores numéricos) associadas a cada fato. 

Exemplos de métricas:
Duração da Consulta
Custo do Procedimento
Dosagem do Medicamento
Resultados do Exame
[Coloque sempre em formato de tabela]

Estrutura da Tabela DW:

Crie uma tabela com as seguintes colunas:
Chave Primária: Identificador único da linha (geralmente um número sequencial).
Chaves Estrangeiras: Colunas que se referem às chaves primárias das dimensões.
Métricas: Colunas que armazenam os valores numéricos dos fatos.
Defina os tipos de dados adequados para cada coluna.
[Coloque sempre em formato de tabela]

Inclua exemplos de dados que poderiam ser inseridos na tabela DW, com base nas tasks da user story.  

Sempre ao gerar dados mock, utilize algum nome da seguinte lista:
Breno, Amadei, Carlos, Mazurque, Kauy, Filipe, Renato, Wilgner, Rober, Diego, Iago, Tiago, Brunno, Koba
Utilize o dados abaixo como entrada. 
All the answers are required to be in {story_lang}.
""" + st.session_state["response"]

st.divider()
generate_python = st.button("Criar dw das tasks", key="generate_python")
if generate_python and promptSnippets:
    with st.spinner("Generating your tasks dw using Gemini..."):
        first_tab1, first_tab2= st.tabs(["Code", "Prompt"])
        with first_tab1:
            responseSnippets = sendPrompt(promptSnippets, model)
            if responseSnippets:
                st.write("Your dw snippets:")
                st.markdown(responseSnippets)
                st.session_state["response"] = responseSnippets
        with first_tab2:
            st.text(promptSnippets)

promptBigQuery = f"""
All the answers are required to be in {story_lang}.
## Prompt para Criação de Tabela DW no BigQuery a Partir de Sugestão (Energia - Consumidor Final)

**Instruções para o Modelo:**

1. **Recebimento da Sugestão:**
   - Receba a sugestão de tabela DW gerada anteriormente para o contexto de energia, com foco no consumidor final, incluindo:
      - Nome da tabela
      - Dimensões (com seus atributos e tipos de dados)
      - Fatos (com suas métricas e tipos de dados)
      - Exemplos de dados (opcional)

2. **Criação do Dataset no BigQuery:**
   - Utilize o comando `gcloud` para criar um novo dataset no BigQuery, caso ainda não exista:
     ```bash
     gcloud bigquery datasets create [NOME_DO_DATASET] --location=[LOCALIZAÇÃO]
     ```
     - Substitua `[NOME_DO_DATASET]` por um nome relevante para o contexto de energia (ex: `dados_energia_consumidor`).
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
     - Substitua `[NOME_DA_DIMENSÃO]` pelo nome da dimensão (ex: `Consumidor`, `Localizacao`, `Tarifa_Energia`).
     - Substitua `[ID_DIMENSÃO]` pelo nome do atributo chave primária da dimensão (ex: `ID_Consumidor`, `ID_Localizacao`, `ID_Tarifa`).
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
     - Substitua `[NOME_DA_TABELA_FATO]` pelo nome da tabela de fato (ex: `Fato_Consumo_Energia`).
     - Substitua `[FK_DIMENSÃO]` pelos nomes das chaves estrangeiras que se referem às dimensões (ex: `FK_Consumidor`, `FK_Tarifa`).
     - Substitua `[METRICA]` pelos nomes das métricas (ex: `Consumo_kWh`, `Valor_Total`).

5. **Inserção de Dados (Opcional):**
   - Se a sugestão incluir exemplos de dados, gere comandos SQL `INSERT INTO` para inserir esses dados nas tabelas criadas.

**Exemplo de Prompt (Energia - Consumidor Final):**

```
Sugestão de Tabela DW:

Nome da Tabela: Fato_Consumo_Energia

Dimensões:
- Consumidor (ID_Consumidor INTEGER, Nome STRING, Tipo_Residencia STRING, Classe_Consumo STRING)
- Localizacao (ID_Localizacao INTEGER, Cidade STRING, Estado STRING, Regiao STRING)
- Tarifa_Energia (ID_Tarifa INTEGER, Descricao STRING, Valor_kWh FLOAT)

Fatos:
- Data_Leitura DATE
- Consumo_kWh FLOAT
- Valor_Total FLOAT
- Bandeira_Tarifaria STRING

Crie as tabelas no BigQuery e gere os comandos SQL necessários.
```

Dados:
""" + st.session_state["response"]

st.divider()
generate_bigquery = st.button("Criar Implementação no BigQuery", key="generate_bigquery")
if generate_bigquery and promptBigQuery:
    with st.spinner("Generating your BigQuery implementation using Gemini..."):
        first_tab1, first_tab2= st.tabs(["Code", "Prompt"])
        with first_tab1:
            responseBigQuery = sendPrompt(promptBigQuery, model)
            if responseBigQuery:
                st.write("Your bq snippets:")
                st.markdown(responseBigQuery)
                st.session_state["bigquery"] = responseBigQuery
        with first_tab2:
            st.text(responseBigQuery)
