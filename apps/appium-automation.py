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
.stVideo {
        width: 400px !important;
        height: auto !important;
        margin: 0 auto;
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

def get_gemini_pro_response(model, prompt, generation_config={}):
    generation_config = {"temperature": 0.1, "max_output_tokens": 8192}
    response = model.generate_content(prompt, generation_config=generation_config, stream=True)
    
    full_response = []
    for chunk in response:
        if chunk.text:
            full_response.append(chunk.text)
            yield chunk.text
    return "".join(full_response)

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
        ["English", "Portuguese", "Spanish"],
        key="language"
    )
    
    use_case = st.selectbox(
        "Select use case:",
        ["Bank of Anthos", "Hipster Shop"],
        key="use_case"
    )

# Load models and video
load_vertex(model_region)
text_model_pro, multimodal_model_pro = load_models(model_name)

video_uris = {
    "Bank of Anthos": "gs://convento-samples/boa-mobile.mp4",
    "Hipster Shop": "gs://convento-samples/hipster-mobile.mp4"
}

selected_video_uri = video_uris[use_case]
video_url = "https://storage.googleapis.com/" + selected_video_uri.split("gs://")[1]

# Video and Results Section
st.header("Video Analysis and Results")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("User Interaction Video")
    st.video(video_url)

with col2:
    st.subheader("Generated Results")
    
    # Video Description Tab
    if st.button("Generate Video Description", key="generate_video_description", disabled=st.session_state['video_description_status'] == "Running"):
        st.session_state['video_description_status'] = "Running"
        
        video_description_prompt = f"""All the answers are to be provided in {language}
        You are analyzing a video recording of a user interacting with the {use_case} mobile application. 
        Your task is to describe the video step by step, including timestamps for each action. 
        Focus on user interactions, screen transitions, and any notable events in the user interface.
        
        Format your response as a markdown table with the following columns:
        | Timestamp | Action | Description | Element Identifier |
        
        For example:
        | Timestamp | Action | Description | Element Identifier |
        |-----------|--------|-------------|---------------------|
        | 0:05 | Tap | User taps on the search bar | id="search_bar" |
        | 0:08 | Type | User types "running shoes" | id="search_input" |
        | 0:12 | Tap | User taps the search button | id="search_button" |
        
        Provide a comprehensive description of the entire video using this table format.
        For the Element Identifier column, use your best guess for appropriate IDs, class names, or XPaths.
        """
        
        with st.spinner("Generating Video Description..."):
            video_part = Part.from_uri(selected_video_uri, mime_type="video/mp4")
            video_description_placeholder = st.empty()
            video_description_response = ""
            for chunk in get_gemini_pro_response(multimodal_model_pro, [video_description_prompt, video_part]):
                video_description_response += chunk
                video_description_placeholder.markdown(video_description_response)
            st.session_state['video_description'] = video_description_response
        st.session_state['video_description_status'] = "Completed"
        video_description_placeholder.empty()
    
    if st.session_state['video_description']:
        with st.expander("Video Description", expanded=True):
            st.markdown(st.session_state['video_description'])
    
    st.write(f"Video Description Status: {st.session_state['video_description_status']}")
    
    # Appium Script Tab
    if st.button("Generate Appium Script", key="generate_appium_script", disabled=st.session_state['appium_script_status'] == "Running"):
        st.session_state['appium_script_status'] = "Running"
        
        appium_script_prompt = f"""All the answers are to be provided in {language}
        You are analyzing a video recording of a user interacting with the {use_case} mobile application. Your task is to generate an Appium script in Python that reproduces the steps shown in the video.
        
        Use the following video description as a reference for the user interactions:
        {st.session_state['video_description']}
        
        Focus on the following key areas:
        1. Setting up the Appium driver with appropriate capabilities
        2. Implementing each user action (taps, swipes, text input) using Appium commands
        3. Using appropriate locator strategies (id, xpath, accessibility id) based on the Element Identifier column
        4. Adding appropriate waits and assertions to ensure reliable test execution
        5. Handling any potential errors or exceptions
        
        Deliverable:
        Appium Python Script:
        - Start with importing necessary libraries and setting up the Appium driver
        - Implement each action from the video description using appropriate Appium commands
        - Add comments to explain the purpose of each action
        - Include error handling and cleanup (quitting the driver) at the end of the script
        
        Here's an example structure for the Appium script:
        
        ```python
        from appium import webdriver
        from appium.webdriver.common.mobileby import MobileBy
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        import time
        
        # Set up desired capabilities
        desired_caps = {{
            'platformName': 'Android',
            'deviceName': 'Android Emulator',
            'app': '/path/to/your/app.apk',
            # Add other necessary capabilities
        }}
        
        # Initialize the Appium driver
        driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)
        
        try:
            # Implement user actions here
            # Example:
            # Find and click on the search bar
            search_bar = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((MobileBy.ID, "search_bar"))
            )
            search_bar.click()
            
            # Type "running shoes" into the search input
            search_input = driver.find_element(MobileBy.ID, "search_input")
            search_input.send_keys("running shoes")
            
            # Click the search button
            search_button = driver.find_element(MobileBy.ID, "search_button")
            search_button.click()
            
            # Add more actions based on the video description
            
        except Exception as e:
            print(f"An error occurred: {{e}}")
        
        finally:
            # Quit the driver
            driver.quit()
        ```
        
        Generate an Appium script that accurately reproduces the user interactions from the video description. Use appropriate Appium commands, locator strategies, and error handling.
        
        Provide a brief summary of the script's coverage and any potential areas that may require manual testing or additional instrumentation.
        """
        
        with st.spinner("Generating Appium Script..."):
            video_part = Part.from_uri(selected_video_uri, mime_type="video/mp4")
            appium_script_placeholder = st.empty()
            appium_script_response = ""
            for chunk in get_gemini_pro_response(multimodal_model_pro, [appium_script_prompt, video_part]):
                appium_script_response += chunk
                appium_script_placeholder.markdown(appium_script_response)
            st.session_state['appium_script'] = appium_script_response
        st.session_state['appium_script_status'] = "Completed"
        appium_script_placeholder.empty()
    
    if st.session_state['appium_script']:
        with st.expander("Generated Appium Script", expanded=True):
            st.code(st.session_state['appium_script'], language="python")
    
    st.write(f"Appium Script Status: {st.session_state['appium_script_status']}")

    # Next step: Run the generated Appium script
    if st.session_state['appium_script']:
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