import streamlit as st
import utils_streamlit

st.set_page_config(page_title="Generative AI Demos", page_icon="./images/logo.png")

cols = st.columns([12, 85])
with cols[0]:
    st.image("./images/logo.png")
with cols[1]:
    st.title("Generative AI Demos")

reset = st.button("Reset Demo State")

if reset:
    utils_streamlit.reset_st_state()

st.subheader("Demos")
st.write("Select a page from the left side menu to start one of the demos.")
st.write("Description of each demonstration:")
st.write(
    """**1.Github repo inspection**\n
**2. Code Retrieval Augmented Generation**
"""
)
