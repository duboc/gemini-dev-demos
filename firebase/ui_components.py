import streamlit as st
from vertexai.generative_models import Part
import os
import json
from config import load_vertex, load_models, video_uris, PROJECT_ID, LOCATION

def load_prompt(prompt_name, **kwargs):
    prompt_path = os.path.join('prompts', f'{prompt_name}_prompt.md')
    try:
        with open(prompt_path, 'r') as file:
            prompt_content = file.read().strip()
        return prompt_content.format(**kwargs)
    except FileNotFoundError:
        st.error(f"Prompt file not found: {prompt_path}")
        return ""
    except KeyError as e:
        st.error(f"Missing key in prompt file: {e}")
        return prompt_content  # Return unformatted content
    except Exception as e:
        st.error(f"Error reading prompt file: {e}")
        return ""

def get_gemini_pro_response(model, prompt, generation_config={}):
    generation_config = {"temperature": 0.1, "max_output_tokens": 8192}
    response = model.generate_content(prompt, generation_config=generation_config, stream=True)
    
    full_response = []
    for chunk in response:
        if chunk.text:
            full_response.append(chunk.text)
            yield chunk.text
    return "".join(full_response)

def generate_video_description(use_case, language, selected_video_uri, multimodal_model_pro):
    if st.button("Generate Video Description", key="generate_video_description", disabled=st.session_state.get('video_description_status') == "Running"):
        st.session_state['video_description_status'] = "Running"
        
        video_description_prompt = load_prompt("video_description", language=language, use_case=use_case)
        
        if video_description_prompt:
            with st.spinner("Generating Video Description..."):
                video_part = Part.from_uri(selected_video_uri, mime_type="video/mp4")
                video_description_response = ""
                for chunk in get_gemini_pro_response(multimodal_model_pro, [video_description_prompt, video_part]):
                    video_description_response += chunk
                st.session_state['video_description'] = video_description_response
            st.session_state['video_description_status'] = "Completed"
        else:
            st.session_state['video_description_status'] = "Ready"

def generate_robo_script(use_case, language, selected_video_uri, multimodal_model_pro):
    if st.button("Generate Robo Script", key="generate_robo_script", disabled=st.session_state.get('robo_script_status') == "Running"):
        st.session_state['robo_script_status'] = "Running"
        
        if not st.session_state.get('video_description'):
            st.error("Please generate a video description first.")
            st.session_state['robo_script_status'] = "Ready"
            return
        
        robo_script_prompt = load_prompt("robo_script", 
                                         language=language, 
                                         use_case=use_case, 
                                         video_description=st.session_state['video_description'])
        
        if robo_script_prompt:
            with st.spinner("Generating Robo Script..."):
                video_part = Part.from_uri(selected_video_uri, mime_type="video/mp4")
                robo_script_response = ""
                for chunk in get_gemini_pro_response(multimodal_model_pro, [robo_script_prompt, video_part]):
                    robo_script_response += chunk
                st.session_state['robo_script'] = robo_script_response
            st.session_state['robo_script_status'] = "Completed"
        else:
            st.session_state['robo_script_status'] = "Ready"

def generate_test_execution_script(use_case, language, multimodal_model_pro):
    if st.button("Generate Test Execution Script", key="generate_test_script", disabled=st.session_state.get('test_script_status') == "Running"):
        st.session_state['test_script_status'] = "Running"
        
        if not st.session_state.get('robo_script'):
            st.error("Please generate a Robo script first.")
            st.session_state['test_script_status'] = "Ready"
            return
        
        robo_script_formatted = st.session_state['robo_script']
        
        test_script_prompt = load_prompt("test_execution", 
                                         use_case=use_case, 
                                         robo_script=robo_script_formatted,
                                         language=language)
        
        if test_script_prompt:
            with st.spinner("Generating Test Execution Script..."):
                test_script_response = ""
                for chunk in get_gemini_pro_response(multimodal_model_pro, test_script_prompt):
                    test_script_response += chunk
                st.session_state['test_execution_script'] = test_script_response
            st.session_state['test_script_status'] = "Completed"
        else:
            st.session_state['test_script_status'] = "Ready"

def render_custom_css():
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
            border-radius: 4px 4px 0px 0px;
            gap: 12px;
            padding: 10px 20px;
        }
        .stTabs [aria-selected="true"] {
            border-bottom-color: transparent;
        }
        .stButton button:disabled {
            background-color: #cccccc;
            color: #666666;
            cursor: not-allowed;
        }
        .status-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 5px;
        }
        .status-ready { background-color: #FFA500; }
        .status-running { background-color: #1E90FF; }
        .status-completed { background-color: #32CD32; }
        .config-section {
            background-color: #f0f2f6;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
    </style>
    """, unsafe_allow_html=True)

def render_header():
    st.title("🤖 Firebase TestLab Robo Script Generator")
    
    st.markdown("""
    This demo showcases the capabilities of our Gemini Models in analyzing user interactions with mobile applications and generating Robo scripts for Firebase Test Lab.
    By capturing user actions from a video, we create a script that can reproduce these steps for automated testing.
    """)

def render_config_section():
    st.header("📊 Configuration")
    
    with st.expander("Configuration Options", expanded=True):
        col1, col2, col3 = st.columns(3)
        
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
                list(video_uris.keys()),
                key="use_case"
            )
        
        with col3:
            st.write("Reset Demo")
            if st.button("Reset", key="reset_demo"):
                for key in ['robo_script', 'robo_script_status', 'video_description', 'video_description_status', 'test_execution_script', 'test_script_status']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
    
    return model_region, model_name, language, use_case

def render_video_analysis_section(video_url, use_case, language, selected_video_uri, multimodal_model_pro):
    st.header("🎥 Video Analysis and Results")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("User Interaction Video")
        st.video(video_url)
    
        # Status indicators
        st.subheader("📊 Generation Status")
        statuses = {
            'Video Description': st.session_state.get('video_description_status', 'Ready'),
            'Robo Script': st.session_state.get('robo_script_status', 'Ready'),
            'Test Execution Script': st.session_state.get('test_script_status', 'Ready')
        }
        
        for name, status in statuses.items():
            color = 'status-ready' if status == 'Ready' else 'status-running' if status == 'Running' else 'status-completed'
            st.markdown(f'<span class="status-indicator {color}"></span> {name}: {status}', unsafe_allow_html=True)

        # Progress tracking
        total_steps = 3
        completed_steps = sum(1 for status in statuses.values() if status == 'Completed')
        st.progress(completed_steps / total_steps, text=f"Overall Progress: {completed_steps}/{total_steps} steps completed")
    
    with col2:
        st.subheader("Generated Results")
        
        tab1, tab2, tab3, tab4 = st.tabs(["📝 Video Description", "🔧 Robo Script", "🚀 Test Execution", "🔍 Prompts"])
        
        with tab1:
            generate_video_description(use_case, language, selected_video_uri, multimodal_model_pro)
            if 'video_description' in st.session_state:
                st.markdown(st.session_state['video_description'])
        
        with tab2:
            generate_robo_script(use_case, language, selected_video_uri, multimodal_model_pro)
            if 'robo_script' in st.session_state:
                st.write(st.session_state['robo_script'], language="json")
        
        with tab3:
            generate_test_execution_script(use_case, language, multimodal_model_pro)
            if 'test_execution_script' in st.session_state:
                st.write(st.session_state['test_execution_script'], language="bash")
        
        with tab4:
            st.subheader("Prompts Used")
            with st.expander("Video Description Prompt"):
                st.code(load_prompt("video_description", language=language, use_case=use_case), language="markdown")
            with st.expander("Robo Script Prompt"):
                st.code(load_prompt("robo_script", language=language, use_case=use_case, video_description="[Video description will appear here after generation]"), language="markdown")
            with st.expander("Test Execution Prompt"):
                st.code(load_prompt("test_execution", language=language, use_case=use_case, robo_script="[Robo script will appear here after generation]"), language="markdown")

def main():
    render_custom_css()
    render_header()
    model_region, model_name, language, use_case = render_config_section()
    
    load_vertex(model_region)
    text_model_pro, multimodal_model_pro = load_models(model_name)
    
    selected_video_uri = video_uris[use_case]
    video_url = "https://storage.googleapis.com/" + selected_video_uri.split("gs://")[1]
    
    render_video_analysis_section(video_url, use_case, language, selected_video_uri, multimodal_model_pro)

if __name__ == "__main__":
    main()