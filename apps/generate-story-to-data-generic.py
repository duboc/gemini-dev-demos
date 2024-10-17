import streamlit as st
from utils_vertex import sendPrompt, model_experimental, model_gemini_pro_15_002, model_gemini_flash_002
from utils_streamlit import reset_st_state
import os

def load_models(model_name):
    if model_name == "gemini-experimental":
        return model_experimental
    elif model_name == "gemini-1.5-pro-002":
        return model_gemini_pro_15_002
    else:
        return model_gemini_flash_002

def load_questions(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read().splitlines()
    except FileNotFoundError:
        st.warning(f"File not found: {file_path}. Falling back to English version.")
        english_file_path = file_path.replace('-es.txt', '-en.txt').replace('-pt.txt', '-en.txt')
        with open(english_file_path, 'r', encoding='utf-8') as f:
            return f.read().splitlines()

def load_prompt(file_name):
    with open(os.path.join("prompts", file_name + ".md"), "r", encoding="utf-8") as file:
        return file.read()


#def load_prompt(file_name):
#    with open(f"./prompts/{file_name}.md", "r") as file:#
#        return file.read()

if 'results' not in st.session_state:
    st.session_state['results'] = []

if st.button("Reset Demo State", key="reset_button"):
    reset_st_state()
    st.session_state['results'] = []

st.title("User Story to Data 📊")

# Initialize button states in session state if not already present
if 'button_states' not in st.session_state:
    st.session_state.button_states = {
        'generate_story': False,
        'generate_tasks': False,
        'generate_dw': False,
        'generate_bigquery': False
    }

def create_button_with_status(label, key, disabled=False):
    col1, col2 = st.columns([3, 1])
    with col1:
        clicked = st.button(label, key=key, disabled=disabled)
    with col2:
        if st.session_state.button_states.get(key, False):
            st.markdown(':green[Completed]')
        elif disabled:
            st.markdown(':gray[Waiting]')
        else:
            st.markdown(':blue[Ready]')
    return clicked

def update_button_state(button_key):
    st.session_state.button_states[button_key] = True

col1, col2 = st.columns([1, 4])

with col1:
    st.subheader("Configuration")
    model_name = st.radio(
        "Model:",
        ["gemini-1.5-pro-002", "gemini-1.5-flash-002", "gemini-experimental"],
        captions=["Gemini Pro 1.5", "Gemini Flash 1.5", "Gemini Pro Experimental"],
        key="model_name",
        index=0,
        horizontal=True
    )

    model = load_models(model_name)

    selected_category = st.selectbox(
        "Select Industry:",
        ["retail", "energy", "health", "finance", "beauty", "games", "ecom", "education", "fintech" ],
        key="category"
    )


    story_lang = st.radio(
        "Select language for story generation:",
        ["Portuguese", "English", "Spanish"],
        key="story_lang",
        horizontal=True,
    )

    # Map selected language to file suffix
    lang_suffix = {
        "English": "en",
        "Portuguese": "pt",
        "Spanish": "es"
    }

    QUESTIONS_FILE = f"./data/{selected_category}-{lang_suffix[story_lang]}.txt"
    questions = load_questions(QUESTIONS_FILE)

    persona_name = st.text_input("Persona:", key="persona_name", value="Breno Cabral")

with col2:
    selected_index = st.selectbox('Select a theme:', 
                                  range(len(questions)), 
                                  format_func=lambda i: questions[i], 
                                  key="user_story")
    st.subheader("User Theme")
    user_story = st.text_area("Edit your theme:", value=questions[selected_index], height=200)

    if create_button_with_status("1. Generate my story", "generate_story"):
        prompt = load_prompt("story_prompt").format(
            persona_name=persona_name,
            user_story=user_story,
            story_lang=story_lang
        )

        with st.spinner("Generating your story using Gemini ..."):
            responseStory = sendPrompt(prompt, model)
            if responseStory:
                st.session_state['results'].append(("User Story", responseStory, prompt))
                update_button_state('generate_story')
                st.rerun()

    if create_button_with_status("2. Generate tasks from user story", "generate_tasks", 
                                 disabled=not st.session_state.button_states.get('generate_story', False)):
        if st.session_state['results']:
            last_story = next((result for result in reversed(st.session_state['results']) if result[0] == "User Story"), None)
            if last_story:
                promptTasks = load_prompt("tasks_prompt").format(story_lang=story_lang) + last_story[1]

                with st.spinner("Generating your tasks using Gemini Pro ..."):
                    responseTasks = sendPrompt(promptTasks, model)
                    if responseTasks:
                        st.session_state['results'].append(("Tasks", responseTasks, promptTasks))
                        update_button_state('generate_tasks')
                        st.rerun()
            else:
                st.warning("Please generate a user story first.")
        else:
            st.warning("Please generate a user story first.")

    if create_button_with_status("3. Create DW from tasks", "generate_dw", 
                                 disabled=not st.session_state.button_states.get('generate_tasks', False)):
        if st.session_state['results']:
            last_tasks = next((result for result in reversed(st.session_state['results']) if result[0] == "Tasks"), None)
            if last_tasks:
                promptDW = load_prompt("dw_prompt").format(story_lang=story_lang) + last_tasks[1]

                with st.spinner("Generating your DW using Gemini..."):
                    responseDW = sendPrompt(promptDW, model)
                    if responseDW:
                        st.session_state['results'].append(("DW Snippets", responseDW, promptDW))
                        update_button_state('generate_dw')
                        st.rerun()
            else:
                st.warning("Please generate tasks first.")
        else:
            st.warning("Please generate a user story and tasks first.")

    if create_button_with_status("4. Create BigQuery Implementation", "generate_bigquery", 
                                 disabled=not st.session_state.button_states.get('generate_dw', False)):
        if st.session_state['results']:
            last_dw = next((result for result in reversed(st.session_state['results']) if result[0] == "DW Snippets"), None)
            if last_dw:
                promptBigQuery = load_prompt("bigquery_prompt").format(story_lang=story_lang) + last_dw[1]

                with st.spinner("Generating your BigQuery implementation using Gemini..."):
                    responseBigQuery = sendPrompt(promptBigQuery, model)
                    if responseBigQuery:
                        st.session_state['results'].append(("BigQuery Snippets", responseBigQuery, promptBigQuery))
                        update_button_state('generate_bigquery')
                        st.rerun()
            else:
                st.warning("Please create DW snippets first.")
        else:
            st.warning("Please generate a user story, tasks, and DW snippets first.")

# Display all results
st.subheader("Results")
for result_type, result_content, prompt in reversed(st.session_state['results']):
    with st.expander(f"{result_type} - Click to expand/collapse"):
        st.markdown("### Generated Content")
        st.markdown(result_content)
        st.markdown("### Prompt Used")
        st.code(prompt, language="markdown")