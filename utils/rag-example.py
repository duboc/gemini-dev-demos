from vertexai.preview import rag
from vertexai.preview.generative_models import GenerativeModel, Tool
import vertexai
import os

# Create a RAG Corpus, Import Files, and Generate a response

# TODO(developer): Update and un-comment below lines
# project_id = "PROJECT_ID"
display_name = "bank_of_anthos_codebase"
paths = ["gs://convento-samples/codebase/bank-of-anthos-main"]  # Supports Google Cloud Storage and Google Drive Links


PROJECT_ID = os.environ.get("GCP_PROJECT")  # Your Google Cloud Project ID
LOCATION = os.environ.get("GCP_REGION")  # Your Google Cloud Project Region
vertexai.init(project=PROJECT_ID, location=LOCATION)

# Create RagCorpus
rag_corpus = rag.create_corpus(display_name=display_name)

# Import Files to the RagCorpus
response = rag.import_files(
    rag_corpus.name,
    paths,
    chunk_size=1000,  # Optional
    chunk_overlap=500,  # Optional
)

# Enhance generation
# Create a RAG retrieval tool
rag_retrieval_tool = Tool.from_retrieval(
    retrieval=rag.Retrieval(
        source=rag.VertexRagStore(
            rag_corpora=[rag_corpus.name],  # Currently only 1 corpus is allowed.
            similarity_top_k=3,  # Optional
        ),
    )
)
# Create a gemini-pro model instance
rag_model = GenerativeModel(
    model_name="gemini-1.5-flash-preview-0514", tools=[rag_retrieval_tool]
)

# Generate response
response = rag_model.generate_content("What does license file say?")
print(response.text)