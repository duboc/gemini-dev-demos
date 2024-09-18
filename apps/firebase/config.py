import os
import streamlit as st
import vertexai
from vertexai.generative_models import GenerativeModel

def load_vertex(region):
    PROJECT_ID = os.environ.get("GCP_PROJECT")
    LOCATION = os.environ.get(f"{region}")
    vertexai.init(project=PROJECT_ID, location=LOCATION)

@st.cache_resource
def load_models(name):
    text_model_pro = GenerativeModel(name)
    multimodal_model_pro = GenerativeModel(name)
    return text_model_pro, multimodal_model_pro

video_uris = {
    "Bank of Anthos": "gs://convento-samples/boa-mobile.mp4",
    "Hipster Shop": "gs://convento-samples/hipster-mobile.mp4"
}