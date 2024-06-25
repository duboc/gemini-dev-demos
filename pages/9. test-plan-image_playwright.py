from utils_vertex import model_gemini_pro, sendPrompt
import streamlit as st
from utils_streamlit import reset_st_state
import os
import vertexai
from vertexai.generative_models import (
    GenerationConfig,
    GenerativeModel,
    HarmBlockThreshold,
    HarmCategory,
    Part,
)

PROJECT_ID = os.environ.get("GCP_PROJECT")  # Your Google Cloud Project ID
LOCATION = os.environ.get("GCP_REGION")  # Your Google Cloud Project Region
vertexai.init(project=PROJECT_ID, location=LOCATION)

if reset := st.button("Reset Demo State"):
    reset_st_state()

if 'response' not in st.session_state:
    st.session_state['response'] = 'init'


@st.cache_resource
def load_models(name):
    """
    Load the generative models for text and multimodal generation.

    Returns:
        Tuple: A tuple containing the text model and multimodal model.
    """
    text_model_pro = GenerativeModel(name)
    multimodal_model_pro = GenerativeModel(name)
    return text_model_pro, multimodal_model_pro


def get_gemini_pro_text_response(
    model: GenerativeModel,
    contents: str,
    generation_config: GenerationConfig,
    stream: bool = True,
):
    safety_settings = {
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    }

    responses = model.generate_content(
        prompt,
        generation_config=generation_config,
        safety_settings=safety_settings,
        stream=stream,
    )

    final_response = []
    for response in responses:
        try:
            # st.write(response.text)
            final_response.append(response.text)
        except IndexError:
            # st.write(response)
            final_response.append("")
            continue
    return " ".join(final_response)


def get_gemini_pro_vision_response(
    model, prompt_list, generation_config={}, stream: bool = True
):
    generation_config = {"temperature": 0.1, "max_output_tokens": 2048}
    responses = model.generate_content(
        prompt_list, generation_config=generation_config, stream=stream
    )
    final_response = []
    for response in responses:
        try:
            final_response.append(response.text)
        except IndexError:
            pass
    return "".join(final_response)


st.header("Sprint from Image", divider="rainbow")


model_name = st.radio(
      label="Model:",
      options=["gemini-experimental", "gemini-1.5-pro-001", "gemini-1.5-flash-001"],
      captions=["Gemini Pro Experimental", "Gemini Pro 1.5", "Gemini Flash 1.5"],
      key="model_name",
      index=0,
      horizontal=True)

story_lang = st.radio(
    "Select the language to be used for the story generation: \n\n",
    ["Portuguese", "Spanish", "English"],
    key="story_lang",
    horizontal=True,
)

text_model_pro, multimodal_model_pro = load_models(model_name)

st.divider()

st.subheader("Image description", divider="blue")

image1 = Part.from_uri(
    mime_type="image/png",
    uri="gs://convento-samples/tela-login.png")
prompt = f""" All the answers should be provided in {story_lang}
            Explique essa tela de login no formato de plano de teste para uma história de usuário. \n
            Essa descrição vai ser utilizado para backlog de desenvolvimento."""


st.markdown( """Gemini Pro can provide a description for any media""" )
st.markdown(""" We need to do this step by step. We are going to be using the same image and a set of different prompts for each step. \n
            Button order:
            1. Generate
            2. Generate Test Case
            3. Generate Script Plan
            4. Generate playwright Script """)
uri = "gs://convento-samples/tela-login.png"
img_desc_url = ("https://storage.googleapis.com/" + uri.split("gs://")[1])

st.image(img_desc_url, width=300)

img_description = st.button(
        "Generate", key="img_description"
    )
if img_description:
    tab1, tab2 = st.tabs(["Response", "Prompt"])
    with tab1:
        if img_description and prompt:
            with st.spinner(
                "Generating image description using Gemini Pro..."
            ):
                response = get_gemini_pro_vision_response(
                multimodal_model_pro, [prompt, image1]
            )
            st.markdown(response)
            st.markdown("\n\n\n")
            st.session_state["response"] = response
    with tab2:
        st.write("Prompt used:")
        st.write(prompt)

st.subheader("Gerar test case", divider="green")
generate_test_case = st.button("Generate Test Case", key="generate_test_case")
if generate_test_case:
    with st.spinner("Generating your test cases using Gemini..."):
        first_tab1, first_tab2= st.tabs(["Code", "Prompt"])
        with first_tab1:
            promptTest = f""" All the answers should be provided in {story_lang}
            Use o conteúdo da imagem mais a descrição gerada para criar um test case para um sprint que está sendo planejado
            Descrição gerada: \n
            """ + "\n" + st.session_state["response"]
            if promptTest:
                response = get_gemini_pro_vision_response( multimodal_model_pro, [promptTest, image1])
                st.markdown(response)
                st.markdown("\n\n\n")
        with first_tab2:
            st.write("Prompt used:")
            st.write(promptTest)

st.subheader("Gerar script de execução do test plan", divider="red")
generate_test_case_code = st.button("Generate Script Plan", key="generate_test_case_code")
if generate_test_case_code:
    with st.spinner("Generating your test cases code using Gemini..."):
        first_tab1, first_tab2= st.tabs(["Code", "Prompt"])
        with first_tab1:
            promptTestCode = f""" All the answers should be provided in {story_lang}
            Use o conteúdo da imagem mais o plano de testes para criar scritps para testar durante o sprint planejado
            Teste plan gerado: \n
            """ + "\n" + st.session_state["response"]
            if promptTestCode:
                response = get_gemini_pro_vision_response( multimodal_model_pro, [promptTestCode, image1])
                st.markdown(response)
                st.markdown("\n\n\n")
        with first_tab2:
            st.write("Prompt used:")
            st.write(promptTestCode)

st.subheader("Gerar script playwright dos test case", divider="violet")
generate_playwright = st.button("Generate playwright Code", key="generate_playwright")
if generate_playwright:
    with st.spinner("Generating your test cases code using Gemini..."):
        first_tab1, first_tab2= st.tabs(["Code", "Prompt"])
        with first_tab1:
            promptplaywright = f""" All the answers should be provided in {story_lang}
            Use o conteúdo da imagem mais o plano de testes para criar um script playwright para automatizar os testes
            Scripts gerados: \n
            """ + "\n" + st.session_state["response"]
            if promptplaywright:
                response = get_gemini_pro_vision_response( multimodal_model_pro, [promptplaywright, image1])
                st.markdown(response)
                st.markdown("\n\n\n")
        with first_tab2:
            st.write("Prompt used:")
            st.write(promptplaywright)