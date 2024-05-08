import vertexai
import os
import git
import shutil
import streamlit as st
from utils_streamlit import reset_st_state
import parse_repo




PROJECT_ID = os.environ.get('GCP_PROJECT', '-')
LOCATION = os.environ.get('GCP_REGION', '-')

vertexai.init(project=PROJECT_ID, location=LOCATION)

if reset := st.button("Reset Demo State"):
    reset_st_state()

st.title("Code Chat with RAG")


repo_url = st.text_input("Cole um repositório para ser analisado:", """https://help.rockcontent.com/pt-br""")


repo_dir = "./repo"

parse_repo.main(repo_url)
