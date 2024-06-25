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
You are evaluating the Nike online store's mobile app using the video recording provided of a user interacting with the app. Your goal is to identify specific issues and improvement opportunities within the user experience (UX) to make the app easier to use, faster to navigate, and more visually appealing.

Focus on the following key areas:

Task Flow (Efficiency and Clarity):
How smooth and intuitive is the process of completing key tasks (e.g., browsing products, filtering search results, adding items to cart, checking out)?
Are there any unnecessary steps, confusing navigation, or dead ends that hinder the user's progress?
Interaction Design (Usability and Responsiveness):
Are the buttons, icons, and touch targets appropriately sized and easy to tap?
Do the interactive elements provide clear feedback when tapped or swiped?
Are animations and transitions smooth and meaningful?
Information Architecture (Findability and Organization):
Is the information presented in a logical and easy-to-understand manner?
Are product categories, filters, and search results well-organized and easy to browse?
Is important information, such as pricing, sizing, and availability, clearly displayed?
Visual Design (Aesthetics and Branding):
Does the app's visual style align with Nike's brand identity?
Is the color scheme visually appealing and easy on the eyes?
Are the fonts legible and appropriate for the content?
Are high-quality images and videos used effectively to showcase products?
Deliverables:

UX Friction Log (Table):

Timestamp: Note the specific time in the video where the issue occurs.
Task: The specific action the user is trying to accomplish.
Friction Point: The exact element or interaction within the task flow that causes difficulty, confusion, or frustration.
Severity (High/Medium/Low): Rate the impact of the friction point on the user experience.
Recommendation: Suggest a specific change or improvement to address the friction point, using visuals (screenshots from the video or mockups) when possible.
Overall Assessment:

Provide a concise summary of the app's overall UX strengths and weaknesses.
Offer recommendations for how the app could be improved to enhance the user experience and better align with Nike's brand.

Example Table:

Timestamp	Task	Friction Point	Severity	Recommendation
0:35	Browse running shoes	Filter options are hidden behind a small icon.	Medium	Make filter options more prominent and easily accessible.
1:12	Add item to cart	Add to cart button blends in with the background.	Low	Use a more contrasting color for the button.
2:48	Checkout	Too many steps in the checkout process.	High	Streamline the checkout process by reducing the number of steps.
3:22	View product details	Important information is below the fold.	Medium	Prioritize key information and make it visible without scrolling.

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


