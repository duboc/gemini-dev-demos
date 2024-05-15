import streamlit as st
import utils_streamlit

st.set_page_config(page_title="Generative AI Demos", page_icon="./images/logo.png")

# Use st.columns for better layout and visual appeal
col1, col2 = st.columns([1, 3])  

with col1:
    st.image("./images/logo.png", width=100) 

with col2:
    st.title("Generative AI Developer Demos")

st.divider()

reset = st.button("Reset Demo State")
if reset:
    utils_streamlit.reset_st_state()

# Introduction to the demos
st.write("""
Welcome to the Generative AI Demos! This app showcases the capabilities of Google's Gemini family of models in various software development tasks.

Select a demo from the left sidebar menu to get started. 
""")

st.subheader("Demo Descriptions:")

# Use markdown for better formatting and readability
st.markdown("""
**1. Gemini Repo Inspection:**

*   Analyzes a given GitHub repository using the Gemini Pro Experimental model.
*   Clones the repository, indexes the code, and allows you to ask questions related to the codebase.
*   The whole codebase is then inserted into the context to provide comprehensive answers based on the repository's code. 

**2. Code Chat with RAG:**

*   Provides a conversational chat interface powered by Gemini Pro Experimental and RAG to interact with a GitHub repository.
*   Answers code-related questions, provides insights into the repository's functionality, and requests more context if needed.

**3. Github Issues Chat with RAG:**

*   Focuses on understanding and answering questions related to GitHub issues.
*   Uses the `GitHubIssuesLoader` to retrieve issues and leverages Gemini Pro Experimental and RAG to answer your queries.

**4. Gemini User Story Generator:**

*   Generates User Stories based on your input using the Gemini Pro Experimental model.
*   Choose from predefined prompts or provide your own brief description for a customized user story.

**5. Gemini Repo to Multimodal Tasks:**

*   Showcases the power of Gemini Pro 1.5, 1.5 Flash, and Experimental models in generating a user story, breaking it down into tasks, and creating Python code snippets.
*   Select the model you want to use with a radio button.

**6. Sprint Planning from Image:**

*   Combines Gemini Pro Experimental and Gemini Pro Vision to generate a sprint plan from an application interface screenshot.
*   Generates a detailed description, breaks it down into backend and frontend tasks, and even creates a Terraform script for deployment on Google Cloud.

**7. Gemini Selenium Task from Video:**

*   Automates tasks based on video input using Gemini Pro Vision.
*   Analyzes user interactions in a web browser video, generates a timestamped list of actions, and creates a Selenium script to automate the showcased task.

**8. Gemini User Story to Code:**

*   Provides a comprehensive approach to moving from User Story to code using Gemini Pro Vision.
*   Analyzes the user story, identifies backend and frontend tasks, suggests suitable Google Cloud services, and generates Terraform code for deployment.
            
**9. Test Plan from Image:**

*   Leverages Gemini Pro Experimental and Gemini Pro Vision to create test plans based on an application screenshot.
*   Generates a description, test plan, test scripts, and even Selenium scripts for automated testing.

""")