"""Shared Gemini access for every demo in this repository.

The demos reach Gemini through the `google-genai` SDK in Vertex AI mode. The
SDK reads `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`, and
`GOOGLE_GENAI_USE_VERTEXAI` on its own and authenticates with application
default credentials, so nothing here passes a project, a region, or a key.

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
def _client(location: str | None) -> genai.Client:
    if location:
        return genai.Client(location=location)
    return genai.Client()


def get_client(location: str | None = None) -> genai.Client:
    """Return a cached client, one per location.

    Pass `location` only where the reader picks a region in the interface.
    Everywhere else, leave it unset and let the SDK read
    `GOOGLE_CLOUD_LOCATION`.

    The cache sits behind this function rather than on it: `functools.cache`
    keys on the call signature, so caching `get_client` itself would give
    `get_client()` and `get_client(None)` separate entries and build the same
    client twice.
    """
    return _client(location or None)


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


def count_tokens(contents, model: str = MODEL_ID, location: str | None = None) -> int:
    """Return the token count Vertex AI reports for a prompt."""
    response = get_client(location).models.count_tokens(model=model, contents=contents)
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
    location: str | None = None,
    max_output_tokens: int = DEFAULT_MAX_OUTPUT_TOKENS,
):
    """Send one prompt to Gemini and return the text of the answer."""
    total_tokens = count_tokens(input, model=model, location=location)
    if total_tokens > MAX_INPUT_TOKENS:
        raise ValueError(
            f"The prompt holds {total_tokens} tokens, above the "
            f"{MAX_INPUT_TOKENS} this helper sends."
        )

    response = get_client(location).models.generate_content(
        model=model,
        contents=input,
        config=generation_config(max_output_tokens=max_output_tokens),
    )
    return response.text
