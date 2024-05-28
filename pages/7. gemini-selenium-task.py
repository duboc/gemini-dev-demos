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


st.header("Generate User Test with Selenium", divider="rainbow")

st.markdown("""
This demonstration showcases the capabilities of our Gemini Models. 
            
In this example, you'll witness how it can:

- Analyze Videos: Understand the actions taking place in a video.
- Generate Descriptions: Create detailed text descriptions of video content.
- Craft Code: Automatically generate code based on a video and description.
            
This demo focuses on creating a Selenium script, a powerful tool for automating web browser interactions.

Feel free to explore and see how this technology can assist you in your coding endeavors! :rocket:
""")

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

prompt = ""

st.divider()

st.markdown( """Gemini Pro Vision can also provide the description of what is going on in the video:""" )
vide_desc_uri = "gs://convento-samples/boa-selenium-rag.mov"
video_desc_url = ("https://storage.googleapis.com/" + vide_desc_uri.split("gs://")[1])

if vide_desc_uri:
    vide_desc_img = Part.from_uri(vide_desc_uri, mime_type="video/mp4")
    st.video(video_desc_url)
    st.write("Our expectation: Generate the description of the video")
    prompt = f"""Describe what is happening in the video and answer the following questions: \n


            **Context:** I have a video showcasing a series of tasks being performed on a web browser. I need a detailed description of each action taken. 

            **Input:** [video_data]

            **Output:**

            * **Timestamped list of actions:** Provide a list of actions taken in the video, along with their timestamps (e.g., "0:10 - User clicks the 'Sign In' button.").
            * **Detailed description:** For each action, provide a clear and concise description of what is happening. Include:
                    * **What is being clicked/selected/typed?**
                    * **What is the purpose of the action?**
                    * **Any relevant context or information displayed on the screen.**
            * **Visual aids:** If possible, include annotations of the video to help visualize the actions.

            **Example:**

                **Timestamp:** 0:10
                **Action:** User clicks the "Sign In" button.
                **Description:** The user clicks the blue "Sign In" button located in the top right corner of the screen. This action initiates the login process.

            **Additional notes:**

                * **Focus on user interactions:** The description should focus on the user's actions and the visible results on the screen.
                * **Avoid technical jargon:** Use clear and simple language that anyone can understand.
                * **Pay attention to details:** Capture all relevant information, including specific button names, website URLs, and any error messages.

                **Please note:** The more detailed and accurate your description is, the more helpful it will be for me to understand the video.
            All the answers should be provided in {story_lang}
            """
    tab1, tab2 = st.tabs(["Response", "Prompt"])
    vide_desc_description = st.button(
        "Generate", key="vide_desc_description"
    )
    with tab1:
        if vide_desc_description and prompt:
            with st.spinner(
                "Generating video description using Gemini Pro..."
            ):
                response = get_gemini_pro_vision_response(
                    multimodal_model_pro, [prompt, vide_desc_img]
                )
                st.markdown(response)
                st.markdown("\n\n\n")
                st.session_state["response"] = response
    with tab2:
        st.write("Prompt used:")
        st.write(prompt, "\n", "{video_data}")

st.divider()
generate_selenium = st.button("Criar selenium", key="generate_selenium")
if generate_selenium:
    with st.spinner("Generating your selenium code using Gemini..."):
        first_tab1, first_tab2= st.tabs(["Code", "Prompt"])
        with first_tab1:
            promptSelenium = """use the content in the video plus the description to create a selenium script to automate the task""" + "\n" + st.session_state["response"]
            vide_desc_img = Part.from_uri(vide_desc_uri, mime_type="video/mp4")
            if promptSelenium:
                response = get_gemini_pro_vision_response( multimodal_model_pro, [promptSelenium, vide_desc_img])
                st.markdown(response)
                st.markdown("\n\n\n")
        with first_tab2:
            st.write("Prompt used:")
            st.write(promptSelenium, "\n", "{video_data}")