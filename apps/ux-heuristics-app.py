import streamlit as st
from config import (
    load_vertex,
    load_models,
    get_gemini_pro_vision_response_stream,
    read_prompt,
    video_uris
)
from vertexai.generative_models import Part

# Custom CSS (same as before)
st.markdown("""
<style>
    .stVideo {
        width: 100%;
        max-width: 400px;
        margin: auto;
    }
    .stButton button:disabled {
        background-color: #cccccc;
        color: #666666;
        cursor: not-allowed;
    }
</style>
""", unsafe_allow_html=True)

st.title("UX Heuristic Analysis using Gemini AI")

st.markdown("""
This demo showcases the power of Gemini AI in analyzing user experience (UX) based on Nielsen's 10 Usability Heuristics. 
By examining video recordings of user interactions with mobile apps, we can identify usability issues and suggest improvements.

**How it works:**
1. Select your preferences (model, region, language, and use case).
2. Generate a UX Heuristic Analysis based on the selected video.
3. Create User Stories from the Heuristic Analysis to prioritize improvements.

Let's get started!
""")

# Initialize session state variables
if 'heuristic_analysis' not in st.session_state:
    st.session_state['heuristic_analysis'] = None
if 'user_stories' not in st.session_state:
    st.session_state['user_stories'] = None
if 'heuristic_analysis_state' not in st.session_state:
    st.session_state['heuristic_analysis_state'] = 'Ready'
if 'user_stories_state' not in st.session_state:
    st.session_state['user_stories_state'] = 'Ready'

# Two-column layout
col1, col2 = st.columns([1, 3])

with col1:
    st.header("Configuration")

    model_region = st.selectbox(
        "Select Gemini region:",
        ["us-central1", "southamerica-east1", "us-east1", "us-south1", "europe-southwest1"],
        key="model_region",
    )

    model_name = st.selectbox(
        "Select Gemini model:",
        ["gemini-experimental", "gemini-1.5-pro-002", "gemini-1.5-flash-002"],
        key="model_name",
        index=0,
    )

    story_lang = st.selectbox(
        "Select output language:",
        ["Portuguese", "Spanish", "English"],
        key="story_lang",
    )

    use_case = st.selectbox(
        "Select use case:",
        list(video_uris.keys()),
        key="use_case",
    )

    load_vertex(model_region)
    text_model_pro, multimodal_model_pro = load_models(model_name)

    heuristic_prompt = read_prompt('prompts/heuristic_prompt.md')

    video_uri = video_uris[use_case]
    video_url = ("https://storage.googleapis.com/" + video_uri.split("gs://")[1])

    st.subheader("Video for Analysis")
    st.video(video_url)

    if st.button("Reset Demo"):
        for key in ['heuristic_analysis', 'user_stories', 'heuristic_analysis_state', 'user_stories_state']:
            st.session_state[key] = None if key.endswith('analysis') or key.endswith('stories') else 'Ready'
        st.rerun()

with col2:
    st.header("Analysis Results")
    tab1, tab2, tab3 = st.tabs(["UX Heuristic Analysis", "User Stories", "Prompts"])

    with tab1:
        if st.button("Generate UX Heuristic Analysis", key="generate_heuristic_analysis", disabled=st.session_state['heuristic_analysis_state'] == 'Running'):
            st.session_state['heuristic_analysis_state'] = 'Running'
            with st.spinner("Analyzing video and generating heuristic analysis..."):
                prompt = f"All answers should be provided in {story_lang} {heuristic_prompt}"
                video_part = Part.from_uri(video_uri, mime_type="video/mp4")
                try:
                    response = ""
                    for chunk in get_gemini_pro_vision_response_stream(multimodal_model_pro, [prompt, video_part]):
                        response += chunk.text
                    st.session_state['heuristic_analysis'] = response
                    st.session_state['heuristic_analysis_state'] = 'Completed'
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                    st.session_state['heuristic_analysis_state'] = 'Ready'

        if st.session_state['heuristic_analysis']:
            st.markdown("## UX Heuristic Analysis")
            st.markdown(st.session_state['heuristic_analysis'])
        else:
            st.info("Click 'Generate UX Heuristic Analysis' to see the results here.")
        
        st.write(f"Status: {st.session_state['heuristic_analysis_state']}")

    with tab2:
        user_story_prompt = read_prompt('prompts/user_story_prompt.md')
        if st.button("Generate User Stories", key="generate_user_stories", disabled=st.session_state['user_stories_state'] == 'Running' or st.session_state['heuristic_analysis'] is None):
            if st.session_state['heuristic_analysis'] is None:
                st.warning("Please generate the UX Heuristic Analysis first.")
            else:
                st.session_state['user_stories_state'] = 'Running'
                with st.spinner("Creating user stories from the heuristic analysis..."):
                    full_prompt = f"All answers should be provided in {story_lang}. {user_story_prompt}"
                    try:
                        user_story_response = ""
                        video_part = Part.from_uri(video_uri, mime_type="video/mp4")
                        for chunk in get_gemini_pro_vision_response_stream(multimodal_model_pro, [full_prompt, video_part, st.session_state['heuristic_analysis']]):
                            user_story_response += chunk.text
                        st.session_state['user_stories'] = user_story_response
                        st.session_state['user_stories_state'] = 'Completed'
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")
                        st.session_state['user_stories_state'] = 'Ready'

        if st.session_state['user_stories']:
            st.markdown("## User Stories")
            st.markdown(st.session_state['user_stories'])
        else:
            st.info("Generate the UX Heuristic Analysis first, then click 'Generate User Stories' to see the results here.")
        
        st.write(f"Status: {st.session_state['user_stories_state']}")

    with tab3:
        st.subheader("Prompts")
        with st.expander("UX Heuristic Analysis Prompt", expanded=False):
            st.code(heuristic_prompt, language="markdown")
        with st.expander("User Story Prompt", expanded=False):
            st.code(user_story_prompt, language="markdown")

st.markdown("---")
st.markdown("Made with ❤️ using Streamlit and Gemini AI")
