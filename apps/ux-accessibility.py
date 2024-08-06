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

def get_gemini_pro_vision_response_stream(
    model, prompt_list, generation_config={}, stream: bool = True
):
    generation_config = {"temperature": 0.1, "max_output_tokens": 8192}
    return model.generate_content(
        prompt_list, generation_config=generation_config, stream=stream
    )

st.markdown("""
    <style>
    .stVideo {
        width: 400px !important;
        height: auto !important;
        margin: 0 auto;
    }
    </style>
    """, unsafe_allow_html=True)

if st.button("Reset Demo", key="reset_demo"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

st.title("WCAG Accessibility Analyzer", anchor=False)

st.markdown("""
This tool analyzes the accessibility of a website or app based on Web Content Accessibility Guidelines (WCAG).
It identifies areas for improvement to enhance user interaction and ensure compliance with accessibility standards.
""")

col1, col2 = st.columns([2, 3])

with col1:
    model_region = st.selectbox(
        "Select Gemini region:",
        ["us-central1", "southamerica-east1", "us-east1", "us-south1", "europe-southwest1"],
        key="model_region",
    )

    load_vertex(model_region)

    model_name = st.radio(
        "Select Model:",
        ["gemini-experimental", "gemini-1.5-pro-001", "gemini-1.5-flash-001"],
        key="model_name",
        horizontal=True,
        index=0,
    )

    story_lang = st.radio(
        "Select language for analysis:",
        ["Portuguese", "Spanish", "English"],
        key="story_lang",
        horizontal=True,
    )

    use_case = st.selectbox(
        "Select use case:",
        ["Retail (Nike)", "Pharmacy (Raia)"],
        key="use_case",
    )

    text_model_pro, multimodal_model_pro = load_models(model_name)

    if use_case == "Retail (Nike)":
        video_uri = "gs://convento-samples/nike-sbf.mp4"
    else:
        video_uri = "gs://convento-samples/raia.mp4"

    video_url = ("https://storage.googleapis.com/" + video_uri.split("gs://")[1])
    
    st.markdown(f"""
        <video width="400" controls>
            <source src="{video_url}" type="video/mp4">
            Your browser does not support the video tag.
        </video>
    """, unsafe_allow_html=True)

with col2:
    with st.expander("WCAG Compliance Analysis", expanded=False):
        wcag_analysis_placeholder = st.empty()
        if st.button("Generate WCAG Analysis", key="generate_wcag_analysis"):
            prompt_wcag = f"""All responses should be in {story_lang}.
            Analyze the video of a user interacting with the {'Nike online store' if use_case == 'Retail (Nike)' else 'online pharmacy app'}.
            Identify specific accessibility issues and improvement opportunities based on WCAG 2.1 guidelines.

            Key areas to evaluate:
            1. Perceivable: Information and user interface components must be presentable to users in ways they can perceive.
            2. Operable: User interface components and navigation must be operable.
            3. Understandable: Information and the operation of user interface must be understandable.
            4. Robust: Content must be robust enough that it can be interpreted by a wide variety of user agents, including assistive technologies.

            Provide a table with:
            Timestamp | WCAG Guideline | Issue Description | Conformance Level (A, AA, AAA) | Recommendation

            Follow with a concise summary of overall WCAG compliance strengths and weaknesses, and specific, actionable recommendations for improvement.
            """
            video_part = Part.from_uri(video_uri, mime_type="video/mp4")
            wcag_response_stream = get_gemini_pro_vision_response_stream(multimodal_model_pro, [prompt_wcag, video_part])
            
            full_response = ""
            for chunk in wcag_response_stream:
                full_response += chunk.text
                wcag_analysis_placeholder.markdown(full_response)
            
            st.session_state["wcag_analysis"] = full_response

    with st.expander("Accessibility User Stories", expanded=False):
        user_story_placeholder = st.empty()
        if st.button("Generate Accessibility User Stories", key="generate_user_story"):
            if "wcag_analysis" not in st.session_state:
                st.warning("Please generate the WCAG Analysis first.")
            else:
                prompt_user_story = f"""All responses should be in {story_lang}.
                Group similar accessibility issues from the WCAG analysis into user stories. Present in a table format.

                For each user story:
                1. Follow the format: "As a [type of user with specific accessibility needs], I want to [action] so that [benefit]."
                2. Prioritize based on the WCAG conformance level (A, AA, AAA).
                3. Include details about the accessibility issue and recommended solution.

                Table format:
                Priority | User Story | WCAG Guideline | Details (including issue and recommendation)
                """
                prompt_user_story += "\n" + st.session_state["wcag_analysis"]
                video_part = Part.from_uri(video_uri, mime_type="video/mp4")
                user_story_response_stream = get_gemini_pro_vision_response_stream(multimodal_model_pro, [prompt_user_story, video_part])
                
                full_response = ""
                for chunk in user_story_response_stream:
                    full_response += chunk.text
                    user_story_placeholder.markdown(full_response)