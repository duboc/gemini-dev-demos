import streamlit as st
from apps.firebase.generation import generate_video_description, generate_robo_script, generate_test_execution_script

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
                ["E-commerce (Nike)", "Pharmacy (Raia)", "Healthcare"],
                key="use_case"
            )
        
        with col3:
            st.write("Reset Demo")
            if st.button("Reset", key="reset_demo"):
                for key in ['robo_script', 'robo_script_status', 'video_description', 'video_description_status', 'test_execution_script', 'test_script_status']:
                    st.session_state[key] = None if key in ['robo_script', 'video_description', 'test_execution_script'] else "Ready"
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
        
        tab1, tab2, tab3 = st.tabs(["📝 Video Description", "🔧 Robo Script", "🚀 Test Execution"])
        
        with tab1:
            generate_video_description(use_case, language, selected_video_uri, multimodal_model_pro)
            if st.session_state.get('video_description'):
                st.markdown(st.session_state['video_description'])
        
        with tab2:
            generate_robo_script(use_case, language, selected_video_uri, multimodal_model_pro)
            if st.session_state.get('robo_script'):
                st.write(st.session_state['robo_script'])
        
        with tab3:
            generate_test_execution_script(use_case, language, multimodal_model_pro)
            if st.session_state.get('test_execution_script'):
                st.code(st.session_state['test_execution_script'], language="bash")