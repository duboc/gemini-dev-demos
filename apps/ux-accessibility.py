import streamlit as st
from config import (
    load_vertex,
    load_models,
    get_gemini_pro_vision_response_stream,
    read_prompt,
    video_uris,
    images_uris,
    model_experimental,
    model_gemini_pro_15,
    model_gemini_flash
)
from vertexai.generative_models import Part

st.markdown("""
    <style>
    .stVideo {
        width: 100% !important;
        height: auto !important;
        margin: 0 auto;
    }
    .stAlert {
        background-color: #f0f2f6;
        border: 1px solid #d1d5db;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .results-container {
        background-color: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-top: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("Video Accessibility Analyzer", anchor=False)

st.markdown("""
This tool analyzes the accessibility of mobile applications based on Web Content Accessibility Guidelines (WCAG).
It identifies areas for improvement to enhance user interaction and ensure compliance with accessibility standards.
""")

col1, col2 = st.columns([1, 3])

with col1:
    st.subheader("Configuration")

    model_region = st.selectbox(
        "Select Gemini region:",
        ["us-central1", "southamerica-east1", "us-east1", "us-south1", "europe-southwest1"],
        key="model_region",
    )

    load_vertex(model_region)

    model_name = st.radio(
        "Select Model:",
        ["gemini-experimental", "gemini-1.5-pro-002", "gemini-1.5-flash-002"],
        key="model_name",
        horizontal=True,
        index=0,
    )

    language = st.radio(
        "Select language for analysis:",
        ["Portuguese", "Spanish", "English"],
        key="language",
        horizontal=True,
    )

    use_case = st.selectbox(
        "Select application:",
        list(video_uris.keys()),
        key="use_case",
    )

    text_model_pro, multimodal_model_pro = load_models(model_name)

    video_uri = video_uris[use_case]
    video_url = ("https://storage.googleapis.com/" + video_uri.split("gs://")[1])
    
    st.subheader("Video Preview")
    st.video(video_url)

    if st.button("Reset Demo", key="reset_demo"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

with col2:
    wcag_prompt = read_prompt('prompts/wcag-compliance-analysis-prompt.md')
    user_stories_prompt = read_prompt('prompts/accessibility-user-stories-prompt.md')
    tasks_prompt = read_prompt('prompts/tasks_prompt.md')

    tabs = st.tabs(["WCAG Analysis", "User Stories", "Task Backlog", "Prompts"])

    with tabs[0]:
        st.subheader("WCAG Compliance Analysis")
        if st.button("Generate WCAG Analysis", key="generate_wcag_analysis"):
            with st.spinner("Generating WCAG Analysis..."):
                prompt_wcag = wcag_prompt.format(
                    language=language,
                    use_case=use_case
                )
                video_part = Part.from_uri(video_uri, mime_type="video/mp4")
                wcag_response_stream = get_gemini_pro_vision_response_stream(multimodal_model_pro, [prompt_wcag, video_part])
                
                full_response = ""
                for chunk in wcag_response_stream:
                    full_response += chunk.text

                st.session_state["wcag_analysis"] = full_response

        if "wcag_analysis" in st.session_state:
            with st.expander("WCAG Analysis Results", expanded=True):
                st.markdown('<div class="results-container">', unsafe_allow_html=True)
                st.markdown(st.session_state["wcag_analysis"])
                st.markdown('</div>', unsafe_allow_html=True)

    with tabs[1]:
        st.subheader("Accessibility User Stories")
        if st.button("Generate Accessibility User Stories", key="generate_user_story"):
            if "wcag_analysis" not in st.session_state:
                st.warning("Please generate the WCAG Analysis first.")
            else:
                with st.spinner("Generating User Stories..."):
                    prompt_user_story = user_stories_prompt.format(language=language)
                    prompt_user_story += "\n" + st.session_state["wcag_analysis"]
                    video_part = Part.from_uri(video_uri, mime_type="video/mp4")
                    user_story_response_stream = get_gemini_pro_vision_response_stream(multimodal_model_pro, [prompt_user_story, video_part])
                    
                    full_response = ""
                    for chunk in user_story_response_stream:
                        full_response += chunk.text

                    st.session_state["user_stories"] = full_response

        if "user_stories" in st.session_state:
            with st.expander("User Stories Results", expanded=True):
                st.markdown('<div class="results-container">', unsafe_allow_html=True)
                st.markdown(st.session_state["user_stories"])
                st.markdown('</div>', unsafe_allow_html=True)

    with tabs[2]:
        st.subheader("Task Backlog")
        if st.button("Generate Task Backlog", key="generate_task_backlog"):
            if "user_stories" not in st.session_state:
                st.warning("Please generate User Stories first.")
            else:
                with st.spinner("Generating Task Backlog..."):
                    prompt_tasks = tasks_prompt + "\n" + st.session_state["user_stories"]
                    tasks_response_stream = get_gemini_pro_vision_response_stream(text_model_pro, [prompt_tasks])
                    
                    full_response = ""
                    for chunk in tasks_response_stream:
                        full_response += chunk.text

                    st.session_state["task_backlog"] = full_response

        if "task_backlog" in st.session_state:
            with st.expander("Task Backlog Results", expanded=True):
                st.markdown('<div class="results-container">', unsafe_allow_html=True)
                st.markdown(st.session_state["task_backlog"])
                st.markdown('</div>', unsafe_allow_html=True)

    with tabs[3]:
        st.subheader("Prompts")
        with st.expander("WCAG Analysis Prompt", expanded=True):
            st.code(wcag_prompt, language="markdown")
        with st.expander("User Stories Prompt", expanded=True):
            st.code(user_stories_prompt, language="markdown")
        with st.expander("Task Backlog Prompt", expanded=True):
            st.code(tasks_prompt, language="markdown")