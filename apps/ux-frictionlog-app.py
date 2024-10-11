import streamlit as st
from config import (
    load_vertex,
    load_models,
    get_gemini_pro_vision_response_stream,
    read_prompt,
    video_uris
)
from vertexai.generative_models import Part

# Custom CSS to resize video, style tabs, and improve button appearance
st.markdown("""
<style>
    .stVideo {
        width: 100%;
        max-width: 800px;
        margin: auto;
    }
    .stButton button:disabled {
        background-color: #cccccc;
        color: #666666;
        cursor: not-allowed;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state variables
if 'friction_log' not in st.session_state:
    st.session_state['friction_log'] = None
if 'user_story' not in st.session_state:
    st.session_state['user_story'] = None
if 'task_backlog' not in st.session_state:
    st.session_state['task_backlog'] = None
if 'friction_status' not in st.session_state:
    st.session_state['friction_status'] = "Ready"
if 'user_story_status' not in st.session_state:
    st.session_state['user_story_status'] = "Ready"
if 'task_backlog_status' not in st.session_state:
    st.session_state['task_backlog_status'] = "Ready"

st.title("UX Friction Log Generator")

st.markdown("""
This demo showcases the capabilities of our Gemini Models in analyzing user experience (UX) of websites and applications.
By capturing user actions and providing visual aids, we allow for a deeper understanding of usability and identify areas for improvement.
The generated friction log, user stories, and task backlog can be used to pinpoint pain points in the UX and suggest solutions for a smoother, more intuitive user experience.
""")

# Two-column layout
col1, col2 = st.columns([1, 3])

with col1:
    # Configuration section
    st.header("Configuration")

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

    language = st.radio(
        "Select language for generation:",
        ["Portuguese", "Spanish", "English"],
        key="language"
    )

    use_case = st.selectbox(
        "Select use case:",
        list(video_uris.keys()),
        key="use_case"
    )

    # Load models and video
    load_vertex(model_region)
    text_model_pro, multimodal_model_pro = load_models(model_name)

    selected_video_uri = video_uris[use_case]
    video_url = "https://storage.googleapis.com/" + selected_video_uri.split("gs://")[1]

    st.header("User Interaction Video")
    st.video(video_url)

    # Reset button
    if st.button("Reset Demo"):
        for key in ['friction_log', 'user_story', 'task_backlog', 'friction_status', 'user_story_status', 'task_backlog_status']:
            st.session_state[key] = None if key.endswith('log') or key.endswith('story') or key.endswith('backlog') else "Ready"
        st.rerun()

with col2:
    # Display results in tabs
    st.header("Analysis Results")
    tab1, tab2, tab3, tab4 = st.tabs(["Friction Log", "User Story", "Task Backlog", "Prompts"])
    
    with tab1:
        friction_prompt = read_prompt('prompts/friction_log_prompt.md').format(language=language, use_case=use_case)
        if st.button("Generate Friction Log", key="generate_friction_log", disabled=st.session_state['friction_status'] == "Running"):
            st.session_state['friction_status'] = "Running"
            with st.spinner("Generating Friction Log..."):
                video_part = Part.from_uri(selected_video_uri, mime_type="video/mp4")
                friction_response = ""
                for chunk in get_gemini_pro_vision_response_stream(multimodal_model_pro, [friction_prompt, video_part]):
                    friction_response += chunk.text
                st.session_state['friction_log'] = friction_response
            st.session_state['friction_status'] = "Completed"

        if st.session_state['friction_log']:
            st.markdown(st.session_state['friction_log'])
        else:
            st.info("Click the 'Generate Friction Log' button to see results here.")
        
        st.write(f"Status: {st.session_state['friction_status']}")
    
    with tab2:
        user_story_prompt = read_prompt('prompts/user_story_prompt.md').format(language=language)
        if st.button("Generate User Story", key="generate_user_story", disabled=st.session_state['user_story_status'] == "Running" or st.session_state['friction_log'] is None):
            st.session_state['user_story_status'] = "Running"
            with st.spinner("Generating User Story..."):
                user_story_response = ""
                for chunk in get_gemini_pro_vision_response_stream(text_model_pro, [user_story_prompt + "\n" + st.session_state['friction_log']]):
                    user_story_response += chunk.text
                st.session_state['user_story'] = user_story_response
            st.session_state['user_story_status'] = "Completed"

        if st.session_state['user_story']:
            st.markdown(st.session_state['user_story'])
        else:
            st.info("Generate the Friction Log first, then click 'Generate User Story' to see results here.")
        
        st.write(f"Status: {st.session_state['user_story_status']}")
    
    with tab3:
        task_backlog_prompt = read_prompt('prompts/task_backlog_prompt.md').format(language=language)
        if st.button("Generate Task Backlog", key="generate_task_backlog", disabled=st.session_state['task_backlog_status'] == "Running" or st.session_state['user_story'] is None):
            st.session_state['task_backlog_status'] = "Running"
            with st.spinner("Generating Task Backlog..."):
                task_backlog_response = ""
                for chunk in get_gemini_pro_vision_response_stream(text_model_pro, [task_backlog_prompt + "\n" + st.session_state['user_story']]):
                    task_backlog_response += chunk.text
                st.session_state['task_backlog'] = task_backlog_response
            st.session_state['task_backlog_status'] = "Completed"

        if st.session_state['task_backlog']:
            st.markdown(st.session_state['task_backlog'])
        else:
            st.info("Generate the User Story first, then click 'Generate Task Backlog' to see results here.")
        
        st.write(f"Status: {st.session_state['task_backlog_status']}")
    
    with tab4:
        st.subheader("Prompts")
        with st.expander("Friction Log Prompt", expanded=False):
            st.code(friction_prompt, language="markdown")
        with st.expander("User Story Prompt", expanded=False):
            st.code(user_story_prompt, language="markdown")
        with st.expander("Task Backlog Prompt", expanded=False):
            st.code(task_backlog_prompt, language="markdown")

st.markdown("---")
st.markdown("Made with ❤️ using Streamlit and Gemini AI")