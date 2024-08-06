import streamlit as st
import vertexai
from vertexai.generative_models import GenerativeModel, Part, GenerationConfig, HarmCategory, HarmBlockThreshold
import os
from utils_streamlit import reset_st_state

PROJECT_ID = os.environ.get("GCP_PROJECT")
LOCATION = os.environ.get("GCP_REGION")
vertexai.init(project=PROJECT_ID, location=LOCATION)

if 'response' not in st.session_state:
    st.session_state['response'] = 'init'
if 'api_costs' not in st.session_state:
    st.session_state['api_costs'] = []
if 'session_analyses' not in st.session_state:
    st.session_state['session_analyses'] = []

st.markdown("""
    <style>
    .stVideo {
        width: 400px !important;
        height: auto !important;
        margin: 0 auto;
    }
    </style>
    """, unsafe_allow_html=True)
@st.cache_resource
def load_models(name):
    text_model_pro = GenerativeModel(name)
    multimodal_model_pro = GenerativeModel(name)
    return text_model_pro, multimodal_model_pro

def get_gemini_pro_vision_response(model, prompt_list, generation_config={}, stream=True):
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

def count_tokens(model, text):
    response = model.count_tokens(text)
    return response.total_tokens, response.total_billable_characters

def calculate_cost(model_name, input_chars, output_chars, video_duration=0):
    if model_name == "gemini-1.5-flash-001":
        input_cost = (input_chars / 1000) * 0.00001875
        output_cost = (output_chars / 1000) * 0.000075
        video_cost = video_duration * 0.00002
    else:  # gemini-1.5-pro-001 or gemini-experimental
        input_cost = (input_chars / 1000) * 0.00125
        output_cost = (output_chars / 1000) * 0.00375
        video_cost = video_duration * 0.001315
    
    return input_cost + output_cost + video_cost

def update_session_analysis(action, cost):
    st.session_state['session_analyses'].append({
        "Action": action,
        "Cost": f"${cost:.6f}"
    })

st.header("Generate Selenium Test from Video", divider="rainbow")

if reset := st.button("Reset Demo State"):
    reset_st_state()

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("""
    This demo showcases Gemini Models' capabilities:
    1. Analyze video content
    2. Generate detailed descriptions
    3. Create Selenium scripts for web automation
    
    Select options and click 'Generate' to start!
    """)

    model_name = st.radio(
        label="Model:",
        options=["gemini-experimental", "gemini-1.5-pro-001", "gemini-1.5-flash-001"],
        captions=["Gemini Pro Experimental", "Gemini Pro 1.5", "Gemini Flash 1.5"],
        key="model_name",
        index=0,
        horizontal=True
    )

    story_lang = st.radio(
        "Output language:",
        ["Portuguese", "Spanish", "English"],
        key="story_lang",
        horizontal=True,
    )

    text_model_pro, multimodal_model_pro = load_models(model_name)

    vide_desc_uri = "gs://convento-samples/boa-selenium-rag.mov"
    video_desc_url = ("https://storage.googleapis.com/" + vide_desc_uri.split("gs://")[1])

    st.video(video_desc_url)

    prompt = f"""Describe the video content concisely, focusing on:
    1. Timestamped list of user actions
    2. Purpose of each action
    3. Relevant screen information

    Provide the description in {story_lang}.
    """

    vide_desc_img = Part.from_uri(vide_desc_uri, mime_type="video/mp4")

with col2:
    # API Costs Session at the top right
    st.subheader("API Costs Session")
    total_session_cost = sum(st.session_state['api_costs'])
    st.metric("Total Session Cost", f"${total_session_cost:.6f}")

    # Session Analyses
    st.subheader("Session Analyses")
    if st.session_state['session_analyses']:
        st.table(st.session_state['session_analyses'])
    else:
        st.info("No actions performed yet.")

    # Generate button moved under session analyses
    vide_desc_description = st.button("Generate", key="vide_desc_description")

    if vide_desc_description and prompt:
        with st.spinner("Analyzing video and generating description..."):
            response = get_gemini_pro_vision_response(multimodal_model_pro, [prompt, vide_desc_img])
            st.session_state["response"] = response

            # Calculate and update costs for video description generation
            input_tokens, input_chars = count_tokens(text_model_pro, prompt)
            output_tokens, output_chars = count_tokens(text_model_pro, response)
            video_duration = 60  # Assuming the video is 60 seconds long. Adjust as needed.
            total_cost = calculate_cost(model_name, input_chars, output_chars, video_duration)
            st.session_state['api_costs'].append(total_cost)
            update_session_analysis("Generate Description", total_cost)

    if st.session_state["response"] != "init":
        st.subheader("Token Usage and Cost")
        
        input_tokens, input_chars = count_tokens(text_model_pro, prompt)
        output_tokens, output_chars = count_tokens(text_model_pro, st.session_state["response"])
        
        video_duration = 60  # Assuming the video is 60 seconds long. Adjust as needed.
        total_cost = calculate_cost(model_name, input_chars, output_chars, video_duration)
        
        token_data = {
            "Metric": ["Input", "Output", "Total", "API Cost"],
            "Tokens": [input_tokens, output_tokens, input_tokens + output_tokens, ""],
            "Characters": [input_chars, output_chars, input_chars + output_chars, ""],
            "Cost ($)": [
                calculate_cost(model_name, input_chars, 0, video_duration),
                calculate_cost(model_name, 0, output_chars, 0),
                total_cost,
                total_cost
            ]
        }
        
        st.table(token_data)

        with st.expander("Video Description", expanded=True):
            st.markdown(st.session_state["response"])

        generate_selenium = st.button("Create Selenium Script", key="generate_selenium")
        if generate_selenium:
            with st.spinner("Generating Selenium code..."):
                prompt_selenium = f"""Create a Selenium script to automate the tasks described:

                {st.session_state["response"]}
                """
                selenium_response = get_gemini_pro_vision_response(multimodal_model_pro, [prompt_selenium, vide_desc_img])
                
                with st.expander("Selenium Script", expanded=True):
                    st.code(selenium_response, language="python")
                
                # Calculate and update costs for Selenium script generation
                input_tokens, input_chars = count_tokens(text_model_pro, prompt_selenium)
                output_tokens, output_chars = count_tokens(text_model_pro, selenium_response)
                selenium_cost = calculate_cost(model_name, input_chars, output_chars, 0)
                st.session_state['api_costs'].append(selenium_cost)
                update_session_analysis("Generate Selenium Script", selenium_cost)