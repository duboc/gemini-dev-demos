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


# Custom CSS to resize video, style tabs, and improve button appearance
st.markdown("""
<style>
    .stVideo {
        width: 60%;
        max-width: 800px;
        margin: auto;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #F0F2F6;
        border-radius: 4px 4px 0px 0px;
        gap: 12px;
        padding-top: 10px;
        padding-bottom: 10px;
        padding-left: 20px;
        padding-right: 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FFFFFF;
        border-bottom-color: transparent;
    }
    .stButton button:disabled {
        background-color: #cccccc;
        color: #666666;
        cursor: not-allowed;
    }
</style>
""", unsafe_allow_html=True)

def load_vertex(region):
    PROJECT_ID = os.environ.get("GCP_PROJECT")
    LOCATION = os.environ.get(f"{region}")
    vertexai.init(project=PROJECT_ID, location=LOCATION)

@st.cache_resource
def load_models(name):
    text_model_pro = GenerativeModel(name)
    multimodal_model_pro = GenerativeModel(name)
    return text_model_pro, multimodal_model_pro

def get_gemini_pro_response(model, prompt, generation_config={}, stream=True):
    generation_config = {"temperature": 0.1, "max_output_tokens": 8192}
    response = model.generate_content(prompt, generation_config=generation_config, stream=stream)
    
    if stream:
        full_response = []
        for chunk in response:
            if chunk.text:
                full_response.append(chunk.text)
                yield chunk.text
        return "".join(full_response)
    else:
        return response.text

# Initialize session state variables
if 'friction_log' not in st.session_state:
    st.session_state['friction_log'] = None
if 'user_story' not in st.session_state:
    st.session_state['user_story'] = None
if 'friction_status' not in st.session_state:
    st.session_state['friction_status'] = "Ready"
if 'user_story_status' not in st.session_state:
    st.session_state['user_story_status'] = "Ready"

st.title("UX Friction Log Generator")

st.markdown("""
This demo showcases the capabilities of our Gemini Models in analyzing user experience (UX) of websites and applications.
By capturing user actions and providing visual aids, we allow for a deeper understanding of usability and identify areas for improvement.
The generated friction log and user stories can be used to pinpoint pain points in the UX and suggest solutions for a smoother, more intuitive user experience.
""")

# Configuration section
st.header("Configuration")

col1, col2 = st.columns(2)

with col1:
    model_region = st.selectbox(
        "Select Gemini region:",
        ["us-central1", "southamerica-east1", "us-east1", "us-south1", "europe-southwest1"],
        key="model_region"
    )
    
    model_name = st.radio(
        "Select Model:",
        ["gemini-experimental", "gemini-1.5-pro-001", "gemini-1.5-flash-001"],
        key="model_name",
        index=0
    )

with col2:
    language = st.radio(
        "Select language for generation:",
        ["Portuguese", "Spanish", "English"],
        key="language"
    )
    
    use_case = st.selectbox(
        "Select use case:",
        ["E-commerce (Nike)", "Pharmacy (Raia)", "Healthcare"],
        key="use_case"
    )

# Load models and video
load_vertex(model_region)
text_model_pro, multimodal_model_pro = load_models(model_name)

video_uris = {
    "E-commerce (Nike)": "gs://convento-samples/nike-sbf.mp4",
    "Pharmacy (Raia)": "gs://convento-samples/raia.mp4",
    "Healthcare": "gs://convento-samples/friction-log.mp4"
}

selected_video_uri = video_uris[use_case]
video_url = "https://storage.googleapis.com/" + selected_video_uri.split("gs://")[1]

st.header("User Interaction Video")
st.video(video_url)

# Friction Log Generation
st.header("Analysis Generation")

friction_prompt = f"""All the answers are to be provided in {language}
You are evaluating the {use_case} application using the video recording provided of a user interacting with the app. Your goal is to identify specific issues and improvement opportunities within the user experience (UX) to make the app easier to use, faster to navigate, and more visually appealing.

Focus on the following key areas:

1. Task Flow (Efficiency and Clarity)
2. Interaction Design (Usability and Responsiveness)
3. Information Architecture (Findability and Organization)
4. Visual Design (Aesthetics and Branding)

Deliverable:

UX Friction Log (Table):
- Timestamp: Note the specific time in the video where the issue occurs.
- Task: The specific action the user is trying to accomplish.
- Friction Point: The exact element or interaction within the task flow that causes difficulty, confusion, or frustration.
- Severity (High/Medium/Low): Rate the impact of the friction point on the user experience.
- Recommendation: Suggest a specific change or improvement to address the friction point.

Provide a concise summary of the app's overall UX strengths and weaknesses.
"""

user_story_prompt = f"""All the answers are to be provided in {language} 
Based on the friction log provided, group similar items into user stories, presented in a table.

Output:
1. User Story Format: "As a [type of user], I want to [action] so that [benefit]." 
2. Prioritization: Rank the user stories based on the severity of the friction points in the log.
3. Additional Details: Include details about the friction point and recommended solution from the log to give context to the development team.

Example of Detailed User Story:
- Priority: High
- User Story: "As a customer, I want to refill my prescriptions with one click so that I can save time."
- Details: Currently, refilling a prescription requires the user to scroll through past orders, which is time-consuming. A "Refill" button should be added directly to the order details screen.
"""

if st.button("Generate Analysis", key="generate_analysis", disabled=st.session_state['friction_status'] == "Running"):
    st.session_state['friction_status'] = "Running"
    st.session_state['user_story_status'] = "Running"
    
    with st.spinner("Generating Friction Log..."):
        video_part = Part.from_uri(selected_video_uri, mime_type="video/mp4")
        friction_response = ""
        friction_placeholder = st.empty()
        for chunk in get_gemini_pro_response(multimodal_model_pro, [friction_prompt, video_part]):
            friction_response += chunk
            friction_placeholder.markdown(friction_response)
        st.session_state['friction_log'] = friction_response
    st.session_state['friction_status'] = "Completed"
    
    with st.spinner("Generating User Story..."):
        user_story_response = ""
        user_story_placeholder = st.empty()
        for chunk in get_gemini_pro_response(text_model_pro, user_story_prompt + "\n" + friction_response):
            user_story_response += chunk
            user_story_placeholder.markdown(user_story_response)
        st.session_state['user_story'] = user_story_response
    st.session_state['user_story_status'] = "Completed"

st.write(f"Friction Log Status: {st.session_state['friction_status']}")
st.write(f"User Story Status: {st.session_state['user_story_status']}")

# Display results in tabs
if st.session_state['friction_log'] and st.session_state['user_story']:
    tab1, tab2 = st.tabs(["Friction Log", "User Story"])
    
    with tab1:
        st.markdown(st.session_state['friction_log'])
    
    with tab2:
        st.markdown(st.session_state['user_story'])

# Reset button
if st.button("Reset Demo"):
    for key in ['friction_log', 'user_story', 'friction_status', 'user_story_status']:
        st.session_state[key] = None if key.endswith('log') or key.endswith('story') else "Ready"
    st.rerun()