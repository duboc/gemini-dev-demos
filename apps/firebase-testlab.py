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
        width: 100%;
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
if 'robo_script' not in st.session_state:
    st.session_state['robo_script'] = None
if 'robo_script_status' not in st.session_state:
    st.session_state['robo_script_status'] = "Ready"
if 'video_description' not in st.session_state:
    st.session_state['video_description'] = None
if 'video_description_status' not in st.session_state:
    st.session_state['video_description_status'] = "Ready"

st.title("Firebase TestLab Robo Script Generator")

# Reset Demo button at the top
if st.button("Reset Demo", key="reset_demo_top"):
    for key in ['robo_script', 'robo_script_status', 'video_description', 'video_description_status']:
        st.session_state[key] = None if key in ['robo_script', 'video_description'] else "Ready"
    st.rerun()

st.markdown("""
This demo showcases the capabilities of our Gemini Models in analyzing user interactions with mobile applications and generating Robo scripts for Firebase Test Lab.
By capturing user actions from a video, we create a script that can reproduce these steps for automated testing.
The generated Robo script can be used to simulate user behavior, identify potential issues, and ensure consistent app performance across different devices.
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
        | Timestamp | Action | Description |
        
        For example:
        | Timestamp | Action | Description |
        |-----------|--------|-------------|
        | 0:05 | Tap | User taps on the search bar |
        | 0:08 | Type | User types "running shoes" |
        | 0:12 | Tap | User taps the search button |
        
        Provide a comprehensive description of the entire video using this table format.
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
    
    # Robo Script Tab
    if st.button("Generate Robo Script", key="generate_robo_script", disabled=st.session_state['robo_script_status'] == "Running"):
        st.session_state['robo_script_status'] = "Running"
        
        robo_script_prompt = f"""All the answers are to be provided in {language}
        You are analyzing a video recording of a user interacting with the {use_case} mobile application. Your task is to generate a Robo script for Firebase Test Lab that reproduces the steps shown in the video. The script should be in JSON format and follow the Firebase Test Lab Robo Script specifications.
        
        Use the following video description as a reference for the user interactions:
        {st.session_state['video_description']}
        
        Focus on the following key areas:
        1. Identifying and describing each user action (taps, swipes, text input)
        2. Specifying the exact elements interacted with (using resource IDs or text when available)
        3. Determining the correct order of actions
        4. Including any necessary waits or assertions
        
        Deliverable:
        Firebase Test Lab Robo Script (JSON format):
        - Each action should be represented as a separate object in the JSON array
        - Include the type of action (e.g., "click", "text", "swipe")
        - Specify the target element using resource ID, text, or coordinates as appropriate
        - Add comments to explain the purpose of each action
        
        Here are two examples of valid Robo scripts:
        
        Example 1 (with context descriptor):
        ```json
        [
          {{
            "crawlStage": "crawl",
            "contextDescriptor": {{
              "condition": "app_under_test_shown"
            }},
            "actions": [
              {{
                "eventType": "VIEW_TEXT_CHANGED",
                "replacementText": "user123",
                "elementDescriptors": [
                  {{
                    "resourceId": "my.app.package:id/username"
                  }}
                ]
              }},
              {{
                "eventType": "VIEW_TEXT_CHANGED",
                "replacementText": "12345",
                "elementDescriptors": [
                  {{
                    "resourceId": "my.app.package:id/password"
                  }}
                ]
              }},
              {{
                "eventType": "VIEW_CLICKED",
                "elementDescriptors": [
                  {{
                    "resourceId": "my.app.package:id/login"
                  }}
                ]
              }}
            ]
          }}
        ]
        ```
        
        Example 2 (without context descriptor):
        ```json
        [
          {{
            "eventType": "VIEW_TEXT_CHANGED",
            "replacementText": "user123",
            "elementDescriptors": [
              {{
                "resourceId": "my.app.package:id/username"
              }}
            ]
          }},
          {{
            "eventType": "VIEW_TEXT_CHANGED",
            "replacementText": "12345",
            "elementDescriptors": [
              {{
                "resourceId": "my.app.package:id/password"
              }}
            ]
          }},
          {{
            "eventType": "VIEW_CLICKED",
            "elementDescriptors": [
              {{
                "resourceId": "my.app.package:id/login"
              }}
            ]
          }}
        ]
        ```
        
        Generate a Robo script that accurately reproduces the user interactions from the video description. Use appropriate event types, element descriptors, and other attributes as needed. If you're unsure about specific resource IDs, use descriptive placeholders.
        
        Provide a brief summary of the script's coverage and any potential areas that may require manual testing or additional instrumentation.
        """
        
        with st.spinner("Generating Robo Script..."):
            video_part = Part.from_uri(selected_video_uri, mime_type="video/mp4")
            robo_script_placeholder = st.empty()
            robo_script_response = ""
            for chunk in get_gemini_pro_response(multimodal_model_pro, [robo_script_prompt, video_part]):
                robo_script_response += chunk
                robo_script_placeholder.markdown(robo_script_response)
            st.session_state['robo_script'] = robo_script_response
        st.session_state['robo_script_status'] = "Completed"
        robo_script_placeholder.empty()
    
    if st.session_state['robo_script']:
        with st.expander("Generated Robo Script", expanded=True):
            st.code(st.session_state['robo_script'], language="json")
    
    st.write(f"Robo Script Status: {st.session_state['robo_script_status']}")

    # Next step: Run the generated test using gcloud CLI
    if st.session_state['robo_script']:
        if st.button("Next Step: Run the Test"):
            with st.expander("Run the Test Instructions", expanded=True):
                st.markdown("""
                To run the generated Robo script using the gcloud CLI, follow these steps:

                1. Save the generated JSON script to a file (e.g., `robo_script.json`).
                2. Make sure you have the latest version of the gcloud CLI installed and configured.
                3. Run the following command in your terminal:

                ```bash
                gcloud firebase test android run \\
                    --type robo \\
                    --app path/to/your/app.apk \\
                    --robo-script path/to/robo_script.json \\
                    --device model=MODEL_ID,version=VERSION_ID,locale=LOCALE,orientation=ORIENTATION
                ```

                Replace the placeholders with your specific values:
                - `path/to/your/app.apk`: The path to your Android app's APK file.
                - `path/to/robo_script.json`: The path to the saved Robo script JSON file.
                - `MODEL_ID`: The device model you want to test on (e.g., "Pixel2").
                - `VERSION_ID`: The Android version to test on (e.g., "28").
                - `LOCALE`: The locale to use for testing (e.g., "en_US").
                - `ORIENTATION`: The screen orientation for testing ("portrait" or "landscape").

                You can add multiple `--device` flags to run the test on different device configurations.
                """)