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
prompt = f""" 
            Explique essa tela de login no formato de implementação de features para uma história de usuário. \n
            Essa descrição vai ser utilizado para backlog de desenvolvimento para criação de frontend, backend e o plano de deploy no Google CLoud.
            All the answers should be provided in {story_lang}
            """


st.markdown( """Gemini Pro can provide a description for any media""" )
st.markdown(""" We need to do this step by step. We are going to be using the same image and a set of different prompts for each step. \n
            Button order:
            1. Generate
            2. Generate Backend 
            3. Generate Frontend 
            4. Generate Google Cloud Deployment""")
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

st.subheader("Gerar Backend", divider="green")
generate_backend = st.button("Generate Backend", key="generate_backend")
if generate_backend:
    with st.spinner("Generating your backend code using Gemini..."):
        first_tab1, first_tab2= st.tabs(["Code", "Prompt"])
        with first_tab1:
            promptBackend = f""" All the answers should be provided in {story_lang}
            Use o conteúdo da imagem mais a descrição gerada para criar uma implementação de backend utilizando flask e python para um sprint que está sendo planejado
            Descrição gerada: \n
            """ + "\n" + st.session_state["response"]
            if promptBackend:
                response = get_gemini_pro_vision_response( multimodal_model_pro, [promptBackend, image1])
                st.markdown(response)
                st.markdown("\n\n\n")
                st.session_state["backend"] = response
        with first_tab2:
            st.write("Prompt used:")
            st.write(promptBackend)

st.subheader("Gerar frontend", divider="red")
generate_frontend = st.button("Generate Frontend", key="generate_frontend")
if generate_frontend:
    with st.spinner("Generating your frontend code using Gemini..."):
        first_tab1, first_tab2= st.tabs(["Code", "Prompt"])
        with first_tab1:
            promptFrontend = f""" All the answers should be provided in {story_lang}
            Use o conteúdo da imagem mais o código do backend para melhorar implementar o frontend para a aplicação
            Código Backend gerado: \n
            """ + "\n" + st.session_state["backend"]
            if promptFrontend:
                response = get_gemini_pro_vision_response( multimodal_model_pro, [promptFrontend, image1])
                st.markdown(response)
                st.markdown("\n\n\n")
                st.session_state["frontend"] = response
        with first_tab2:
            st.write("Prompt used:")
            st.write(promptFrontend)

st.subheader("Gerar Deployment Google CLoud", divider="violet")
generate_gcloud = st.button("Generate Google Cloud Deployment", key="generate_gcloud")
if generate_gcloud:
    with st.spinner("Generating your Google Cloud scripts Gemini..."):
        first_tab1, first_tab2= st.tabs(["Code", "Prompt"])
        with first_tab1:
            promptGcloud = f""" All the answers should be provided in {story_lang}
            Use o conteúdo do backend e frontend para criar a melhor arquitetura de deploy para uma aplicação stateless. \n
            Utilize cloud run e algum banco de dados e escolha o mais apropriado baseado no código, e utilize o google cloud storage para guardar possíveis imagens. \n 
            O output precisa ser um terraform dentro das melhores práticas: \n
            """ + "\n" + st.session_state["response"] + "\n" + st.session_state["backend"] + "\n" + st.session_state["frontend"]
            if promptGcloud:
                response = get_gemini_pro_vision_response( multimodal_model_pro, [promptGcloud, image1])
                st.markdown(response)
                st.markdown("\n\n\n")
        with first_tab2:
            st.write("Prompt used:")
            st.write(promptGcloud)