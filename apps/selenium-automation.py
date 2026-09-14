import streamlit as st
from google.genai import types

from utils_streamlit import reset_st_state
from utils_vertex import MODEL_ID, generation_config, get_client

if 'response' not in st.session_state:
    st.session_state['response'] = 'init'
if 'token_totals' not in st.session_state:
    st.session_state['token_totals'] = []
if 'session_analyses' not in st.session_state:
    st.session_state['session_analyses'] = []

st.markdown("""
    <style>
    .stVideo {
        width: 400px !important;
        height: auto !important;
        margin: 0 auto;
    }
    </style>
    """, unsafe_allow_html=True)

def get_gemini_pro_vision_response(model, prompt_list):
    responses = get_client().models.generate_content_stream(
        model=model,
        contents=prompt_list,
        config=generation_config(temperature=0.1, max_output_tokens=2048),
    )
    final_response = []
    for response in responses:
        if response.text:
            final_response.append(response.text)
    return "".join(final_response)

def count_tokens(model, text):
    """Return the token count for a prompt or an answer.

    The retired SDK also returned `total_billable_characters`, and this demo
    priced the run from it. google-genai reports only tokens, and Vertex AI
    publishes no per-character price, so the demo reports tokens and leaves the
    arithmetic to https://cloud.google.com/vertex-ai/generative-ai/pricing
    """
    response = get_client().models.count_tokens(model=model, contents=text)
    return response.total_tokens or 0

def update_session_analysis(action, tokens):
    st.session_state['session_analyses'].append({
        "Action": action,
        "Tokens": tokens
    })

st.header("Generate Selenium Test from Video", divider="rainbow")

if reset := st.button("Reset Demo State"):
    reset_st_state()

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("""
    This demo showcases Gemini Models' capabilities:
    1. Analyze video content
    2. Generate detailed descriptions
    3. Create Selenium scripts for web automation
    
    Select options and click 'Generate' to start!
    """)

    model_name = st.radio(
        label="Model:",
        options=[MODEL_ID],
        key="model_name",
        index=0,
        horizontal=True
    )

    story_lang = st.radio(
        "Output language:",
        ["Portuguese", "Spanish", "English"],
        key="story_lang",
        horizontal=True,
    )

    vide_desc_uri = "gs://convento-samples/boa-selenium-rag.mov"
    video_desc_url = ("https://storage.googleapis.com/" + vide_desc_uri.split("gs://")[1])

    st.video(video_desc_url)

    prompt = f"""Describe the video content concisely, focusing on:
    1. Timestamped list of user actions
    2. Purpose of each action
    3. Relevant screen information

    Provide the description in {story_lang}.
    """

    vide_desc_img = types.Part.from_uri(file_uri=vide_desc_uri, mime_type="video/mp4")

with col2:
    # Session token usage at the top right
    st.subheader("Session token usage")
    st.metric("Total tokens this session", sum(st.session_state['token_totals']))

    # Session Analyses
    st.subheader("Session Analyses")
    if st.session_state['session_analyses']:
        st.table(st.session_state['session_analyses'])
    else:
        st.info("No actions performed yet.")

    # Generate button moved under session analyses
    vide_desc_description = st.button("Generate", key="vide_desc_description")

    if vide_desc_description and prompt:
        with st.spinner("Analyzing video and generating description..."):
            response = get_gemini_pro_vision_response(model_name, [prompt, vide_desc_img])
            st.session_state["response"] = response

            # Record the tokens this generation consumed
            input_tokens = count_tokens(model_name, prompt)
            output_tokens = count_tokens(model_name, response)
            st.session_state['token_totals'].append(input_tokens + output_tokens)
            update_session_analysis("Generate Description", input_tokens + output_tokens)

    if st.session_state["response"] != "init":
        st.subheader("Token usage")

        input_tokens = count_tokens(model_name, prompt)
        output_tokens = count_tokens(model_name, st.session_state["response"])

        token_data = {
            "Metric": ["Input", "Output", "Total"],
            "Tokens": [input_tokens, output_tokens, input_tokens + output_tokens],
        }

        st.table(token_data)
        st.caption(
            "Vertex AI prices Gemini per token. For the rate that applies to "
            "this model, read the Vertex AI pricing page."
        )

        with st.expander("Video Description", expanded=True):
            st.markdown(st.session_state["response"])

        generate_selenium = st.button("Create Selenium Script", key="generate_selenium")
        if generate_selenium:
            with st.spinner("Generating Selenium code..."):
                prompt_selenium = f"""Create a Selenium script to automate the tasks described:

                {st.session_state["response"]}
                """
                selenium_response = get_gemini_pro_vision_response(model_name, [prompt_selenium, vide_desc_img])

                with st.expander("Selenium Script", expanded=True):
                    st.code(selenium_response, language="python")

                # Record the tokens the Selenium generation consumed
                script_tokens = (
                    count_tokens(model_name, prompt_selenium)
                    + count_tokens(model_name, selenium_response)
                )
                st.session_state['token_totals'].append(script_tokens)
                update_session_analysis("Generate Selenium Script", script_tokens)