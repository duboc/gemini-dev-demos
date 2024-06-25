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

def load_vertex(region):
    PROJECT_ID = os.environ.get("GCP_PROJECT")  # Your Google Cloud Project ID
    LOCATION = os.environ.get(f"{region}")  # Your Google Cloud Project Region
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
    generation_config = {"temperature": 0.1, "max_output_tokens": 8192}
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


st.header("Generate UX Friction Log", divider="rainbow")

st.markdown("""

This demonstration showcases the capabilities of our Gemini Models aiming to analyze the user experience (UX) of a website by capturing user actions and providing visual aids. 
Our main idea is to allow a deeper understanding of the website's usability and identifies areas where improvements can be made to enhance the user's interaction with the site. 
The friction log generated from this process can be used to pinpoint pain points in the UX and suggest solutions to create a smoother and more intuitive user experience.
""")


model_region = st.radio(
    "Select the Gemini region to be used: \n\n",
    ["us-central1", "southamerica-east1", "us-east1", "us-south1", "europe-southwest1"],
    key="model_region",
    horizontal=True,
)

load_vertex(model_region)
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
vide_desc_uri = "gs://convento-samples/nike-sbf.mp4"
video_desc_url = ("https://storage.googleapis.com/" + vide_desc_uri.split("gs://")[1])
st.video(video_desc_url)

st.subheader("Friction Log", divider="green")
generate_selenium = st.button("Criar friction log", key="generate_selenium")
if generate_selenium:
    with st.spinner("Generating your friction log using Gemini..."):
        first_tab1, first_tab2= st.tabs(["Code", "Prompt"])
        with first_tab1:
            promptSelenium = f""" All the answers are to be provided in {story_lang}
You are evaluating the Nike online store's mobile app using the video recording provided of a user interacting with the app. Your goal is to identify specific issues and improvement opportunities within the user experience (UX) to make the app more accessible to users with disabilities.

Focus on the following key areas:

Accessibility Guidelines Compliance:

WCAG 2.1: Does the app meet the Web Content Accessibility Guidelines (WCAG) 2.1 success criteria?
Screen Reader Compatibility: Is the app navigable and understandable using a screen reader?
Keyboard Navigation: Can all functionalities be accessed and used with a keyboard alone?
Visual Design and Layout:

Color Contrast: Is there sufficient contrast between text and background colors?
Font Size and Readability: Are fonts legible and can the size be adjusted?
Touch Target Size: Are interactive elements (buttons, links) large enough to be easily tapped?
Navigation and Interaction:

Clear Focus Indicators: Are focus states visually apparent for keyboard users?
Alternative Text for Images: Do images have descriptive alternative text for screen reader users?
Form Labeling: Are form fields clearly labeled and programmatically associated with their labels?
Error Identification: Are error messages clear and easy to understand?
Additional Considerations:

Captioning and Transcripts: Are videos captioned and/or have transcripts available?
Voice Control: Can the app be controlled using voice commands?

Overall Assessment:

Provide a concise summary of the app's overall accessibility strengths and weaknesses.
Offer specific, actionable recommendations for improving the app's accessibility, referencing WCAG guidelines and best practices where applicable.

Example table:
Timestamp	Issue Description	WCAG Reference	Severity	Recommendation
0:35	Insufficient color contrast between text and background on the product page	1.4.3	Medium	Increase contrast ratio to meet WCAG AA standards
1:12	Missing alternative text for product image	1.1.1	High	Add descriptive alt text to convey the image content to screen reader users
2:48	Small touch target size for "Add to Cart" button	2.5.5	Low	Increase the button's touch target size to 44x44 pixels minimum

            """
            vide_desc_img = Part.from_uri(vide_desc_uri, mime_type="video/mp4")
            if promptSelenium:
                response = get_gemini_pro_vision_response( multimodal_model_pro, [promptSelenium, vide_desc_img])
                st.session_state["selenium"] = response
                st.markdown(response)
                print(response)
                st.markdown("\n\n\n")
        with first_tab2:
            st.write("Prompt used:")
            st.write(promptSelenium)


st.subheader("User Story", divider="green")
generate_user_story = st.button("Criar user story log", key="generate_user_story")
if generate_user_story:
    with st.spinner("Generating your user story using Gemini..."):
        first_tab1, first_tab2= st.tabs(["Code", "Prompt"])
        with first_tab1:
            promptUserStory = f""" All the answers are to be provided in {story_lang} 
                    Group the friction log that are similar into a user story, present with a table.

                    **Input:**

                    * **Task:** The user's goal
                    * **Friction Point:** The specific obstacle
                    * **Severity:** High, Medium, or Low
                    * **Recommendation:** Proposed solution

                    **Output:**

                    1. **User Story Format:**  Concise user stories following this template:
                       * "As a [type of user], I want to [action] so that [benefit]." 

                    2. **Prioritization:**  Rank the user stories based on the severity of the friction points in the log.

                    3. **Additional Details:** Optionally, include details about the friction point and recommended solution from the log to give context to the development team.

                    **Example of Detailed User Story:**

                    * **Priority:** High
                    * **User Story:** "As a customer, I want to refill my prescriptions with one click so that I can save time."
                    * **Details:** Currently, refilling a prescription requires the user to scroll through past orders, which is time-consuming. A "Refill" button should be added directly to the order details screen.


            """ + "\n" + st.session_state["selenium"]
            vide_desc_img = Part.from_uri(vide_desc_uri, mime_type="video/mp4")
            if promptUserStory:
                responseStory = get_gemini_pro_vision_response( multimodal_model_pro, [promptUserStory, vide_desc_img])
                st.markdown(responseStory)
                print(responseStory)
                st.markdown("\n\n\n")
        with first_tab2:
            st.write("Prompt used:")
            st.write(promptUserStory)


