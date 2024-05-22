from utils_vertex import * 
from utils_streamlit import reset_st_state
import streamlit as st


def load_models(model_name):
    if model_name == "gemini-experimental":
        model = model_experimental
    elif model_name == "gemini-1.5-pro-preview-0514":
        model = model_gemini_pro_15
    else:
        model = model_gemini_flash
    return model 


if reset := st.button("Reset Demo State"):
    reset_st_state()

if 'response' not in st.session_state:
    st.session_state['response'] = 'init'

st.write("Using Gemini Pro Experimental ")
st.subheader("Generate a User Story")
# Story premise
model_name = st.radio(
      label="Model:",
      options=["gemini-experimental", "gemini-1.5-pro-preview-0514", "gemini-1.5-flash-preview-0514"],
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
				'1. Recomendação de Produtos Personalizada: Como Consultora de Beleza, desejo ter acesso a um sistema de CRM que utilize algoritmos de recomendação baseados em dados demográficos, histórico de compras e preferências das clientes, para que eu possa oferecer sugestões de produtos altamente personalizadas, maximizando o potencial de vendas e a satisfação do cliente.',
				'2. Otimização da Gestão de Estoque: Como Gerente de Vendas, necessito de um painel de controle com visualização em tempo real dos níveis de estoque, vendas por SKU e desempenho por região/consultora, a fim de identificar gargalos na cadeia de suprimentos, otimizar a alocação de estoque e prevenir rupturas ou excessos, garantindo a disponibilidade dos produtos e a eficiência logística.',
				'3. Treinamento Personalizado para a Força de Vendas: Como Gerente de Treinamento, desejo analisar o desempenho individual das consultoras, utilizando métricas como taxa de conversão, ticket médio e feedback de clientes, para que eu possa desenvolver programas de treinamento personalizados, abordando as necessidades específicas de cada consultora e aprimorando suas habilidades de vendas e conhecimento do portfólio de produtos.',
				'4. Análise Preditiva de Tendências e Lançamentos: Como Diretor de Marketing, requiro um sistema de inteligência de mercado que utilize técnicas de mineração de dados e análise de sentimentos em redes sociais, blogs e outras fontes relevantes, a fim de identificar tendências emergentes, prever a demanda do consumidor e orientar o desenvolvimento de novos produtos e estratégias de lançamento que estejam alinhados com as expectativas do mercado.',
				'5. Implementação de Programa de Fidelidade Personalizado: Como Gerente de Relacionamento com o Cliente, necessito de segmentar a base de clientes com base em dados comportamentais e transacionais, para que eu possa desenvolver um programa de fidelidade com níveis diferenciados, oferecendo recompensas personalizadas, benefícios exclusivos e comunicação direcionada, visando aumentar a retenção, o lifetime value e o engajamento do cliente.',
				'6. Monitoramento da Concorrência e Inteligência Competitiva: Como Analista de Mercado, desejo acesso a um sistema de inteligência competitiva que monitore os principais concorrentes, seus lançamentos, preços, promoções e estratégias de marketing, a fim de identificar oportunidades e ameaças, ajustar as estratégias da empresa e manter a competitividade no mercado.'
            ], 
            key="user_story", 

            )

length_of_story = st.radio(
    "Select the length of the story: \n\n",
    ["Short", "Long"],
    key="length_of_story",
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
        Todas as respostas precisam estar em português e utilizar sempre a persona indicada. 
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
        


promptTasks = """
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

promptSnippets = """Análise da User Story:

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
""" + st.session_state["response"]

st.divider()
generate_python = st.button("Criar modelagem", key="generate_python")
if generate_python and promptSnippets:
    with st.spinner("Generating your data model..."):
        first_tab1, first_tab2= st.tabs(["Code", "Prompt"])
        with first_tab1:
            responseSnippets = sendPrompt(promptSnippets, model)
            if responseSnippets:
                st.write("Your response:")
                st.markdown(responseSnippets)
                st.session_state["response"] = responseSnippets
        with first_tab2:
            st.text(promptSnippets)

promptBigQuery = """

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
/vendas/{id}: Retorna detalhes de uma venda específica pelo ID.
/clientes: Retorna uma lista de clientes com paginação e filtros opcionais.
/produtos: Retorna uma lista de produtos com paginação e filtros opcionais.
/lojas: Retorna uma lista de lojas com paginação e filtros opcionais.
/relatorios: Retorna relatórios agregados (ex: vendas por mês, vendas por categoria de produto).
Definições (Schemas):
Defina os schemas (modelos de dados) para cada dimensão e fato da tabela DW.
Inclua exemplos de dados para cada schema.
Segurança: Defina o esquema de autenticação da API (ex: OAuth2, API Key).
Criação do Proxy no Apigee X:

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
Exemplo de Prompt (Varejo):

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

Gere uma especificação OpenAPI 3.0 em formato YAML para uma API de consulta de dados de vendas no varejo e descreva os passos para criar um proxy no Apigee X usando a apigeecli.

Dados:
""" + st.session_state["response"]

st.divider()
generate_bigquery = st.button("Criar OpenAPI Specs", key="generate_bigquery")
if generate_bigquery and promptBigQuery:
    with st.spinner("Generating your Specs..."):
        first_tab1, first_tab2= st.tabs(["Code", "Prompt"])
        with first_tab1:
            responseBigQuery = sendPrompt(promptBigQuery, model)
            if responseBigQuery:
                st.write("Your response:")
                st.markdown(responseBigQuery)
                st.session_state["bigquery"] = responseBigQuery
        with first_tab2:
            st.text(responseBigQuery)
