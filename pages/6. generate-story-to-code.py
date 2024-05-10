from utils_vertex import * 
from utils_streamlit import reset_st_state
import streamlit as st


model = model_experimental

if reset := st.button("Reset Demo State"):
    reset_st_state()


st.write("Using Gemini Pro Experimental ")
st.subheader("Generate a User Story")
# Story premise
persona_name = st.text_input(
    "Persona: \n\n", key="persona_name", value="Joao"
)
persona_type = st.text_input(
    "Tipo de persona? \n\n", key="persona_type", value="Customer"
)


user_story = st.selectbox ('Selecione um tema:', [
            'Como cliente curioso, quero ver teasers sobre o próximo lançamento do produto para despertar meu interesse.',
            'Como cliente fidelizado, quero ser recompensado com acesso antecipado ou ofertas exclusivas para o novo produto.',
            'Como cliente experiente em tecnologia, quero aprender sobre os recursos e benefícios do novo produto por meio de páginas de produto detalhadas ou vídeos.',
            'Como cliente recorrente, quero poder encontrar e adicionar rapidamente o novo produto ao meu carrinho.',
            'Como cliente preocupado com o preço, quero ver informações claras sobre preços, descontos e quaisquer pacotes disponíveis para o novo produto.',
            'Como cliente satisfeito, quero deixar uma avaliação e compartilhar minha experiência com o novo produto.' 
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
    # st.write(prompt)    with st.spinner("Generating your story using Gemini ..."):
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
    with st.spinner("Generating your story using Gemini 1.0 Pro ..."):
        first_tab1, first_tab2= st.tabs(["Tasks", "Prompt"])
        with first_tab1:
            responseTasks = sendPrompt(promptTasks, model)
            if responseTasks:
                st.write("Your Tasks:")
                st.markdown(responseTasks)
                st.session_state["response"] = responseTasks
        with first_tab2:
            st.text(promptTasks)

promptSnippets = """A partir da lista de tasks, crie snippets de python para implementar a funcionalidade para a primeira task da lista.
Identifique restrições ou requisitos específicos que impactam a implementação:
Limitações de tempo ou recursos
Compatibilidade com APIs ou bibliotecas externas
Padrões de codificação ou estilo a serem seguidos
Documente claramente quaisquer suposições ou premissas feitas.
Com as seguintes diretivas:
- Google Style Guide para formatação
- Utilize ferramentas e frameworks já existentes
- Garantir a reprodutibilidade do código em diferentes ambientes
- Código formatado com indentação e espaçamento adequados
- Comentários explicativos para cada seção do código
- Documentação com exemplos de uso e informações adicionais
Teste e Validação:
- Inclua testes automatizados para validar o funcionamento dos snippets:
- Casos de teste que garantem a cobertura das funcionalidades
- Verificação de erros e exceções
- Validação da correção dos resultados
- Assegure a confiabilidade e robustez do código gerado.

Crie o código somente para a primeira task. Faça uma ordem numerada onde o primeiro numero é o nome da task, o segundo é um sumário do código e depois coloque o snippet gerado e quantas novos itens precisar para complementar com a informação requerida. 
""" + st.session_state["response"]

st.divider()
generate_python = st.button("Criar snippets das tasks", key="generate_python")
if generate_python and promptSnippets:
    with st.spinner("Generating your tasks code using Gemini..."):
        first_tab1, first_tab2= st.tabs(["Code", "Prompt"])
        with first_tab1:
            responseSnippets = sendPrompt(promptSnippets, model)
            if responseSnippets:
                st.write("Your code snippets:")
                st.markdown(responseSnippets)
                st.session_state["snippets"] = responseSnippets
        with first_tab2:
            st.text(promptSnippets)
