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

PROJECT_ID = os.environ.get("GCP_PROJECT")
LOCATION = os.environ.get("GCP_REGION")
vertexai.init(project=PROJECT_ID, location=LOCATION)

st.markdown("""
    <style>
    .stVideo {
        width: 400px !important;
        height: auto !important;
        margin: 0 auto;
    }
    </style>
    """, unsafe_allow_html=True)
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

st.title("Multi-Purpose Image To Action Demo")

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

col1, col2 = st.columns([1, 2])

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

    text_model_pro, multimodal_model_pro = load_models(model_name)

    if use_case == "Custom Use Case":
        image_upload = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
        custom_prompt_suggestion = "Analyze this image and provide a detailed description of its contents, focusing on [specific aspect]. Then, suggest potential applications or use cases for this image in the context of [your industry/field]."
        custom_prompt = st.text_area("Enter your custom prompt:", value=custom_prompt_suggestion, height=100)
        if image_upload:
            st.image(image_upload, width=300)
            image_part = Part.from_bytes(image_upload.getvalue(), mime_type=image_upload.type)
    else:
        if use_case == "Sprint Planning":
            image_url = "gs://convento-samples/boa-login.png"
            prompt = f"""
            All answers should be provided in {story_lang}.
            Explain this login screen in the format of feature implementation for a user story.
            This description will be used for development backlog for frontend, backend, and Google Cloud deployment plan and also implement login with facebook, google and apple.
            """
        elif use_case == "Random Jokes Website":
            image_url = "gs://convento-samples/guardanapo.jpg"
            prompt = f"""
            All answers should be provided in {story_lang}.
            Explain this napkin sketch in the format of feature implementation for a user story.
            The idea is a website for random jokes generated using Vertex AI with the gemini-1.5-flash-001 model.
            This description will be used for development backlog for frontend, backend, and Google Cloud deployment plan.
            """
        else:  # Test Plan Generation
            image_url = "gs://convento-samples/boa-login.png"
            prompt = f"""
            All answers should be provided in {story_lang}.
            Explain this login screen in the format of a test plan for a user story.
            This description will be used for development backlog.
            and also implement login with facebook, google and apple.
            """
        
        image_part = Part.from_uri(mime_type="image/png", uri=image_url)
        st.image("https://storage.googleapis.com/" + image_url.split("gs://")[1], width=300)

with col2:
    st.subheader("Generated Content")

    if st.button("Generate Initial Description", disabled=st.session_state.button_states['initial_description']):
        with st.spinner("Generating image description..."):
            if use_case == "Custom Use Case":
                if not image_upload or not custom_prompt:
                    st.error("Please upload an image and enter a custom prompt.")
                else:
                    response = get_gemini_pro_vision_response(multimodal_model_pro, [custom_prompt, image_part])
            else:
                response = get_gemini_pro_vision_response(multimodal_model_pro, [prompt, image_part])
            
            if 'response' in locals():
                st.session_state['initial_description'] = response
                st.session_state.button_states['initial_description'] = True

    if 'initial_description' in st.session_state:
        with st.expander("Initial Description", expanded=True):
            st.markdown(st.session_state['initial_description'])

        if use_case in ["Sprint Planning", "Random Jokes Website", "Custom Use Case"]:
            if st.button("Generate Backend", disabled=st.session_state.button_states['backend_code']):
                with st.spinner("Generating backend code..."):
                    backend_prompt = f"""
                    All answers should be provided in {story_lang}.
                    Use the image content and the generated description to create a backend implementation using Flask and Python for a planned sprint.
                    Generated description:
                    {st.session_state['initial_description']}
                    """
                    backend_response = get_gemini_pro_vision_response(multimodal_model_pro, [backend_prompt, image_part])
                    st.session_state['backend_code'] = backend_response
                    st.session_state.button_states['backend_code'] = True

            if 'backend_code' in st.session_state:
                with st.expander("Backend Code", expanded=True):
                    st.code(st.session_state['backend_code'], language="python")

                if st.button("Generate Frontend", disabled=st.session_state.button_states['frontend_code']):
                    with st.spinner("Generating frontend code..."):
                        frontend_prompt = f"""
                        All answers should be provided in {story_lang}.
                        Use the image content and the backend code to implement the frontend for the application.
                        Backend code:
                        {st.session_state['backend_code']}
                        """
                        frontend_response = get_gemini_pro_vision_response(multimodal_model_pro, [frontend_prompt, image_part])
                        st.session_state['frontend_code'] = frontend_response
                        st.session_state.button_states['frontend_code'] = True

            if 'frontend_code' in st.session_state:
                with st.expander("Frontend Code", expanded=True):
                    st.code(st.session_state['frontend_code'], language="javascript")

                if st.button("Generate Google Cloud Deployment", disabled=st.session_state.button_states['gcloud_code']):
                    with st.spinner("Generating Google Cloud deployment scripts..."):
                        gcloud_prompt = f"""
                        All answers should be provided in {story_lang}.
                        Use the backend and frontend content to create the best deployment architecture for a stateless application.
                        Use Cloud Run and choose an appropriate database based on the code. Use Google Cloud Storage for storing images if needed.
                        The output should be a Terraform script following best practices.
                        Backend code:
                        {st.session_state['backend_code']}
                        Frontend code:
                        {st.session_state['frontend_code']}
                        """
                        gcloud_response = get_gemini_pro_vision_response(multimodal_model_pro, [gcloud_prompt, image_part])
                        st.session_state['gcloud_code'] = gcloud_response
                        st.session_state.button_states['gcloud_code'] = True

            if 'gcloud_code' in st.session_state:
                with st.expander("Google Cloud Deployment (Terraform)", expanded=True):
                    st.code(st.session_state['gcloud_code'], language="hcl")

        elif use_case == "Test Plan Generation":
            if st.button("Generate Test Cases", disabled=st.session_state.button_states['test_cases']):
                with st.spinner("Generating test cases..."):
                    test_case_prompt = f"""
                    All answers should be provided in {story_lang}.
                    Use the image content and the generated description to create test cases for a planned sprint.
                    Generated description:
                    {st.session_state['initial_description']}
                    """
                    test_case_response = get_gemini_pro_vision_response(multimodal_model_pro, [test_case_prompt, image_part])
                    st.session_state['test_cases'] = test_case_response
                    st.session_state.button_states['test_cases'] = True

            if 'test_cases' in st.session_state:
                with st.expander("Test Cases", expanded=True):
                    st.markdown(st.session_state['test_cases'])

                if st.button("Generate Test Execution Script", disabled=st.session_state.button_states['test_script']):
                    with st.spinner("Generating test execution script..."):
                        script_prompt = f"""
                        All answers should be provided in {story_lang}.
                        Use the image content and the test plan to create scripts for testing during the planned sprint.
                        Test plan:
                        {st.session_state['test_cases']}
                        """
                        script_response = get_gemini_pro_vision_response(multimodal_model_pro, [script_prompt, image_part])
                        st.session_state['test_script'] = script_response
                        st.session_state.button_states['test_script'] = True

            if 'test_script' in st.session_state:
                with st.expander("Test Execution Script", expanded=True):
                    st.code(st.session_state['test_script'], language="python")

                if st.button("Generate Selenium Script", disabled=st.session_state.button_states['selenium_script']):
                    with st.spinner("Generating Selenium script..."):
                        selenium_prompt = f"""
                        All answers should be provided in {story_lang}.
                        Use the image content and the test plan to create a Selenium script to automate the tests.
                        Test plan:
                        {st.session_state['test_cases']}
                        """
                        selenium_response = get_gemini_pro_vision_response(multimodal_model_pro, [selenium_prompt, image_part])
                        st.session_state['selenium_script'] = selenium_response
                        st.session_state.button_states['selenium_script'] = True

            if 'selenium_script' in st.session_state:
                with st.expander("Selenium Script", expanded=True):
                    st.code(st.session_state['selenium_script'], language="python")
