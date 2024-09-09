import streamlit as st
from apps.firebase.config import load_vertex, load_models, video_uris
from apps.firebase.ui_components import render_custom_css, render_header, render_config_section, render_video_analysis_section
from apps.firebase.generation import generate_video_description, generate_robo_script

render_custom_css()
render_header()

# Configuration section
model_region, model_name, language, use_case = render_config_section()

# Load models and video
load_vertex(model_region)
text_model_pro, multimodal_model_pro = load_models(model_name)

selected_video_uri = video_uris[use_case]
video_url = "https://storage.googleapis.com/" + selected_video_uri.split("gs://")[1]

# Video and Results Section
render_video_analysis_section(video_url, use_case, language, selected_video_uri, multimodal_model_pro)