from tree_sitter import Language
import vertexai
import os
import git
import shutil
import streamlit as st
from utils_streamlit import reset_st_state



PROJECT_ID = os.environ.get('GCP_PROJECT', '-')
LOCATION = os.environ.get('GCP_REGION', '-')

vertexai.init(project=PROJECT_ID, location=LOCATION)

if reset := st.button("Reset Demo State"):
    reset_st_state()

tree_sitter_parent_dir_name = "tmp"  # @param {type:"string"}
tree_sitter_parent_dir = os.path.join(os.getcwd(), tree_sitter_parent_dir_name)

repo_url = st.text_input("Cole um repositório para ser analisado:", """https://github.com/GoogleCloudPlatform/microservices-demo""")


repo_dir = "./repo"


def clone_repo(repo_url, repo_dir):
    """Clone a GitHub repository."""

    if os.path.exists(repo_dir):
        shutil.rmtree(repo_dir)
    os.makedirs(repo_dir)
    git.Repo.clone_from(repo_url, repo_dir)
    return True


