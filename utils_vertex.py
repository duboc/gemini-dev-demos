import os
import re

import vertexai
from vertexai.generative_models import (
    GenerationConfig,
    GenerativeModel,
    HarmBlockThreshold,
    HarmCategory,
    Part,
)
import vertexai.generative_models as generative_models
from vertexai.preview.vision_models import (
    ImageGenerationModel,
    MultiModalEmbeddingModel,
)
from vertexai.language_models import TextEmbeddingInput, TextEmbeddingModel



PROJECT_ID = os.environ.get("GCP_PROJECT")  # Your Google Cloud Project ID
LOCATION = os.environ.get("GCP_REGION")  # Your Google Cloud Project Region
vertexai.init(project=PROJECT_ID, location=LOCATION)



model_gemini_pro = GenerativeModel("gemini-1.0-pro")
model_gemini_pro_15 = GenerativeModel("gemini-1.5-pro-001")
model_gemini_flash = GenerativeModel("gemini-1.5-flash-001")
model_experimental = GenerativeModel("gemini-experimental")
multimodal_model_pro = GenerativeModel("gemini-1.0-pro-vision")
multimodal_embeddings = MultiModalEmbeddingModel.from_pretrained(
    "multimodalembedding@001"
)
embeddings = TextEmbeddingModel(model_id="textembedding-gecko-multilingual@latest")
imagen = ImageGenerationModel.from_pretrained("imagegeneration@005")

safety_settings = {
    generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_NONE,
    generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_NONE,
    generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_NONE,
    generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_NONE,
}






def sendPrompt(input, model):

    
    token_size = model.count_tokens(input)
    token_size = str(token_size)
    patternToken = r"total_tokens:\s*(\d+)"
    matchToken = re.search(patternToken, token_size)

    total_tokens = int(matchToken.group(1))
    if total_tokens > 1000000:
        raise ValueError("Total tokens must be less than 1000000")


    patternChar = r"total_billable_characters:\s*(\d+)"
    matchChar = re.search(patternChar, token_size)

    billable_characters = int(matchChar.group(1))
    valor = (billable_characters / 1000) * 0.0025

    prompt_response = model.generate_content(input,
        generation_config={
            "max_output_tokens": 8192,
            "temperature": 0.4,
            "top_p": 1
        },
        safety_settings=safety_settings,
    )
    return prompt_response.text


