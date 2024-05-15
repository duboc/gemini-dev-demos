import streamlit as st
import os
from langchain_community.document_loaders import GitHubIssuesLoader
from utils_streamlit import reset_st_state
import time
from vertexai.generative_models import GenerativeModel, Part, FinishReason, ChatSession
from langchain_google_vertexai import VertexAIEmbeddings, VertexAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from utils_gcp import access_secret_version


if reset := st.button("Reset Demo State"):
    reset_st_state()

embeddings = VertexAIEmbeddings(model_name="textembedding-gecko-multilingual@latest")
llm = VertexAI(model_name="gemini-experimental")

gtoken = access_secret_version("GITHUB_TOKEN")
ACCESS_TOKEN = os.environ.get(f'GITHUB_TOKEN', gtoken)

st.title("Github Issues Chat with RAG")
st.subheader("Github Setup")
repo = st.text_input("Digite um repositório do gitub no formato repo/name. Repo: ", "GoogleCloudPlatform/microservices-demo")


def load_issues(repoName):
    loader = GitHubIssuesLoader(
        repo="GoogleCloudPlatform/microservices-demo",
        access_token=ACCESS_TOKEN, 
        include_prs=False,
    )

    docs = loader.load()

    return docs

def parse_string(issue_list):
    output = []
    for issue in issue_list:
        output.append(issue.page_content)
    
    return "\n".join(output)

def get_chain(input):
 text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000,
                                                chunk_overlap=500,
                                                length_function=len)
 text = text_splitter.split_text(input)
 vector = FAISS.from_texts(text, embeddings)
 chain = RetrievalQA.from_chain_type(llm, chain_type="stuff",
                                     retriever=vector.as_retriever())



 return chain


if st.button("Iniciar bot"):
    with st.status("Carregando issues...", expanded=True) as status:
        st.write("Preparando bot...")
        time.sleep(1)
        listaIssues = load_issues(repo)
        chain = get_chain(parse_string(listaIssues))
        st.success("Ready to chat!")
        st.session_state.chain = chain



st.divider()
st.subheader("Chat")


template = """
Answer: Let's think step by step.
The conversation interface is a chat tool. Be concise and polite. 
Always reply in table and always add the issue name as the index"""



# Initialize chat history
if "github_issues" not in st.session_state:
    st.session_state.github_issues = []

# Display chat messages from history on app rerun
for message in st.session_state.github_issues:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# React to user input
if prompt := st.chat_input("Ask a question..."):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.github_issues.append({"role": "user", "content": prompt})
    chain = st.session_state.chain 
    response = chain.run({"query": template + prompt})
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)
    # Add assistant response to chat history
    st.session_state.github_issues.append({"role": "assistant", "content": response})