from langchain_google_vertexai import VertexAIEmbeddings, VertexAI

embeddings = VertexAIEmbeddings(model_name="textembedding-gecko-multilingual@latest")
llm = VertexAI(model_name="gemini-experimental")