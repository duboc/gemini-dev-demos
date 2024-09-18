import streamlit as st
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
    PROJECT_ID = os.environ.get("GCP_PROJECT")
    LOCATION = os.environ.get(f"{region}")
    vertexai.init(project=PROJECT_ID, location=LOCATION)

@st.cache_resource
def load_models(name):
    text_model_pro = GenerativeModel(name)
    multimodal_model_pro = GenerativeModel(name)
    return text_model_pro, multimodal_model_pro

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


# Custom CSS to resize the video
st.markdown("""
    <style>
    .stVideo {
        width: 400px !important;
        height: auto !important;
        margin: 0 auto;
    }

    </style>

    """, unsafe_allow_html=True)

st.title("UX Heuristic Analysis using Gemini AI")

st.markdown("""
This demo showcases the power of Gemini AI in analyzing user experience (UX) based on Nielsen's 10 Usability Heuristics. 
By examining video recordings of user interactions with mobile apps, we can identify usability issues and suggest improvements.

**How it works:**
1. Select your preferences (model, region, language, and use case).
2. Generate a UX Friction Log based on the selected video.
3. Create User Stories from the Friction Log to prioritize improvements.

Let's get started!
""")

# Initialize session state variables
if 'friction_log' not in st.session_state:
    st.session_state['friction_log'] = None
if 'user_stories' not in st.session_state:
    st.session_state['user_stories'] = None
if 'friction_log_state' not in st.session_state:
    st.session_state['friction_log_state'] = 'Ready'
if 'user_stories_state' not in st.session_state:
    st.session_state['user_stories_state'] = 'Ready'

col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    model_region = st.selectbox(
        "Select Gemini region:",
        ["us-central1", "southamerica-east1", "us-east1", "us-south1", "europe-southwest1"],
        key="model_region",
    )

    model_name = st.selectbox(
        "Select Gemini model:",
        ["gemini-experimental", "gemini-1.5-pro-001", "gemini-1.5-flash-001"],
        key="model_name",
        index=0,
    )

with col2:
    story_lang = st.selectbox(
        "Select output language:",
        ["Portuguese", "Spanish", "English"],
        key="story_lang",
    )

    use_case = st.selectbox(
        "Select use case:",
        ["Bank of Anthos", "Hipster Shop"],
        key="use_case",
    )

load_vertex(model_region)
text_model_pro, multimodal_model_pro = load_models(model_name)

if use_case == "Bank of Anthos":
    video_uri = "gs://convento-samples/boa-mobile.mp4"
    heuristic_prompt = """You are reviewing a video recording of a user interacting with the Bank of Anthos online banking mobile app. Your objective is to conduct a thorough UX evaluation using Nielsen's 10 Usability Heuristics as a framework, pinpointing specific areas where the app excels and where it could be improved. Focus on the following key areas, aligning your analysis with Nielsen's principles:

1. Visibility of System Status
2. Match Between System and the Real World
3. User Control and Freedom
4. Consistency and Standards
5. Error Prevention
6. Recognition Rather Than Recall
7. Flexibility and Efficiency of Use
8. Aesthetic and Minimalist Design
9. Help Users Recognize, Diagnose, and Recover from Errors
10. Help and Documentation

Provide a detailed analysis for each heuristic, including specific examples from the video.
"""
else:
    video_uri = "gs://convento-samples/hipster-mobile.mp4"
    heuristic_prompt = """You are reviewing a video recording of a user interacting with a Brazilian retailer for mobile Hipster Shop store app. Your objective is to conduct a thorough UX evaluation using Nielsen's 10 Usability Heuristics as a framework, pinpointing specific areas where the app excels and where it could be improved, considering the Brazilian context. Focus on the following key areas, aligning your analysis with Nielsen's principles:

1. Visibility of System Status
2. Match Between System and the Real World
3. User Control and Freedom
4. Consistency and Standards
5. Error Prevention
6. Recognition Rather Than Recall
7. Flexibility and Efficiency of Use
8. Aesthetic and Minimalist Design
9. Help Users Recognize, Diagnose, and Recover from Errors
10. Help and Documentation

Provide a detailed analysis for each heuristic, including specific examples from the video and considering the Brazilian context.
"""

video_url = ("https://storage.googleapis.com/" + video_uri.split("gs://")[1])

st.subheader("Video for Analysis")
st.video(video_url)

col1, col2 = st.columns(2)

with col1:
    friction_log_button = st.button(
        f"Generate UX Friction Log ({st.session_state['friction_log_state']})",
        disabled=(st.session_state['friction_log_state'] == 'Running')
    )
    if friction_log_button:
        st.session_state['friction_log_state'] = 'Running'
        with st.spinner("Analyzing video and generating friction log..."):
            prompt = f"All answers should be provided in {story_lang}. {heuristic_prompt}"
            video_part = Part.from_uri(video_uri, mime_type="video/mp4")
            try:
                response = get_gemini_pro_vision_response(multimodal_model_pro, [prompt, video_part])
                st.session_state['friction_log'] = response
                st.session_state['friction_log_state'] = 'Completed'
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.session_state['friction_log_state'] = 'Ready'

with col2:
    user_stories_button = st.button(
        f"Generate User Stories ({st.session_state['user_stories_state']})",
        disabled=(st.session_state['user_stories_state'] == 'Running' or st.session_state['friction_log'] is None)
    )
    if user_stories_button:
        if st.session_state['friction_log'] is None:
            st.warning("Please generate the UX Friction Log first.")
        else:
            st.session_state['user_stories_state'] = 'Running'
            with st.spinner("Creating user stories from the friction log..."):
                user_story_prompt = f"""All answers should be provided in {story_lang}.
                Group the friction log items that are similar into user stories, presented in a table format.

                For each user story, provide:
                1. Priority (High, Medium, or Low)
                2. User Story in the format: "As a [type of user], I want to [action] so that [benefit]."
                3. Details about the friction point and recommended solution

                Rank the user stories based on the severity of the friction points in the log.
                """
                try:
                    user_story_response = get_gemini_pro_vision_response(multimodal_model_pro, [user_story_prompt, st.session_state['friction_log']])
                    st.session_state['user_stories'] = user_story_response
                    st.session_state['user_stories_state'] = 'Completed'
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                    st.session_state['user_stories_state'] = 'Ready'

tab1, tab2 = st.tabs(["UX Friction Log", "User Stories"])

with tab1:
    if st.session_state['friction_log']:
        st.markdown("## UX Friction Log")
        st.markdown(st.session_state['friction_log'])
    else:
        st.info("Generate the UX Friction Log to see the results here.")

with tab2:
    if st.session_state['user_stories']:
        st.markdown("## User Stories")
        st.markdown(st.session_state['user_stories'])
    else:
        st.info("Generate User Stories to see the results here.")

st.markdown("---")
st.markdown("Made with ❤️ using Streamlit and Gemini AI")