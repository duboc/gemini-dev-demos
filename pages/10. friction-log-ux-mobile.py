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
      options=["gemini-experimental", "gemini-1.5-pro-preview-0514", "gemini-1.5-flash-preview-0514"],
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
vide_desc_uri = "gs://convento-samples/raia.mp4"
video_desc_url = ("https://storage.googleapis.com/" + vide_desc_uri.split("gs://")[1])
st.video(video_desc_url)

st.subheader("Friction Log", divider="green")
generate_selenium = st.button("Criar friction log", key="generate_selenium")
if generate_selenium:
    with st.spinner("Generating your friction log using Gemini..."):
        first_tab1, first_tab2= st.tabs(["Code", "Prompt"])
        with first_tab1:
            promptSelenium = f""" All the answers are to be provided in {story_lang}
**Prompt for UX Friction Log**

**Context:**

You're evaluating a mobile app for an online pharmacy. Your goal is to identify specific areas where the user experience (UX) could be improved. Focus on the following key aspects:

* **Task Flow:**  Analyze the steps users take to complete common actions (e.g., search for a medication, refill a prescription, check order status).
* **Interaction Design:** Evaluate how easy it is to use buttons, menus, forms, and other interactive elements.
* **Information Architecture:** Assess how information is organized and presented (e.g., product listings, prescription details, account settings).
* **Visual Design:** Consider if the app's visual appearance is clear, aesthetically pleasing, and supports usability.

**Deliverable:**

1. **UX Friction Log (Table):**
   * **Task:**  The specific action the user is trying to accomplish.
   * **Friction Point:** The exact step or element within the task flow that causes difficulty, confusion, or frustration.
   * **Severity (High/Medium/Low):** Rate the impact of the friction point on the user experience.
   * **Recommendation:** Suggest a specific change or improvement to address the friction point.

2. **Optional (but valuable):** Include screenshots or screen recordings to illustrate friction points. 

**Example Table:**

| Task                          | Friction Point                                           | Severity | Recommendation                                                                    |
| ----------------------------- | --------------------------------------------------------- | -------- | ------------------------------------------------------------------------------- |
| Search for medication        | Search bar is not easily visible on the home screen.          | Medium   | Place the search bar prominently at the top of the home screen.                 |
| Refill a prescription       | Process requires excessive scrolling through past orders. | High    | Add a direct "Refill" button on the order details screen.                       |
| Check order status           | Confusing navigation to the order status page.              | Low     | Add a clear "Order Status" link in the main navigation menu.                    |
| View medication details     | Important dosage information is buried in small text.        | Medium   | Display dosage prominently near the top of the medication details screen.     |



**Why This Prompt is Improved:**

* **Clearer Focus:** The prompt explicitly outlines the areas of UX to analyze.
* **Actionable Output:** The table format ensures that the friction log is organized and easy for the development team to act on.
* **Prioritization:** The severity rating helps identify the most critical issues.

            """
            vide_desc_img = Part.from_uri(vide_desc_uri, mime_type="video/mp4")
            if promptSelenium:
                response = get_gemini_pro_vision_response( multimodal_model_pro, [promptSelenium, vide_desc_img])
                st.session_state["selenium"] = response
                st.markdown(response)
                st.markdown("\n\n\n")
        with first_tab2:
            st.write("Prompt used:")
            st.write(promptSelenium)


st.subheader("User Story", divider="green")
generate_user_story = st.button("Criar user story log", key="generate_user_story")
output_type = st.radio(
            "Select the output type",
            ["text", "table", "json"],
            key="output_type",
            horizontal=True,
        )
if generate_user_story:
    with st.spinner("Generating your user story using Gemini..."):
        first_tab1, first_tab2= st.tabs(["Code", "Prompt"])
        with first_tab1:
            promptUserStory = f""" All the answers are to be provided in {story_lang} 
            Resuma o friction log em uma lista de user story. Crie quantas forem necessárias. 
                Write a User story based on the following premise: \n
                persona_name: [persona_name] \n
                persona_type: [persona_type] \n
                user_story: [user_story] \n
                 First start by giving the user Story an Summary: [concise, memorable, human-readable story title] 
             User Story Format example:
                As a: [Suggest a persona]
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
            Coloque o resultado no formato de {output_type} """ + "\n" + st.session_state["selenium"]
            vide_desc_img = Part.from_uri(vide_desc_uri, mime_type="video/mp4")
            if promptUserStory:
                response = get_gemini_pro_vision_response( multimodal_model_pro, [promptUserStory, vide_desc_img])
                st.markdown(response)
                st.markdown("\n\n\n")
        with first_tab2:
            st.write("Prompt used:")
            st.write(promptUserStory)


