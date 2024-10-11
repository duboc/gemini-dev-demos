import streamlit as st
import os
from config import (
    load_vertex,
    load_models,
    get_gemini_pro_vision_response_stream,
    read_prompt,
    video_uris,
    images_uris,
    model_gemini_pro_15,
    model_gemini_flash,
    model_experimental
)
from vertexai.generative_models import Part

# Custom CSS to resize video, style tabs, and improve button appearance
st.markdown("""
<style>
    .stVideo {
        width: 100% !important;
        height: auto !important;
        margin: 0 auto;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state variables
if 'appium_script' not in st.session_state:
    st.session_state['appium_script'] = None
if 'appium_script_status' not in st.session_state:
    st.session_state['appium_script_status'] = "Ready"
if 'video_description' not in st.session_state:
    st.session_state['video_description'] = None
if 'video_description_status' not in st.session_state:
    st.session_state['video_description_status'] = "Ready"

st.title("Appium Script Generator")

# Reset Demo button at the top with custom styling
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    if st.button("Reset Demo", key="reset_demo_top", help="Click to reset the demo"):
        for key in ['appium_script', 'appium_script_status', 'video_description', 'video_description_status']:
            st.session_state[key] = None if key in ['appium_script', 'video_description'] else "Ready"
        st.rerun()

st.markdown("""
This demo showcases the capabilities of our Gemini Models in analyzing user interactions with mobile applications and generating Appium scripts.
By capturing user actions from a video, we create a script that can reproduce these steps for automated testing.
The generated Appium script can be used to simulate user behavior, identify potential issues, and ensure consistent app performance across different devices.
""")

# Main content
col1, col2 = st.columns([1, 4])

with col1:
    st.header("Configuration and Video")

    model_region = st.selectbox(
        "Select Gemini region:",
        ["us-central1", "southamerica-east1", "us-east1", "us-south1", "europe-southwest1"],
        key="model_region"
    )
    
    model_name = st.radio(
        "Select Model:",
        ["gemini-experimental", "gemini-1.5-pro-002", "gemini-1.5-flash-002"],
        key="model_name",
        index=0
    )

    language = st.radio(
        "Select language for generation:",
        ["English", "Portuguese", "Spanish"],
        key="language"
    )
    
    use_case = st.selectbox(
        "Select use case:",
        list(video_uris.keys()),
        key="use_case"
    )

    # Load models
    load_vertex(model_region)
    if model_name == "gemini-experimental":
        model = model_experimental
    elif model_name == "gemini-1.5-pro-002":
        model = model_gemini_pro_15
    else:
        model = model_gemini_flash

    st.subheader("User Interaction Video")
    selected_video_uri = video_uris[use_case]
    video_url = "https://storage.googleapis.com/" + selected_video_uri.split("gs://")[1]
    st.video(video_url)

with col2:
    st.header("Generated Results")
    tab1, tab2, tab3 = st.tabs(["Video Description", "Appium Script", "Prompts"])

    with tab1:
        if st.button("Generate Video Description", key="generate_video_description", disabled=st.session_state['video_description_status'] == "Running"):
            st.session_state['video_description_status'] = "Running"
            
            video_description_prompt = read_prompt('prompts/video_description_prompt.md')
            video_description_prompt = video_description_prompt.format(language=language, use_case=use_case)
            
            with st.spinner("Generating Video Description..."):
                video_part = Part.from_uri(selected_video_uri, mime_type="video/mp4")
                video_description_placeholder = st.empty()
                video_description_response = ""
                for chunk in get_gemini_pro_vision_response_stream(model, [video_description_prompt, video_part]):
                    if chunk.text:
                        video_description_response += chunk.text
                        video_description_placeholder.markdown(video_description_response)
                st.session_state['video_description'] = video_description_response
            st.session_state['video_description_status'] = "Completed"
            video_description_placeholder.empty()
        
        if st.session_state.get('video_description'):
            st.markdown(st.session_state['video_description'])
        
        st.write(f"Video Description Status: {st.session_state['video_description_status']}")

    with tab2:
        if st.button("Generate Appium Script", key="generate_appium_script", disabled=st.session_state['appium_script_status'] == "Running"):
            st.session_state['appium_script_status'] = "Running"
            
            appium_script_prompt = read_prompt('prompts/appium_script_prompt.md')
            appium_script_prompt = appium_script_prompt.format(
                language=language,
                use_case=use_case,
                video_description=st.session_state.get('video_description')
            )
            
            with st.spinner("Generating Appium Script..."):
                video_part = Part.from_uri(selected_video_uri, mime_type="video/mp4")
                appium_script_placeholder = st.empty()
                appium_script_response = ""
                for chunk in get_gemini_pro_vision_response_stream(model, [appium_script_prompt, video_part]):
                    if chunk.text:
                        appium_script_response += chunk.text
                        appium_script_placeholder.markdown(appium_script_response)
                st.session_state['appium_script'] = appium_script_response
            st.session_state['appium_script_status'] = "Completed"
            appium_script_placeholder.empty()
        
        if st.session_state.get('appium_script'):
            st.code(st.session_state['appium_script'], language="python")
        
        st.write(f"Appium Script Status: {st.session_state['appium_script_status']}")

        if st.session_state.get('appium_script'):
            if st.button("Next Step: Run the Appium Script"):
                with st.expander("Run the Appium Script Instructions", expanded=True):
                    st.markdown("""
                    To run the generated Appium script, follow these steps:

                    1. Set up your Appium environment:
                       - Install Appium server: `npm install -g appium`
                       - Install necessary drivers (e.g., UiAutomator2 for Android): `appium driver install uiautomator2`
                       - Set up Android SDK and necessary tools

                    2. Start the Appium server:
                       ```
                       appium
                       ```

                    3. Save the generated Python script to a file (e.g., `appium_test.py`).

                    4. Install the required Python libraries:
                       ```
                       pip install Appium-Python-Client selenium
                       ```

                    5. Update the `desired_caps` in the script with your specific device and app information.

                    6. Run the Appium script:
                       ```
                       python appium_test.py
                       ```

                    Make sure you have a device or emulator running and properly configured before executing the script.

                    Note: You may need to adjust the script based on your specific app structure and element identifiers. The generated script provides a starting point, but some fine-tuning might be necessary for optimal performance.
                    """)

    with tab3:
        st.subheader("Video Description Prompt")
        st.code(read_prompt('prompts/video_description_prompt.md'), language="markdown")
        
        st.subheader("Appium Script Prompt")
        st.code(read_prompt('prompts/appium_script_prompt.md'), language="markdown")