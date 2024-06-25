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
You are reviewing a video recording of a user interacting with a Brazilian online mobile pharmacy store app. Your objective is to conduct a thorough UX evaluation using Nielsen's 10 Usability Heuristics as a framework, pinpointing specific areas where the app excels and where it could be improved, considering the Brazilian context. Focus on the following key areas, aligning your analysis with Nielsen's principles:

Visibility of System Status:
Heuristic: Does the app keep users informed about what's happening (e.g., order processing, prescription validation with ANVISA) through appropriate feedback within reasonable time, considering potential network limitations in Brazil?
Analysis: Assess loading indicators, progress bars, confirmation messages (in Portuguese), and any communication of system status in the video. Note instances where feedback is lacking or unclear, especially during critical actions like prescription submissions and deliveries.
Match Between System and the Real World:
Heuristic: Does the app speak the users' language (Brazilian Portuguese), use familiar pharmacy terminology, and follow real-world conventions related to pharmacies and healthcare in Brazil?
Analysis: Evaluate whether terminology (e.g., medication names, dosage instructions, ANVISA-related terms), icons, and overall presentation are culturally relevant and intuitive for Brazilian users. Look for inconsistencies or medical jargon that might confuse users.
User Control and Freedom:
Heuristic: Does the app offer clearly marked "emergency exits" (e.g., canceling an order before it's processed by the pharmacy) and ways to undo actions, considering the potential for errors in prescription entry?
Analysis: Observe if the user can easily navigate back, cancel actions, or exit processes, particularly during sensitive tasks like entering personal health information (CPF), prescription details, or payment methods common in Brazil (e.g., Pix, boleto).
Consistency and Standards:
Heuristic: Does the app adhere to platform conventions (iOS/Android), Brazilian design trends, and maintain consistency within itself regarding healthcare information display and interactions?
Analysis: Compare the app's design and interactions to standard patterns, but also consider local design preferences. Check for consistency in terminology (e.g., "receita médica" vs. "prescrição"), layout, and visual elements throughout the app, especially across sections like medication lists, health records, and delivery tracking.
Error Prevention:
Heuristic: Does the app proactively prevent errors from occurring, especially with critical data like prescriptions, CPF, and personal information, taking into account potential input errors in Brazilian Portuguese?
Analysis: Look for input validation (e.g., dosage limits, interaction checks, CPF validation), clear instructions for prescription uploads (considering different formats used in Brazil), and safeguards against accidental actions. Note any error messages and how effectively they guide the user towards resolution, ensuring they are in clear, concise Portuguese.
Recognition Rather Than Recall:
Heuristic: Does the app minimize the user's memory load by making objects, actions, and options (e.g., medication history, refill options, common Brazilian medications) visible?
Analysis: Assess how easily the user can find information or complete tasks without remembering previous steps. Evaluate the clarity of menus, labels (in Portuguese), and navigation, particularly for features like medication refills, order tracking, and accessing common medications used in Brazil.
Flexibility and Efficiency of Use:
Heuristic: Does the app cater to both novice and experienced users, considering varying levels of health literacy and tech proficiency in Brazil, and offer options relevant to the Brazilian healthcare system?
Analysis: Look for shortcuts (e.g., quick refills of common medications), personalization options (e.g., medication reminders based on Brazilian time zones), and ways to streamline repeated actions. Consider if the app accommodates different user needs, such as easy prescription uploads for older adults or clear dosage instructions in Portuguese for those with visual impairments. Consider options like integrating with the Brazilian public healthcare system (SUS) or offering features to locate nearby pharmacies.
Aesthetic and Minimalist Design:
Heuristic: Does the app present information clearly, especially health-related data, and avoid irrelevant clutter, while aligning with Brazilian design preferences?
Analysis: Evaluate the overall visual design, ensuring it's appropriate for a healthcare context and culturally relevant to Brazil. Consider the use of whitespace, typography (legible for medication names and instructions in Portuguese), and visual hierarchy. Note any distracting elements or information overload, particularly in sections displaying critical health information.
Help Users Recognize, Diagnose, and Recover from Errors:
Heuristic: Are error messages clear, precise, and constructive in Brazilian Portuguese, especially when dealing with sensitive actions like prescription refills or personal data entry?
Analysis: Assess how the app communicates errors to the user in clear Portuguese. Check if error messages provide specific solutions or helpful guidance, such as contacting customer support for prescription issues or offering alternative ways to complete a task.
Help and Documentation:
Heuristic: Does the app provide easy access to help and documentation relevant to pharmacy services and healthcare needs specific to Brazil?
Analysis: Look for help sections, FAQs specific to medication usage in Brazil, insurance coverage details relevant to the Brazilian healthcare system, tutorials for prescription refills, or any resources that assist the user with their healthcare needs in the Brazilian context. Note how easy it is to find and access these resources in Portuguese.
Deliverables:

UX Friction Log (Table): Use the format provided in the original prompt to document specific issues and recommendations, tailoring them to the Brazilian context.
Overall Assessment: Summarize the app's strengths and weaknesses based on your heuristic evaluation, emphasizing aspects relevant to healthcare apps in Brazil. Provide actionable recommendations for improvement, focusing on how these changes would enhance the user experience for Brazilian users with varying health literacy and tech proficiency, while considering the specific needs and preferences of the Brazilian market.
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


