import streamlit as st

from utils_vertex import MODEL_ID, sendPrompt

my_model = MODEL_ID

x = sendPrompt("textosobre", my_model)

st.write(x)
