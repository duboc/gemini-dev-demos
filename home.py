import streamlit as st
import importlib.util
import os

# Override Streamlit's default page config
st.set_page_config(
    page_title="Generative AI Demos",
    page_icon="./images/logo.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Hide default Streamlit elements and remove extra top padding
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .reportview-container .main .block-container {padding-top: 0rem;}
        .sidebar .sidebar-content {
            background-image: linear-gradient(#2e7bcf,#2e7bcf);
            color: white;
        }
        .sidebar .sidebar-content [aria-selected="true"] {
            background-color: #0056b3;
            font-weight: bold; 
        }
    </style>
""", unsafe_allow_html=True)

st.title("Generative AI Developer Demos")
st.write("Select a demo category from the sidebar to get started.")

# Define the demo pages
demo_pages = {
    "🤖 Code Intelligence": [
        {"title": "Repo Inspection", "path": "apps/repo-inspection.py"},
        {"title": "Image to Code, Test and Deploy", "path": "apps/code-to-image.py"},
        {"title": "Cobol to Java", "path": "apps/cobol-to-java.py"},
    ],
    "🐛 Test Automation": [
        {"title": "Selenium Automation", "path": "apps/selenium-automation.py"},
        {"title": "Firebase Robo Script", "path": "apps/firebase-testlab.py"},
        {"title": "Appium Automation", "path": "apps/appium-automation.py"},
    ],
    "🎨 UX/UI Design": [
        {"title": "UX Heuristic Analysis using Gemini AI", "path": "apps/ux-heuristics-app.py"},
        {"title": "UX Friction Log Generator", "path": "apps/ux-frictionlog-app.py"},
        {"title": "Accessibility with Gemini", "path": "apps/ux-accessibility.py"},
    ],
    "📝 User Story Automation": [
        {"title": "User Story to Code", "path": "apps/generate-story-to-code-generic.py"},
        {"title": "User Story to Data", "path": "apps/generate-story-to-data-generic.py"},
        {"title": "User Story to API", "path": "apps/generate-story-to-api-generic.py"},
    ],
    "🌍 Others": [
        {"title": "Dataform Generation", "path": "apps/dataform-gen.py"},
    ],
}

# Initialize session state
if 'current_page' not in st.session_state:
    st.session_state.current_page = None
if 'selected_category' not in st.session_state:
    st.session_state.selected_category = list(demo_pages.keys())[0]

# Custom sidebar
st.sidebar.title("Demo Categories")

# Radio buttons for categories
selected_category = st.sidebar.radio(
    "Select a category:",
    options=list(demo_pages.keys()),
    key="selected_category"
)

st.sidebar.title("Demos")
for page in demo_pages[st.session_state.selected_category]:
    if st.sidebar.button(page["title"]):
        st.session_state.current_page = page["path"]
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.info("If you encounter a state error, click the 'Reset All' button below.")
if st.sidebar.button("Reset All"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# Load the selected demo page
if st.session_state.current_page:
    page_path = st.session_state.current_page
    page_name = os.path.splitext(os.path.basename(page_path))[0]
    
    spec = importlib.util.spec_from_file_location(page_name, page_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
else:
    st.write("Please select a demo from the sidebar to get started.")