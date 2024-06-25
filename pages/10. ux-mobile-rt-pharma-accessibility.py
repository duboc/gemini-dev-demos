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

You are evaluating an online mobile pharmacy store's app using the video recording provided, specifically focusing on accessibility for users with disabilities. Your goal is to identify barriers and suggest improvements to make the app more inclusive and usable for everyone, particularly in the context of purchasing medication and managing prescriptions.

Focus on the following key areas:

Accessibility Guidelines Compliance:

WCAG 2.1: Assess the app's adherence to Web Content Accessibility Guidelines (WCAG) 2.1 success criteria (levels A, AA, AAA), especially those relevant to healthcare information and transactions.
Screen Reader Compatibility: Evaluate how well the app works with screen readers. Are prescription details, drug information, and dosage instructions read clearly and accurately? Are interactive elements like refill buttons easily accessible?
Keyboard Navigation: Can all functionalities, including searching for medications, refilling prescriptions, and managing payment information, be accessed and used solely with a keyboard?
Color Contrast: Analyze the color contrast of important elements like prescription details, drug warnings, and dosage information. Are they sufficient for users with low vision or color blindness?
Interaction Design for Accessibility in the Pharmacy Context:

Touch Target Size: Are interactive elements like "Add to Cart," "Refill," and dosage selection buttons large enough for users with motor impairments? Consider the precision needed for selecting specific quantities.
Clear Instructions and Feedback: Are instructions for uploading prescriptions, setting reminders, and managing refills clear and easy to understand, especially for users with cognitive disabilities or who may be unfamiliar with technology?
Alternative Input Methods: Does the app support alternative input methods like dictation or voice commands for searching medications or filling out forms?
Visual and Auditory Accessibility for Medication Management:

Text Alternatives: Are descriptive text alternatives provided for images of medication packaging or instructional diagrams?
Prescription Details: Is the prescription information (medication name, dosage, instructions) presented in a clear, easy-to-read format, with options for enlarging text?
Refill Reminders: Are refill reminders available in multiple formats (e.g., visual notifications, text messages, emails) to accommodate different user preferences and needs?
Medication Interactions: If the app provides information about drug interactions, is this information clearly presented and accessible to users with different disabilities?
Deliverables:

Accessibility Barriers Log (Table):
Timestamp	Barrier Type	Description	WCAG Success Criterion (if applicable)	Severity (AAA_High/AA_Medium/A_Low)	Recommendation
1:12	Color Contrast	Dosage instructions have insufficient contrast against the background.	1.4.3 Contrast (Minimum)	AAA_High	Increase color contrast to meet WCAG standards, ensuring critical information is legible.
2:48	Screen Reader	Drug interaction warnings not announced by screen reader.	1.3.1 Info and Relationships	AAA_High	Ensure all critical alerts and warnings are programmatically associated and announced by screen readers.
3:22	Touch Target Size	Refill button too small and close to other buttons, difficult to tap accurately.	2.5.5 Target Size	AA_Medium	Increase the size of the button and provide more spacing between interactive elements.

Overall Assessment:

Provide a concise summary of the app's overall strengths and weaknesses in terms of accessibility for users with disabilities who need to manage medications and prescriptions. Offer prioritized recommendations to improve the app's accessibility, ensuring it meets the unique needs of this user group. Reference WCAG 2.1 success criteria where applicable.
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


