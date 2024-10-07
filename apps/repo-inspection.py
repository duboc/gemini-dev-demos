import streamlit as st
import time
import re
import vertexai
import os
import shutil
from pathlib import Path
import git
import magika
from vertexai.generative_models import GenerativeModel
import vertexai.preview.generative_models as generative_models
import pandas as pd

# Initialize Vertex AI
PROJECT_ID = os.environ.get('GCP_PROJECT')
LOCATION = os.environ.get('GCP_REGION')
vertexai.init(project=PROJECT_ID, location=LOCATION)

# Initialize Magika
m = magika.Magika()

# Constants
MODEL_ID = "gemini-1.5-flash-002"
REPO_DIR = "./repo"

# Safety settings
safety_settings = {
    generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_NONE,
    generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_NONE,
    generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_NONE,
    generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_NONE,
}

st.markdown("""
    <style>
    .stVideo {
        width: 400px !important;
        height: auto !important;
        margin: 0 auto;
    }
    </style>
    """, unsafe_allow_html=True)
# Initialize Gemini model
model = GenerativeModel(MODEL_ID, safety_settings=safety_settings)

# Helper functions
def stream_prompt(input):
    token_size = model.count_tokens(input)
    total_tokens = int(re.search(r"total_tokens:\s*(\d+)", str(token_size)).group(1))
    if total_tokens > 2000000:
        raise ValueError("Total tokens must be less than 2000000")

    billable_characters = int(re.search(r"total_billable_characters:\s*(\d+)", str(token_size)).group(1))
    cost = (billable_characters / 1000) * 0.0025

    response = model.generate_content(
        input,
        generation_config={
            "max_output_tokens": 8192,
            "temperature": 0.4,
            "top_p": 1
        },
        safety_settings=safety_settings,
        stream=True,
    )
    return response, cost

def get_code_prompt(question, code_index, code_text):
    return f"""
    Task: {question}

    Context:
    - You are an expert code analyzer and technical writer.
    - The entire codebase is provided below.
    - Here is an index of all the files in the codebase:
      \n\n{code_index}\n\n
    - The content of each file is concatenated below:
      \n\n{code_text}\n\n

    Instructions:
    1. Carefully analyze the provided codebase.
    2. Focus on addressing the specific task or question given.
    3. Provide a comprehensive and well-structured response.
    4. Use markdown formatting to enhance readability.
    5. If relevant, include code snippets or examples from the codebase.
    6. Ensure your analysis is accurate, insightful, and actionable.

    Response:
    """

def clone_repo(repo_url, repo_dir):
    if os.path.exists(repo_dir):
        shutil.rmtree(repo_dir)
    os.makedirs(repo_dir)
    git.Repo.clone_from(repo_url, repo_dir)
    return True

def extract_code(repo_dir):
    code_index = []
    code_text = ""
    for root, _, files in os.walk(repo_dir):
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, repo_dir)
            code_index.append(relative_path)

            file_type = m.identify_path(Path(file_path))
            if file_type.output.group in ("text", "code"):
                try:
                    with open(file_path, "r") as f:
                        code_text += f"----- File: {relative_path} -----\n"
                        code_text += f.read()
                        code_text += "\n-------------------------\n"
                except Exception:
                    pass
    return code_index, code_text


st.title("Gemini Repo Inspection")
st.markdown("""
This advanced tool uses the Gemini Experimental model to analyze GitHub repositories and provide in-depth insights.
The model can handle large codebases but is limited to 1 million tokens.
Responses are streamed in real-time as they are generated, providing immediate feedback.
""")

# Initialize session state
if 'analyses' not in st.session_state:
    st.session_state.analyses = []
if 'costs' not in st.session_state:
    st.session_state.costs = []

# Two-column layout
col1, col2 = st.columns([4, 6])

with col1:
    # Step 1: Repo Input
    st.header("Step 1: Repository Input", divider="gray")
    repo_url = st.text_input("Enter a GitHub repository URL:", "https://github.com/GoogleCloudPlatform/microservices-demo")

    if st.button("Clone and Index Repository"):
        with st.spinner("Cloning and indexing repository..."):
            clone_success = clone_repo(repo_url, REPO_DIR)
            if clone_success:
                code_index, code_text = extract_code(REPO_DIR)
                st.session_state["index"] = code_index
                st.session_state["text"] = code_text
                st.success("Repository cloned and indexed successfully!")

    # Step 2: Analysis Selection
    st.header("Step 2: Choose and Generate Analysis", divider="gray")
    analysis_options = {
        "summary": "Provide a comprehensive summary of the codebase, highlighting its architecture, main components, and top 3 key learnings for developers.",
        "readme": "Generate a detailed README for the application, including project overview, setup instructions, main features, and contribution guidelines.",
        "onboarding": "Create an in-depth getting started guide for new developers, covering setup process, code structure, development workflow, and best practices.",
        "issues": "Conduct a thorough code review to identify and explain the top 3 most critical issues or areas for improvement in the codebase.",
        "bug_fix": "Identify the most severe potential bug or vulnerability in the codebase, explain its impact, and provide a detailed fix with code examples.",
        "troubleshooting": "Develop a comprehensive troubleshooting guide for common issues, including potential error scenarios, diagnostics steps, and resolution procedures.",
        "custom": "Custom analysis (specify your own prompt)"
    }
    selected_analysis = st.selectbox("Select the type of analysis:", list(analysis_options.keys()), format_func=lambda x: x.capitalize())

    # Display explanation for selected analysis type
    if selected_analysis != "custom":
        st.text_area("Analysis Description:", value=analysis_options[selected_analysis], height=100, disabled=True)
    else:
        custom_prompt = st.text_area("Enter your custom analysis prompt:", height=100)

    if st.button("Generate Analysis"):
        if "index" not in st.session_state or "text" not in st.session_state:
            st.error("Please clone and index a repository first.")
        else:
            question = custom_prompt if selected_analysis == "custom" else analysis_options[selected_analysis]
            prompt = get_code_prompt(question, st.session_state["index"], st.session_state["text"])
            response, cost = stream_prompt(prompt)
            
            analysis_container = st.empty()
            full_response = ""
            
            for chunk in response:
                if chunk.text:
                    full_response += chunk.text
                    analysis_container.markdown(full_response + "▌")
            
            analysis_container.markdown(full_response)
            
            st.success("Analysis generated successfully!")
            st.session_state.analyses.append((selected_analysis, full_response))
            st.session_state.costs.append(cost)

with col2:
    # API Costs Table
    st.header("API Costs", divider="gray")
    if st.session_state.costs:
        cost_df = pd.DataFrame({
            "Analysis": [a[0].capitalize() for a in st.session_state.analyses],
            "Cost ($)": st.session_state.costs
        })
        cost_df["Cumulative Cost ($)"] = cost_df["Cost ($)"].cumsum()
        st.dataframe(cost_df, use_container_width=True)
        st.info(f"Total cost: ${sum(st.session_state.costs):.4f}")
    else:
        st.info("No analyses performed yet.")

    # Collapsible Session Analyses
    st.header("Session Analyses", divider="gray")
    for idx, (analysis_type, analysis_text) in enumerate(st.session_state.analyses):
        with st.expander(f"Analysis {idx + 1}: {analysis_type.capitalize()}"):
            st.markdown(analysis_text)

    # Clear all analyses
    if st.button("Clear All Analyses"):
        st.session_state.analyses = []
        st.session_state.costs = []
        st.success("All analyses cleared!")