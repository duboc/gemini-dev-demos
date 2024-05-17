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
			'Descoberta: Como cliente, quero encontrar facilmente produtos relevantes para minhas necessidades, tanto online quanto na loja física.',
			'Pesquisa e Comparação: Como cliente, quero comparar preços, características e avaliações de produtos similares para tomar a melhor decisão de compra.',
			'Compra (Online): Como cliente, quero um processo de compra online intuitivo, seguro e com diversas opções de pagamento e entrega.',
			'Compra (Loja Física): Como cliente, quero encontrar facilmente os produtos na loja, receber auxílio de vendedores atenciosos e ter um checkout rápido e eficiente.',
			'Pós-Compra (Online): Como cliente, quero acompanhar o status do meu pedido, receber notificações sobre a entrega e ter opções fáceis de troca ou devolução.',
			'Pós-Compra (Loja Física): Como cliente, quero trocar ou devolver produtos sem complicações e receber suporte para dúvidas ou problemas.',
			'Fidelização: Como cliente, quero ser reconhecido e recompensado por minhas compras, receber ofertas personalizadas e participar de programas de fidelidade.',
			'Loja Física: Como cliente, quero receber atendimento atencioso e personalizado de vendedores que conheçam bem os produtos e possam me ajudar a encontrar o que preciso.',
			'Online (Chat/E-mail): Como cliente, quero ter acesso a canais de atendimento online eficientes, com respostas rápidas e soluções eficazes para minhas dúvidas ou problemas.',
			'Central de Atendimento: Como cliente, quero falar com atendentes capacitados e resolver meus problemas de forma rápida e satisfatória.',
			'Canais de Autoatendimento: Como cliente, quero encontrar informações e soluções para problemas comuns através de FAQs, tutoriais em vídeo e chatbots.',
			'Personalização: Como cliente, quero receber recomendações de produtos, ofertas e conteúdo relevantes para meus interesses e histórico de compras.',
			'Omnichannel: Como cliente, quero uma experiência de compra integrada, com acesso aos mesmos produtos, informações e serviços em todos os canais de venda (online e offline).',
			'Sustentabilidade: Como cliente, quero ter acesso a informações sobre a origem e impacto ambiental dos produtos, além de opções de compra e descarte mais sustentáveis.'
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

Leia atentamente a descrição da user story de varejo fornecida.
Identifique as tasks (ou atividades) que compõem a user story.
Extraia os principais substantivos e verbos das tasks, pois eles podem indicar dimensões e fatos relevantes para a tabela DW.

Exemplo:
User Story: "Como cliente, quero poder visualizar o histórico das minhas compras, incluindo data, produtos comprados, quantidade, preço e valor total."

Tasks:
- Acessar a página de histórico de compras.
- Visualizar lista de compras anteriores com detalhes.
- Filtrar compras por período.

Gere uma sugestão de tabela DW para armazenar os dados necessários para atender a essa user story.
Fim exemplo:

Modelagem Dimensional:

Crie uma lista de dimensões candidatas com base nos substantivos identificados. \n
Exemplos de dimensões comuns em varejo:
Produto
Cliente
Loja
Tempo (Data, Hora, Dia da Semana, Mês, Ano)
Promoção
Categoria de Produto
Forma de Pagamento
Avalie a granularidade desejada para cada dimensão. Por exemplo, a dimensão tempo pode ser diária, semanal ou mensal.
[Coloque sempre em formato de tabela]

Modelagem de Fatos:
Identifique os fatos (eventos mensuráveis) a partir dos verbos das tasks. 
Exemplos de fatos em varejo:
Venda
Devolução
Visualização de Produto
Adição ao Carrinho
[Coloque sempre em formato de tabela]

Determine as métricas (valores numéricos) associadas a cada fato. Exemplos de métricas:
Quantidade Vendida
Valor Total da Venda
Preço Unitário
Desconto
Custo
[Coloque sempre em formato de tabela]

Estrutura da Tabela DW:

Crie uma tabela com as seguintes colunas:
Chave Primária: Identificador único da linha (geralmente um número sequencial).
Chaves Estrangeiras: Colunas que se referem às chaves primárias das dimensões.
Métricas: Colunas que armazenam os valores numéricos dos fatos.
Defina os tipos de dados adequados para cada coluna.
[Coloque sempre em formato de tabela]

Sempre ao gerar dados mock, utilize algum nome da seguinte lista:
Breno, Amadei, Carlos, Mazurque, Kauy, Filipe, Renato, Wilgner, Rober, Diego, Iago, Tiago, Brunno

Inclua exemplos de dados que poderiam ser inseridos na tabela DW, com base nas tasks da user story.  Utilize o dados abaixo como entrada.
 
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
                st.session_state["snippets"] = responseSnippets
        with first_tab2:
            st.text(promptSnippets)
