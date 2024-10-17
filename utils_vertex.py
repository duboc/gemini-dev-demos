import os
import re
from typing import Union, List

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

# Import tenacity for retry logic
from tenacity import retry, stop_after_attempt, wait_exponential

PROJECT_ID = os.environ.get("GCP_PROJECT")  # Your Google Cloud Project ID
LOCATION = os.environ.get("GCP_REGION")  # Your Google Cloud Project Region
vertexai.init(project=PROJECT_ID, location=LOCATION)

# Initialize models
model_gemini_pro_15_001 = GenerativeModel("gemini-1.5-pro-001")
model_gemini_flash_001 = GenerativeModel("gemini-1.5-flash-001")
model_gemini_pro_15_002 = GenerativeModel("gemini-1.5-pro-002")
model_gemini_flash_002 = GenerativeModel("gemini-1.5-flash-002")
model_experimental = GenerativeModel("gemini-experimental")
multimodal_embeddings = MultiModalEmbeddingModel.from_pretrained("multimodalembedding@001")
embeddings = TextEmbeddingModel(model_id="textembedding-gecko-multilingual@latest")
imagen = ImageGenerationModel.from_pretrained("imagegeneration@005")

safety_settings = {
    generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_NONE,
    generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_NONE,
    generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_NONE,
    generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_NONE,
}

# Define a retry strategy using tenacity
retry_strategy = {
    'wait': wait_exponential(multiplier=1, min=2, max=10),
    'stop': stop_after_attempt(3)
}

@retry(**retry_strategy)
def sendPrompt(input: Union[str, List[Union[str, Part]]], model: GenerativeModel = None) -> str:
    models = [
        model_gemini_pro_15_002,
        model_gemini_flash_002,
        model_gemini_pro_15_001
    ]
    
    if model:
        models.insert(0, model)
    
    for attempt, fallback_model in enumerate(models):
        try:
            prompt_response = fallback_model.generate_content(
                input,
                generation_config=GenerationConfig(
                    max_output_tokens=8192,
                    temperature=0.4,
                    top_p=1
                ),
                safety_settings=safety_settings,
            )
            return prompt_response.text
        except Exception as e:
            print(f"Error with model {fallback_model._model_name}: {str(e)}")
            if attempt == len(models) - 1:
                raise Exception(f"All models failed. Last error: {str(e)}") from e

def count_tokens(input: str, model: GenerativeModel) -> int:
    token_size = model.count_tokens(input)
    token_size = str(token_size)
    patternToken = r"total_tokens:\s*(\d+)"
    matchToken = re.search(patternToken, token_size)

    if matchToken:
        total_tokens = int(matchToken.group(1))
        if total_tokens > 1000000:
            raise ValueError("Total tokens must be less than 1000000")
        return total_tokens
    else:
        raise ValueError("Unable to parse token count")

def calculate_cost(input: str, model: GenerativeModel) -> float:
    token_size = model.count_tokens(input)
    token_size = str(token_size)
    patternChar = r"total_billable_characters:\s*(\d+)"
    matchChar = re.search(patternChar, token_size)

    if matchChar:
        billable_characters = int(matchChar.group(1))
        return (billable_characters / 1000) * 0.0025
    else:
        raise ValueError("Unable to parse billable characters")





