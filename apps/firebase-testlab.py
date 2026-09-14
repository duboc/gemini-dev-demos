from apps.firebase.config import video_uris
from apps.firebase.ui_components import render_custom_css, render_header, render_config_section, render_video_analysis_section

render_custom_css()
render_header()

# Configuration section
model_name, language, use_case = render_config_section()

selected_video_uri = video_uris[use_case]
video_url = "https://storage.googleapis.com/" + selected_video_uri.split("gs://")[1]

# Video and Results Section
render_video_analysis_section(video_url, use_case, language, selected_video_uri, model_name)