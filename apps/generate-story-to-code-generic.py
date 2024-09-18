import streamlit as st
from utils_vertex import sendPrompt, model_experimental, model_gemini_pro_15, model_gemini_flash
from utils_streamlit import reset_st_state

def load_models(model_name):
    if model_name == "gemini-experimental":
        return model_experimental
    elif model_name == "gemini-1.5-pro-001":
        return model_gemini_pro_15
    else:
        return model_gemini_flash

def load_questions(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read().splitlines()
    except FileNotFoundError:
        st.warning(f"File not found: {file_path}. Falling back to English version.")
        # Fallback to English version
        english_file_path = file_path.replace('-es.txt', '-en.txt').replace('-pt.txt', '-en.txt')
        with open(english_file_path, 'r', encoding='utf-8') as f:
            return f.read().splitlines()

if 'results' not in st.session_state:
    st.session_state['results'] = []

if st.button("Reset Demo State", key="reset_button"):
    reset_st_state()
    st.session_state['results'] = []

st.title("User Story to Code 💻 ")

# Initialize button states in session state
if 'button_states' not in st.session_state:
    st.session_state.button_states = {
        'generate_story': False,
        'generate_tasks': False,
        'generate_code': False,
        'generate_test': False
    }

# Function to update button state
def update_button_state(button_key):
    st.session_state.button_states[button_key] = True

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

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Configuration")
    model_name = st.radio(
        "Model:",
        ["gemini-experimental", "gemini-1.5-pro-001", "gemini-1.5-flash-001"],
        captions=["Gemini Pro Experimental", "Gemini Pro 1.5", "Gemini Flash 1.5"],
        key="model_name",
        index=0,
        horizontal=True
    )

    model = load_models(model_name)

    selected_category = st.radio(
        "Select Industry:",
        ["retail", "energy", "health", "finance", "beauty"],
        key="category"
    )

    story_lang = st.radio(
        "Select language for story generation:",
        ["English", "Portuguese", "Spanish"],
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
        prompt = f"""Write a User story based on the following premise:
        persona_name: {persona_name}
        user_story: {user_story}
        First start by giving the user Story a Summary: [concise, memorable, human-readable story title] 
        User Story Format example:
            As a: [persona_type]
            I want to: [Action or Goal]
            So that: [Benefit or Value]
            Additional Context: [Optional details about the scenario, environment, or specific requirements]
            Acceptance Criteria: [Specific, measurable conditions that must be met for the story to be considered complete]
                *   **Scenario**: 
                        [concise, human-readable user scenario]
                *   **Given**: 
                        [Initial context]
                *   **and Given**: 
                        [Additional Given context]
                *   **and Given** 
                        [additional Given context statements as needed]
                *   **When**: 
                        [Event occurs]
                *   **Then**: 
                        [Expected outcome]
        All the answers are required to be in {story_lang} and to stick to the persona. 
        """

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
                promptTasks = f"""All the answers are required to be in {story_lang} and to stick to the persona.
                Divide the user story into tasks as granular as possible.
                The goal of fragmenting a user story is to create a list of tasks that can be completed within a sprint.
                Therefore, it is important to break down the story into minimal tasks that still add value to the end user.
                This facilitates progress tracking and ensures that the team stays on track.
                Create a table with the tasks as the table index with the task description.
                """ + last_story[1]

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

    if create_button_with_status("3. Create Code from tasks", "generate_code",
                             disabled=not st.session_state.button_states.get('generate_tasks', False)):
        if st.session_state['results']:
            last_tasks = next((result for result in reversed(st.session_state['results']) if result[0] == "Tasks"), None)
            if last_tasks:
                promptCodeGeneration = f"""
                    Based on the list of tasks, create Python code snippets to implement the functionality for the first task in the list.
                    Identify specific constraints or requirements that impact the implementation:
                    Time or resource limitations
                    Compatibility with external APIs or libraries
                    Coding standards or style guidelines to be followed
                    Clearly document any assumptions or premises made.
                    Follow these directives:
                    - Use Google Style Guide for formatting
                    - Utilize existing tools and frameworks
                    - Ensure code reproducibility in different environments
                    - Format code with proper indentation and spacing
                    - Include explanatory comments for each section of the code
                    - Provide documentation with usage examples and additional information
                    All the answers are required to be in {story_lang} and to stick to the persona.
                    Create code only for the first task. Make a numbered list where the first item is the task name, the second is a summary of the code, and then include the generated snippet and as many new items as needed to complement the required information.
"""  + last_tasks[1]

                with st.spinner("Generating your code using Gemini..."):
                    responseCodeSnippets = sendPrompt(promptCodeGeneration, model)
                    if responseCodeSnippets:
                        st.session_state['results'].append(("Code Snippets", responseCodeSnippets, promptCodeGeneration))
                        update_button_state('generate_code')
                        st.rerun()
            else:
                st.warning("Please generate tasks first.")
        else:
            st.warning("Please generate a user story and tasks first.")

    if create_button_with_status("4. Create UnitTest Implementation", "generate_test",
                                 disabled=not st.session_state.button_states.get('generate_code', False)):
        if st.session_state['results']:
            last_code = next((result for result in reversed(st.session_state['results']) if result[0] == "Code Snippets"), None)
            if last_code:
                promptUnitTest = f"""
                    All the answers are required to be in {story_lang}.
                    You are an expert software developer specializing in writing high-quality unit tests. Your task is to create comprehensive unit tests for the given code snippet. Follow these guidelines:

                    Analyze the provided code carefully, identifying its purpose, inputs, outputs, and potential edge cases.
                    Create a suite of unit tests that covers:

                    Happy path scenarios
                    Edge cases
                    Error handling
                    Boundary conditions

                    Use appropriate testing frameworks and assertions based on the programming language of the code.
                    Follow best practices for unit testing, including:

                    Descriptive test names
                    Arrange-Act-Assert (AAA) pattern
                    One assertion per test when possible
                    Proper setup and teardown if needed

                    Include comments explaining the purpose of each test and any complex logic.
                    If the code has dependencies, suggest appropriate mocking or stubbing strategies.
                    Provide a brief explanation of your testing approach and any assumptions made.
                    Please generate a comprehensive set of unit tests for this code, following the guidelines above.

                    Given the following code snippet:

                    """ + last_code[1]

                with st.spinner("Generating your UnitTest implementation using Gemini..."):
                    responseUnitTest = sendPrompt(promptUnitTest, model)
                    if responseUnitTest:
                        st.session_state['results'].append(("UnitTest Snippets", responseUnitTest, promptUnitTest))
                        update_button_state('generate_test')
                        st.rerun()
            else:
                st.warning("Please create Code snippets first.")
        else:
            st.warning("Please generate a user story, tasks, and Code snippets first.")

# Display all results
st.subheader("Results")
for result_type, result_content, prompt in reversed(st.session_state['results']):
    with st.expander(f"{result_type} - Click to expand/collapse"):
        st.markdown("### Generated Content")
        st.markdown(result_content)
        st.markdown("### Prompt Used")
        st.code(prompt, language="markdown")