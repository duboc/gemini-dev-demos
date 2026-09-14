"""Shared Gemini access for every demo in this repository.

The demos reach Gemini through the `google-genai` SDK in Vertex AI mode. The
SDK reads `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`, and
`GOOGLE_GENAI_USE_VERTEXAI` on its own and authenticates with application
default credentials, so nothing here passes a project, a region, or a key.

Every call lands on the Vertex AI `global` endpoint, and no demo offers the
reader a region to pick. A run against a live project on September 14, 2026
sent one `generate_content` call per model and per location: `gemini-3.8-flash`
answered on `global` and returned 404 NOT_FOUND on `us-central1`, `us-east5`,
`southamerica-east1`, `us-east1`, `us-south1`, and `europe-southwest1`. Every
other 3.x flash identifier behaved the same way. Only the previous model
generation answered on a regional endpoint, and this repository pins none of
those, so a region is not a setting a reader can usefully change.

`GOOGLE_CLOUD_LOCATION` still carries the endpoint, and `Dockerfile`,
`cloudbuild.yaml`, and the README all set it to `global`. The same run
confirmed that the SDK falls back to `global` when the variable is unset, so a
reader who forgets the export reaches the endpoint that works rather than a
region that 404s.

`get_client()` builds the client on first use rather than at import time. A
client built at import turns a missing environment variable into an
ImportError, which takes down every page of the Streamlit shell instead of the
one call that needs credentials.
"""

import functools

from google import genai
from google.genai import types

# The single Gemini model the demos call. Google lists gemini-3.8-flash under
# "Models available for shorter availability periods", where a model retires 45
# days after its replacement ships, so re-read the lifecycle page before you
# depend on this identifier:
# https://cloud.google.com/vertex-ai/generative-ai/docs/learn/model-versioning
MODEL_ID = "gemini-3.8-flash"

# The embedding model that replaces the retired textembedding-gecko family.
EMBEDDING_MODEL_ID = "gemini-embedding-001"

# The five demos that used to offer a region picker show this line where the
# picker stood. It lives here, not in each demo, so the five cannot drift.
LOCATION_NOTE = (
    "Vertex AI serves Gemini 3.x models only on the global endpoint, so this "
    "demo no longer offers a region picker. Set GOOGLE_CLOUD_LOCATION to move "
    "the endpoint."
)

# Refuse a prompt this script cannot afford to send. count_tokens() answers
# before the request goes out, so an oversized prompt costs one cheap call
# instead of one rejected generation.
MAX_INPUT_TOKENS = 1_000_000

DEFAULT_MAX_OUTPUT_TOKENS = 8192
DEFAULT_TEMPERATURE = 0.4
DEFAULT_TOP_P = 1.0

# google-genai takes safety settings as a list of SafetySetting objects, not as
# the category-to-threshold mapping the retired vertexai SDK accepted.
SAFETY_SETTINGS = [
    types.SafetySetting(
        category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        threshold=types.HarmBlockThreshold.BLOCK_NONE,
    ),
    types.SafetySetting(
        category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        threshold=types.HarmBlockThreshold.BLOCK_NONE,
    ),
    types.SafetySetting(
        category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        threshold=types.HarmBlockThreshold.BLOCK_NONE,
    ),
    types.SafetySetting(
        category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
        threshold=types.HarmBlockThreshold.BLOCK_NONE,
    ),
]


@functools.cache
def get_client() -> genai.Client:
    """Return the one shared client, built on the first call.

    The client takes no location. The SDK reads `GOOGLE_CLOUD_LOCATION`, and
    the endpoint that serves this repository's model is `global` either way:
    the deployment files set the variable to `global`, and the SDK defaults to
    `global` when nothing sets it.
    """
    return genai.Client()


def generation_config(
    temperature: float = DEFAULT_TEMPERATURE,
    top_p: float = DEFAULT_TOP_P,
    max_output_tokens: int = DEFAULT_MAX_OUTPUT_TOKENS,
    system_instruction: str | None = None,
) -> types.GenerateContentConfig:
    """Build a request config that carries the shared safety settings."""
    return types.GenerateContentConfig(
        temperature=temperature,
        top_p=top_p,
        max_output_tokens=max_output_tokens,
        safety_settings=SAFETY_SETTINGS,
        system_instruction=system_instruction,
    )


def count_tokens(contents, model: str = MODEL_ID) -> int:
    """Return the token count Vertex AI reports for a prompt."""
    response = get_client().models.count_tokens(model=model, contents=contents)
    return response.total_tokens or 0


def usage_tokens(response) -> dict[str, int]:
    """Return the token counts a finished response reports.

    The retired SDK exposed `total_billable_characters`, and the demos turned
    that number into a dollar figure with a per-character price. google-genai
    reports neither, so the demos report what the API does state: the tokens
    the call actually consumed. For the price of those tokens, read
    https://cloud.google.com/vertex-ai/generative-ai/pricing
    """
    usage = getattr(response, "usage_metadata", None)
    if usage is None:
        return {"prompt": 0, "candidates": 0, "total": 0}
    return {
        "prompt": usage.prompt_token_count or 0,
        "candidates": usage.candidates_token_count or 0,
        "total": usage.total_token_count or 0,
    }


def sendPrompt(  # the name every demo already calls
    input,
    model: str = MODEL_ID,
    max_output_tokens: int = DEFAULT_MAX_OUTPUT_TOKENS,
):
    """Send one prompt to Gemini and return the text of the answer."""
    total_tokens = count_tokens(input, model=model)
    if total_tokens > MAX_INPUT_TOKENS:
        raise ValueError(
            f"The prompt holds {total_tokens} tokens, above the "
            f"{MAX_INPUT_TOKENS} this helper sends."
        )

    response = get_client().models.generate_content(
        model=model,
        contents=input,
        config=generation_config(max_output_tokens=max_output_tokens),
    )
    return response.text
