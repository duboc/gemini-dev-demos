import streamlit as st
import os
from config import (
    load_vertex,
    load_models,
    get_gemini_pro_vision_response_stream,
    video_uris,
    images_uris,
    PROJECT_ID,
    LOCATION
)
from vertexai.generative_models import Part

st.markdown("""
    <style>
    .stVideo {
        width: 400px !important;
        height: auto !important;
        margin: 0 auto;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #F0F2F6;
        border-radius: 4px;
        color: #000000;
        font-size: 14px;
        font-weight: 400;
        align-items: center;
        justify-content: center;
        border: none;
        padding: 0px 16px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FFFFFF;
        border-bottom: 2px solid #4CAF50;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("Multi-Purpose Image To Action Demo")

def read_prompt(file_name):
    with open(os.path.join("prompts", file_name), "r") as file:
        return file.read()

if 'button_states' not in st.session_state:
    st.session_state.button_states = {
        'initial_description': False,
        'backend_code': False,
        'frontend_code': False,
        'gcloud_code': False,
        'test_cases': False,
        'test_script': False,
        'selenium_script': False
    }

if st.button("Reset Demo", key="reset_top"):
    for key in ['initial_description', 'backend_code', 'frontend_code', 'gcloud_code', 'test_cases', 'test_script', 'selenium_script']:
        if key in st.session_state:
            del st.session_state[key]
    st.session_state.button_states = {key: False for key in st.session_state.button_states}
    st.rerun()

col1, col2 = st.columns([1, 3])

with col1:
    st.subheader("Configuration")
    model_name = st.radio(
        "Select Model:",
        ["gemini-experimental", "gemini-1.5-pro-001", "gemini-1.5-flash-001"],
        format_func=lambda x: {
            "gemini-experimental": "Gemini Pro Experimental",
            "gemini-1.5-pro-001": "Gemini Pro 1.5",
            "gemini-1.5-flash-001": "Gemini Flash 1.5"
        }[x],
        horizontal=True
    )

    story_lang = st.radio(
        "Select Language:",
        ["Portuguese", "Spanish", "English"],
        horizontal=True
    )

    use_case = st.selectbox(
        "Select Use Case:",
        ["Sprint Planning", "Random Jokes Website", "Test Plan Generation", "Custom Use Case"]
    )

    use_case_descriptions = {
        "Sprint Planning": "This use case focuses on creating a development plan for a login screen. It includes generating backend, frontend, and deployment code based on the image analysis.",
        "Random Jokes Website": "This use case involves creating a website that generates random jokes using Vertex AI. It includes backend, frontend, and deployment code generation based on a napkin sketch.",
        "Test Plan Generation": "This use case is centered around creating a comprehensive test plan for a login screen. It includes generating test cases, test execution scripts, and Selenium automation scripts.",
        "Custom Use Case": "This option allows you to upload your own image and provide a custom prompt for analysis. You can then generate various outputs based on your specific needs."
    }

    st.text_area("Use Case Description", use_case_descriptions[use_case], height=100, disabled=True)

    load_vertex(LOCATION)
    text_model_pro, multimodal_model_pro = load_models(model_name)

    if use_case == "Custom Use Case":
        image_upload = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
        custom_prompt_suggestion = read_prompt("custom_prompt_suggestion.md")
        custom_prompt = st.text_area("Enter your custom prompt:", value=custom_prompt_suggestion, height=100)
        if image_upload:
            st.image(image_upload, width=300)
            # Convert the uploaded file to bytes
            image_bytes = image_upload.getvalue()
            # Create a Part object from the image bytes
            image_part = Part.from_data(data=image_bytes, mime_type=image_upload.type)
    else:
        if use_case == "Sprint Planning":
            image_uri = images_uris["Bank of Anthos Login"]
            prompt = read_prompt("sprint_planning_prompt.md").format(language=story_lang)
        elif use_case == "Random Jokes Website":
            image_uri = images_uris["Guardanapo"]
            prompt = read_prompt("random_jokes_prompt.md").format(language=story_lang)
        else:  # Test Plan Generation
            image_uri = images_uris["Bank of Anthos Login"]
            prompt = read_prompt("test_plan_prompt.md").format(language=story_lang)
        
        image_part = Part.from_uri(mime_type="image/png", uri=image_uri)
        st.image("https://storage.googleapis.com/" + image_uri.split("gs://")[1], width=300)

with col2:
    st.subheader("Generated Content")

    tab_titles = ["Initial Description", "Backend Code", "Frontend Code", "Google Cloud Deployment", "Test Cases", "Test Execution Script", "Selenium Script"]
    tabs = st.tabs(tab_titles)

    with tabs[0]:  # Initial Description
        if st.button("Generate Initial Description", disabled=st.session_state.button_states['initial_description']):
            with st.spinner("Generating image description..."):
                if use_case == "Custom Use Case":
                    if not image_upload or not custom_prompt:
                        st.error("Please upload an image and enter a custom prompt.")
                    else:
                        response = "".join([chunk.text for chunk in get_gemini_pro_vision_response_stream(multimodal_model_pro, [custom_prompt, image_part])])
                else:
                    response = "".join([chunk.text for chunk in get_gemini_pro_vision_response_stream(multimodal_model_pro, [prompt, image_part])])
                
                if 'response' in locals():
                    st.session_state['initial_description'] = response
                    st.session_state.button_states['initial_description'] = True
        
        if 'initial_description' in st.session_state:
            st.markdown(st.session_state['initial_description'])

    if use_case in ["Sprint Planning", "Random Jokes Website", "Custom Use Case"]:
        with tabs[1]:  # Backend Code
            if st.button("Generate Backend", disabled=st.session_state.button_states['backend_code']):
                with st.spinner("Generating backend code..."):
                    backend_prompt = read_prompt("backend_prompt.md").format(
                        language=story_lang,
                        initial_description=st.session_state['initial_description']
                    )
                    backend_response = "".join([chunk.text for chunk in get_gemini_pro_vision_response_stream(multimodal_model_pro, [backend_prompt, image_part])])
                    st.session_state['backend_code'] = backend_response
                    st.session_state.button_states['backend_code'] = True
            
            if 'backend_code' in st.session_state:
                st.code(st.session_state['backend_code'], language="python")

        with tabs[2]:  # Frontend Code
            if st.button("Generate Frontend", disabled=st.session_state.button_states['frontend_code']):
                with st.spinner("Generating frontend code..."):
                    frontend_prompt = read_prompt("frontend_prompt.md").format(
                        language=story_lang,
                        backend_code=st.session_state['backend_code']
                    )
                    frontend_response = "".join([chunk.text for chunk in get_gemini_pro_vision_response_stream(multimodal_model_pro, [frontend_prompt, image_part])])
                    st.session_state['frontend_code'] = frontend_response
                    st.session_state.button_states['frontend_code'] = True
            
            if 'frontend_code' in st.session_state:
                st.code(st.session_state['frontend_code'], language="javascript")

        with tabs[3]:  # Google Cloud Deployment
            if st.button("Generate Google Cloud Deployment", disabled=st.session_state.button_states['gcloud_code']):
                with st.spinner("Generating Google Cloud deployment scripts..."):
                    gcloud_prompt = read_prompt("gcloud_prompt.md").format(
                        language=story_lang,
                        backend_code=st.session_state['backend_code'],
                        frontend_code=st.session_state['frontend_code']
                    )
                    gcloud_response = "".join([chunk.text for chunk in get_gemini_pro_vision_response_stream(multimodal_model_pro, [gcloud_prompt, image_part])])
                    st.session_state['gcloud_code'] = gcloud_response
                    st.session_state.button_states['gcloud_code'] = True
            
            if 'gcloud_code' in st.session_state:
                st.code(st.session_state['gcloud_code'], language="hcl")

    elif use_case == "Test Plan Generation":
        with tabs[4]:  # Test Cases
            if st.button("Generate Test Cases", disabled=st.session_state.button_states['test_cases']):
                with st.spinner("Generating test cases..."):
                    test_case_prompt = read_prompt("test_case_prompt.md").format(
                        language=story_lang,
                        initial_description=st.session_state['initial_description']
                    )
                    test_case_response = "".join([chunk.text for chunk in get_gemini_pro_vision_response_stream(multimodal_model_pro, [test_case_prompt, image_part])])
                    st.session_state['test_cases'] = test_case_response
                    st.session_state.button_states['test_cases'] = True
            
            if 'test_cases' in st.session_state:
                st.markdown(st.session_state['test_cases'])

        with tabs[5]:  # Test Execution Script
            if st.button("Generate Test Execution Script", disabled=st.session_state.button_states['test_script']):
                with st.spinner("Generating test execution script..."):
                    script_prompt = read_prompt("test_script_prompt.md").format(
                        language=story_lang,
                        test_cases=st.session_state['test_cases']
                    )
                    script_response = "".join([chunk.text for chunk in get_gemini_pro_vision_response_stream(multimodal_model_pro, [script_prompt, image_part])])
                    st.session_state['test_script'] = script_response
                    st.session_state.button_states['test_script'] = True
            
            if 'test_script' in st.session_state:
                st.code(st.session_state['test_script'], language="python")

        with tabs[6]:  # Selenium Script
            if st.button("Generate Selenium Script", disabled=st.session_state.button_states['selenium_script']):
                with st.spinner("Generating Selenium script..."):
                    selenium_prompt = read_prompt("selenium_script_prompt.md").format(
                        language=story_lang,
                        test_cases=st.session_state['test_cases']
                    )
                    selenium_response = "".join([chunk.text for chunk in get_gemini_pro_vision_response_stream(multimodal_model_pro, [selenium_prompt, image_part])])
                    st.session_state['selenium_script'] = selenium_response
                    st.session_state.button_states['selenium_script'] = True
            
            if 'selenium_script' in st.session_state:
                st.code(st.session_state['selenium_script'], language="python")

st.markdown("---")
st.markdown("Made with ❤️ using Streamlit and Gemini AI")