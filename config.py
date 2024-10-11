import os
import vertexai
from vertexai.generative_models import GenerativeModel, Part

def load_vertex(region):
    PROJECT_ID = os.environ.get("GCP_PROJECT")
    LOCATION = os.environ.get(f"{region}")
    vertexai.init(project=PROJECT_ID, location=LOCATION)

def load_models(name):
    text_model_pro = GenerativeModel(name)
    multimodal_model_pro = GenerativeModel(name)
    return text_model_pro, multimodal_model_pro

def get_gemini_pro_vision_response_stream(
    model, prompt_list, generation_config={}, stream: bool = True
):
    generation_config = {"temperature": 0.1, "max_output_tokens": 8192}
    return model.generate_content(
        prompt_list, generation_config=generation_config, stream=stream
    )

def read_prompt(file_path):
    with open(file_path, 'r') as file:
        return file.read()

video_uris = {
    "Bank of Anthos": "gs://convento-samples/boa-mobile.mp4",
    "Hipster Shop": "gs://convento-samples/hipster-mobile.mp4"
}

images_uris = { 
    "Bank of Anthos Login": "gs://convento-samples/boa-login.png",
    "Guardanapo": "gs://convento-samples/guardanapo.jpg"
}

PROJECT_ID = os.environ.get("GCP_PROJECT")
LOCATION = os.environ.get("GCP_REGION")
vertexai.init(project=PROJECT_ID, location=LOCATION)

model_gemini_pro_15 = GenerativeModel("gemini-1.5-pro-002")
model_gemini_flash = GenerativeModel("gemini-1.5-flash-002")
model_experimental = GenerativeModel("gemini-experimental")