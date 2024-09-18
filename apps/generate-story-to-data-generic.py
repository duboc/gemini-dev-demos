import streamlit as st
from utils_vertex import sendPrompt, model_experimental, model_gemini_pro_15, model_gemini_flash
from utils_streamlit import reset_st_state

def load_models(model_name):
    if model_name == "gemini-experimental":
        return model_experimental
    elif model_name == "gemini-1.5-pro-001":
        return model_gemini_pro_15
    else:
        return model_gemini_flash

def load_questions(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read().splitlines()
    except FileNotFoundError:
        st.warning(f"File not found: {file_path}. Falling back to English version.")
        english_file_path = file_path.replace('-es.txt', '-en.txt').replace('-pt.txt', '-en.txt')
        with open(english_file_path, 'r', encoding='utf-8') as f:
            return f.read().splitlines()

if 'results' not in st.session_state:
    st.session_state['results'] = []

if st.button("Reset Demo State", key="reset_button"):
    reset_st_state()
    st.session_state['results'] = []

st.title("User Story to Data 📊")

# Initialize button states in session state if not already present
if 'button_states' not in st.session_state:
    st.session_state.button_states = {
        'generate_story': False,
        'generate_tasks': False,
        'generate_dw': False,
        'generate_bigquery': False
    }

def create_button_with_status(label, key, disabled=False):
    col1, col2 = st.columns([3, 1])
    with col1:
        clicked = st.button(label, key=key, disabled=disabled)
    with col2:
        if st.session_state.button_states.get(key, False):
            st.markdown(':green[Completed]')
        elif disabled:
            st.markdown(':gray[Waiting]')
        else:
            st.markdown(':blue[Ready]')
    return clicked

def update_button_state(button_key):
    st.session_state.button_states[button_key] = True

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Configuration")
    model_name = st.radio(
        "Model:",
        ["gemini-experimental", "gemini-1.5-pro-001", "gemini-1.5-flash-001"],
        captions=["Gemini Pro Experimental", "Gemini Pro 1.5", "Gemini Flash 1.5"],
        key="model_name",
        index=0,
        horizontal=True
    )

    model = load_models(model_name)

    selected_category = st.radio(
        "Select Industry:",
        ["retail", "energy", "health", "finance", "beauty"],
        key="category"
    )

    persona_name = st.text_input("Persona:", key="persona_name", value="Breno Cabral")

    story_lang = st.radio(
        "Select language for story generation:",
        ["English", "Portuguese", "Spanish"],
        key="story_lang",
        horizontal=True,
    )

    # Map selected language to file suffix
    lang_suffix = {
        "English": "en",
        "Portuguese": "pt",
        "Spanish": "es"
    }

    QUESTIONS_FILE = f"./data/{selected_category}-{lang_suffix[story_lang]}.txt"
    questions = load_questions(QUESTIONS_FILE)
with col2:
    selected_index = st.selectbox('Select a theme:', 
                                  range(len(questions)), 
                                  format_func=lambda i: questions[i], 
                                  key="user_story")
    st.subheader("User Theme")
    user_story = st.text_area("Edit your theme:", value=questions[selected_index], height=200)

    if create_button_with_status("1. Generate my story", "generate_story"):
        prompt = f"""Write a User story based on the following premise:
        persona_name: {persona_name}
        user_story: {user_story}
        First start by giving the user Story a Summary: [concise, memorable, human-readable story title] 
        User Story Format example:
            As a: [persona_type]
            I want to: [Action or Goal]
            So that: [Benefit or Value]
            Additional Context: [Optional details about the scenario, environment, or specific requirements]
            Acceptance Criteria: [Specific, measurable conditions that must be met for the story to be considered complete]
                *   **Scenario**: 
                        [concise, human-readable user scenario]
                *   **Given**: 
                        [Initial context]
                *   **and Given**: 
                        [Additional Given context]
                *   **and Given** 
                        [additional Given context statements as needed]
                *   **When**: 
                        [Event occurs]
                *   **Then**: 
                        [Expected outcome]
        All the answers are required to be in {story_lang} and to stick to the persona. 
        """

        with st.spinner("Generating your story using Gemini ..."):
            responseStory = sendPrompt(prompt, model)
            if responseStory:
                st.session_state['results'].append(("User Story", responseStory, prompt))
                update_button_state('generate_story')
                st.rerun()

    if create_button_with_status("2. Generate tasks from user story", "generate_tasks", 
                                 disabled=not st.session_state.button_states.get('generate_story', False)):
        if st.session_state['results']:
            last_story = next((result for result in reversed(st.session_state['results']) if result[0] == "User Story"), None)
            if last_story:
                promptTasks = f"""All the answers are required to be in {story_lang} and to stick to the persona. 
                Divide the user story into tasks as granular as possible. 
                The goal of fragmenting a user story is to create a list of tasks that can be completed within a sprint. 
                Therefore, it is important to break down the story into minimal tasks that still add value to the end user. 
                This facilitates progress tracking and ensures that the team stays on track.
                Create a table with the tasks as the table index with the task description. 
                """ + last_story[1]

                with st.spinner("Generating your tasks using Gemini Pro ..."):
                    responseTasks = sendPrompt(promptTasks, model)
                    if responseTasks:
                        st.session_state['results'].append(("Tasks", responseTasks, promptTasks))
                        update_button_state('generate_tasks')
                        st.rerun()
            else:
                st.warning("Please generate a user story first.")
        else:
            st.warning("Please generate a user story first.")

    if create_button_with_status("3. Create DW from tasks", "generate_dw", 
                                 disabled=not st.session_state.button_states.get('generate_tasks', False)):
        if st.session_state['results']:
            last_tasks = next((result for result in reversed(st.session_state['results']) if result[0] == "Tasks"), None)
            if last_tasks:
                promptSnippets = f"""
                    Análise da User Story:
                    All the answers are required to be in {story_lang}.
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
                """ + last_tasks[1]

                with st.spinner("Generating your tasks DW using Gemini..."):
                    responseSnippets = sendPrompt(promptSnippets, model)
                    if responseSnippets:
                        st.session_state['results'].append(("DW Snippets", responseSnippets, promptSnippets))
                        update_button_state('generate_dw')
                        st.rerun()

            else:
                st.warning("Please generate tasks first.")
        else:
            st.warning("Please generate a user story and tasks first.")

    if create_button_with_status("4. Create BigQuery Implementation", "generate_bigquery", 
                                 disabled=not st.session_state.button_states.get('generate_dw', False)):
        if st.session_state['results']:
            last_dw = next((result for result in reversed(st.session_state['results']) if result[0] == "DW Snippets"), None)
            if last_dw:
                promptBigQuery = f"""
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
                    
                    5. **Inserção de Dados (Opcional)
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

                """ + last_dw[1]

                with st.spinner("Generating your BigQuery implementation using Gemini..."):
                    responseBigQuery = sendPrompt(promptBigQuery, model)
                    if responseBigQuery:
                        st.session_state['results'].append(("BigQuery Snippets", responseBigQuery, promptBigQuery))
                        update_button_state('generate_bigquery')
                        st.rerun()

            else:
                st.warning("Please create DW snippets first.")
        else:
            st.warning("Please generate a user story, tasks, and DW snippets first.")

# Display all results
st.subheader("Results")
for result_type, result_content, prompt in reversed(st.session_state['results']):
    with st.expander(f"{result_type} - Click to expand/collapse"):
        st.markdown("### Generated Content")
        st.markdown(result_content)
        st.markdown("### Prompt Used")
        st.code(prompt, language="markdown")