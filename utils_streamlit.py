import streamlit as st


def reset_page_state(prefix: str):
    for key in st.session_state:
        if key.startswith(prefix):
            del st.session_state[key]


def reset_st_state():
    for key in st.session_state:
        del st.session_state[key]