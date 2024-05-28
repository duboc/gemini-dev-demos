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
All the answers are required to be in {story_lang}.
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
        


promptTasks = f"""All the answers are required to be in {story_lang}.
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

promptSnippets = f"""A partir da lista de tasks, crie snippets de ADVPL para implementar a funcionalidade para a primeira task da lista.
Identifique restrições ou requisitos específicos que impactam a implementação:
Limitações de tempo ou recursos
Compatibilidade com APIs ou bibliotecas externas
Padrões de codificação ou estilo a serem seguidos
Documente claramente quaisquer suposições ou premissas feitas.
Com as seguintes diretivas:
- Google Style Guide para formatação
- Utilize a linguagem ADVPL
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
All the answers are required to be in {story_lang}.
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
