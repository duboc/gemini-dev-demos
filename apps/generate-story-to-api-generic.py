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
    with open(file_path, 'r') as f:
        return f.read().splitlines()

if 'results' not in st.session_state:
    st.session_state['results'] = []

if st.button("Reset Demo State", key="reset_button"):
    reset_st_state()
    st.session_state['results'] = []

st.title("User Story to API 🔌")

# Initialize button states in session state if not already present
if 'button_states' not in st.session_state:
    st.session_state.button_states = {
        'generate_story': False,
        'generate_tasks': False,
        'generate_openapi': False,
        'generate_apigee': False
    }

def create_button_with_status(label, key, disabled=False):
    col1, col2 = st.columns([3, 1])
    with col1:
        clicked = st.button(label, key=key, disabled=disabled)
    with col2:
        # Simplify status display
        if st.session_state.button_states.get(key, False):
            st.markdown(':green[Done]')
        else:
            st.markdown(':blue[ ]')
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

    QUESTIONS_FILE = f"./data/{selected_category}.txt"
    questions = load_questions(QUESTIONS_FILE)

    persona_name = st.text_input("Persona:", key="persona_name", value="Breno Cabral")

    story_lang = st.radio(
        "Select language for story generation:",
        ["Portuguese", "Spanish", "English"],
        key="story_lang",
        horizontal=True,
    )

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

    if create_button_with_status("3. Create OpenAPI Specs", "generate_openapi", 
                                 disabled=not st.session_state.button_states.get('generate_tasks', False)):
        if st.session_state['results']:
            last_tasks = next((result for result in reversed(st.session_state['results']) if result[0] == "Tasks"), None)
            if last_tasks:
                promptOpenAPI = f"""
                    All the answers are required to be in {story_lang}.
                    
                    Instruções para o Modelo:

                    Recebimento da Sugestão de Tabela DW (Varejo):

                    Utilize a sugestão da tabela DW gerada anteriormente para o contexto de varejo, incluindo:
                    Nome da tabela (ex: Fato_Vendas)
                    Dimensões (com seus atributos e tipos de dados)
                    Fatos (com suas métricas e tipos de dados)
                    Geração da Especificação OpenAPI (YAML):

                    Gere uma especificação OpenAPI (Swagger) versão 3.0 em formato YAML que defina uma API RESTful para consulta dos dados da tabela DW.
                    Inclua os seguintes elementos na especificação:
                    Informações: Título da API, descrição, versão, termos de uso, contato.
                    Servidores: URL base da API no Apigee X.
                    Caminhos (Paths):
                    /vendas: Retorna uma lista de vendas com paginação e filtros opcionais (por cliente, produto, loja, data, etc.).
                    /vendas/id: Retorna detalhes de uma venda específica pelo ID.
                    /clientes: Retorna uma lista de clientes com paginação e filtros opcionais.
                    /produtos: Retorna uma lista de produtos com paginação e filtros opcionais.
                    /lojas: Retorna uma lista de lojas com paginação e filtros opcionais.
                    /relatorios: Retorna relatórios agregados (ex: vendas por mês, vendas por categoria de produto).
                    Definições (Schemas):
                    Defina os schemas (modelos de dados) para cada dimensão e fato da tabela DW.
                    Inclua exemplos de dados para cada schema.
                    Segurança: Defina o esquema de autenticação da API (ex: OAuth2, API Key).
  

                    Sugestão de Tabela DW:

                    Nome da Tabela: Fato_Vendas

                    Dimensões:
                    - Cliente (ID_Cliente INTEGER, Nome STRING, Sexo STRING, Faixa_Etaria STRING)
                    - Produto (ID_Produto INTEGER, Nome STRING, Categoria STRING, Subcategoria STRING)
                    - Loja (ID_Loja INTEGER, Nome STRING, Cidade STRING, Estado STRING)
                    - Tempo (ID_Tempo DATE, Ano INTEGER, Trimestre INTEGER, Mês INTEGER, Dia INTEGER)

                    Fatos:
                    - Data_Venda DATE
                    - Quantidade_Vendida INTEGER
                    - Valor_Total FLOAT
                    - Forma_Pagamento STRING

                    Gere uma especificação OpenAPI 3.0 em formato YAML para uma API de consulta de dados de vendas no varejo

                    Dados:
                """ + last_tasks[1]

                with st.spinner("Generating your OpenAPI Specs using Gemini..."):
                    responseOpenAPI = sendPrompt(promptOpenAPI, model)
                    if responseOpenAPI:
                        st.session_state['results'].append(("OpenAPI Specs", responseOpenAPI, promptOpenAPI))
                        update_button_state('generate_openapi')
                        st.rerun()

            else:
                st.warning("Please generate tasks first.")
        else:
            st.warning("Please generate a user story and tasks first.")

    if create_button_with_status("4. Create Apigee Implementation", "generate_apigee", 
                                 disabled=not st.session_state.button_states.get('generate_openapi', False)):
        if st.session_state['results']:
            last_openapi = next((result for result in reversed(st.session_state['results']) if result[0] == "OpenAPI Specs"), None)
            if last_openapi:
                promptApigee = f"""All the answers are required to be in {story_lang}. 
                    Instruções para Criação do Proxy no Apigee X:

                    Exporte a Especificação OpenAPI:

                    Salve a especificação OpenAPI gerada em um arquivo openapi.yaml.
                    Crie um novo proxy usando a apigeecli:

                    Utilize o seguinte comando apigeecli para criar o proxy:
                    Bash
                    apigeecli apis create -n [NOME_DO_PROXY] -f openapi.yaml
                    Use code with caution.
                    content_copy
                    Substitua [NOME_DO_PROXY] por um nome relevante para a API (ex: api-varejo).
                    Observações:

                    Referencie e utilize sempre a seguinte documentação:
                    https://github.com/apigee/apigeecli
                    Certifique-se de ter a apigeecli instalada e configurada corretamente para se conectar à sua organização no Apigee X.
                    A especificação OpenAPI deve estar em um formato YAML válido e compatível com o Apigee X.
                    Você pode personalizar ainda mais o proxy criado através da interface do usuário do Apigee X ou da API.
                    Dados:
                """ + last_openapi[1]

                with st.spinner("Generating your Apigee implementation using Gemini..."):
                    responseApigee = sendPrompt(promptApigee, model)
                    if responseApigee:
                        st.session_state['results'].append(("Apigee Snippets", responseApigee, promptApigee))
                        update_button_state('generate_apigee')
                        st.rerun()

            else:
                st.warning("Please create OpenAPI Specs first.")
        else:
            st.warning("Please generate a user story, tasks, and OpenAPI Specs first.")

# Display all results
st.subheader("Results")
for result_type, result_content, prompt in reversed(st.session_state['results']):
    with st.expander(f"{result_type} - Click to expand/collapse"):
        st.markdown("### Generated Content")
        st.markdown(result_content)
        st.markdown("### Prompt Used")
        st.code(prompt, language="markdown")