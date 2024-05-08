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


def get_code_prompt(question):
    prompt = f"""
    Request: {question}

    User Story Format example:
        As a: [User Role or Persona]
        I want to: [Action or Goal]
        So that: [Benefit or Value]
        Additional Context: [Optional details about the scenario, environment, or specific requirements]
        Acceptance Criteria: [Specific, measurable conditions that must be met for the story to be considered complete]
    """

    return prompt


st.title('Gemini User Story Generator')

question = st.selectbox('Selecione um prompt:', [
            'Crie uma historia para login no ecomerce',
            'Provide a README explaining what this application do and how to properly use it',
            'Provide a getting started guide to onboard new developers to the codebase.',
            'Find the top 3 most severe issues in the codebase.',
            'Find the most severe bug in the codebase that you can provide a code fix for.',
            'Provide a troubleshooting guide to help resolve common issues.' 
            ])

repo_url = st.text_input("Breve descrição da User Story:", """...""")
        
if st.button('Generate'):
    with st.spinner("Processando resposta"):
        pergunta = get_code_prompt(question)
        resposta = sendPrompt(pergunta)
        st.write(resposta.text)
        st.write(resposta.to_dict().get("usage_metadata"))