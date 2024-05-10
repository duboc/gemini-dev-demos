from utils_vertex import model_gemini_pro, sendPrompt
import streamlit as st

my_model = model_gemini_pro

x = sendPrompt("textosobre", my_model)

st.write(x)


