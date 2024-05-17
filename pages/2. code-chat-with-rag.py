import vertexai
import os
import git
import shutil
import streamlit as st
from utils_streamlit import reset_st_state
import utils_files
import time
from langchain_google_vertexai import VertexAIEmbeddings, VertexAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from utils_gcp import access_secret_version

if reset := st.button("Reset Demo State"):
    reset_st_state()

embeddings = VertexAIEmbeddings(model_name="textembedding-gecko-multilingual@latest")
llm = VertexAI(model_name="gemini-experimental")

st.header("Code Chat with RAG", divider="rainbow")

st.info(
        "💡 **Observação:** Se o repositório for grande, a indexação pode levar um tempo. \n"
        "Isso é normal, pois estamos analisando e organizando todo o código para facilitar a busca e resposta às suas perguntas. 😊"
    )

st.subheader("Preparar dados", divider="blue")
repo_url = st.text_input("Cole um repositório para ser analisado:", """https://github.com/GoogleCloudPlatform/microservices-demo""")

repo_dir = "./repo"

if st.button("Clonar e Index repo"):
    with st.status("Downloading data...", expanded=True) as status:
        st.write("Cloning repo...")
        time.sleep(1)
        utils_files.main(repo_url)
        st.write("Indexing data...")
        time.sleep(1)
        status.update(label="Download complete!", state="complete", expanded=False)

def get_chain(input):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000,
                                                chunk_overlap=500,
                                                length_function=len)
    text = text_splitter.split_text(input)
    vector = FAISS.from_texts(text, embeddings)
    chain = RetrievalQA.from_chain_type(llm, chain_type="stuff",
                                     retriever=vector.as_retriever())

    return chain

st.subheader("Start conversation", divider="green")


if st.button("Iniciar bot"):
    with st.status("Carregando issues...", expanded=True) as status:
        st.write("Preparando bot...")
        time.sleep(1)
        with open('files/compressed_output.txt', 'r') as f:
            user_code = f.read()
        chain = get_chain(user_code)
        st.success("Ready to chat!")
        st.session_state.chain = chain

st.subheader("Chat")
st.divider()

template = """
Initial context: Always think step by step.
The conversation interface is a chat tool acting a knowledge base for a repository codebase. Be concise and polite. 
Your mission is to answer all code related questions with given context and instructions.
The entire codebase is embeded and if you need more context, ask a question back"""




# Initialize chat history
if "codebase" not in st.session_state:
    st.session_state.codebase = []

# Display chat messages from history on app rerun
for message in st.session_state.codebase:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# React to user input
if prompt := st.chat_input("Ask a question..."):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.codebase.append({"role": "user", "content": prompt})
    chain = st.session_state.chain 
    response = chain.run({"query": template + prompt})
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)
    # Add assistant response to chat history
    st.session_state.codebase.append({"role": "assistant", "content": response})