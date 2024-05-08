import streamlit as st
import random
import time
import re
import vertexai
import os
import shutil
from pathlib import Path
from utils_streamlit import reset_st_state
import git
import magika


from vertexai.generative_models import GenerativeModel, Part, FinishReason
import vertexai.preview.generative_models as generative_models


PROJECT_ID = os.environ.get('GCP_PROJECT', '-')
LOCATION = os.environ.get('GCP_REGION', '-')

if reset := st.button("Reset Demo State"):
    reset_st_state()

m = magika.Magika()
vertexai.init(project=PROJECT_ID, location=LOCATION)

MODEL_ID = "gemini-experimental" 

model = GenerativeModel(
    MODEL_ID,
    #system_instruction=[
    #    "You are a coding expert.",
    #    "Your mission is to answer all code related questions with given context and instructions.",
    #],
)

safety_settings = {
    generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_NONE,
    generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_NONE,
    generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_NONE,
    generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_NONE,
}


def sendPrompt(input):
    token_size = model.count_tokens(input)
    st.write(f"Input Token size: {token_size}")
    token_size = str(token_size)
    patternToken = r"total_tokens:\s*(\d+)"
    matchToken = re.search(patternToken, token_size)

    total_tokens = int(matchToken.group(1))
    if total_tokens > 1000000:
        raise ValueError("Total tokens must be less than 1000000")
    # st.write(f"Total Tokens: {total_tokens}")

    patternChar = r"total_billable_characters:\s*(\d+)"
    matchChar = re.search(patternChar, token_size)

    billable_characters = int(matchChar.group(1))
    valor = (billable_characters / 1000) * 0.0025
    st.write(f"Valor da chamada: US$ {round(valor,2)}")

    prompt_response = model.generate_content(input,
        generation_config={
            "max_output_tokens": 4096,
            "temperature": 0.4,
            "top_p": 1
        },
        safety_settings=safety_settings,
    )
    return prompt_response

def get_code_prompt(question, code_index, code_text):
    """Generates a prompt to a code related question."""

    prompt = f"""
    Questions: {question}

    Context:
    - The entire codebase is provided below.
    - Here is an index of all of the files in the codebase:
      \n\n{code_index}\n\n.
    - Then each of the files is concatenated together. You will find all of the code you need:
      \n\n{code_text}\n\n

    Answer:
  """

    return prompt


st.title('Gemini Repo Inspection')

repo_dir = "./repo"

def clone_repo(repo_url, repo_dir):
    """Clone a GitHub repository."""

    if os.path.exists(repo_dir):
        shutil.rmtree(repo_dir)
    os.makedirs(repo_dir)
    git.Repo.clone_from(repo_url, repo_dir)
    st.write(f"Repo {repo_url} foi clonado com sucesso!")
    return True


def extract_code(repo_dir):
    """Create an index, extract content of code/text files."""

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
    st.write(f"Código indexado com sucesso!")
    return code_index, code_text

repo_url = st.text_input("Cole um repositório para ser analisado:", """https://github.com/GoogleCloudPlatform/microservices-demo""")

if st.button("Clonar e Index repo"):
    with st.status("Downloading data...", expanded=True) as status:
        st.write("Cloning repo...")
        time.sleep(1)
        clone_repo(repo_url, repo_dir)
        st.write("Indexing data...")
        code_index, code_text = extract_code(repo_dir)
        time.sleep(1)
        st.session_state["index"] = code_index
        st.session_state["text"] = code_text
        status.update(label="Download complete!", state="complete", expanded=False)

 


question = st.selectbox('Selecione um prompt:', [
            'Give me a summary of this codebase, and tell me the top 3 things that I can learn from it.',
            'Provide a README explaining what this application do and how to properly use it',
            'Provide a getting started guide to onboard new developers to the codebase.',
            'Find the top 3 most severe issues in the codebase.',
            'Find the most severe bug in the codebase that you can provide a code fix for.',
            'Provide a troubleshooting guide to help resolve common issues.' 
            ])
        
if st.button('Generate'):
    with st.spinner("Processando resposta"):
        indice = st.session_state["index"]
        texto = st.session_state["text"]
        pergunta = get_code_prompt(question, indice, texto)
        resposta = sendPrompt(pergunta)
        st.write(resposta.text)
        st.write(resposta.to_dict().get("usage_metadata"))