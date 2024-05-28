# Gemini-Dev-Demos

This application showcases the capabilities of Google's Gemini AI models in various software development tasks. Built using Streamlit, it offers interactive demos that highlight Gemini's potential for code analysis, test plan generation, user story creation, and code snippet generation, leveraging advanced techniques like Retrieval Augmented Generation (RAG) and multimodal processing.

Live demo:
https://genai-re-demos-nhgqlpa4za-uc.a.run.app


## Demo Highlights

- **Gemini Repo Inspection:** Analyze a GitHub repository, ask code-related questions, and get comprehensive answers based on the repository's code.
- **Code Chat with RAG:** Engage in a conversational chat interface to explore a codebase and get insights into its functionality.
- **Github Issues Chat with RAG:**  Ask questions about issues in a GitHub repository and get answers based on the issue content.
- **Gemini User Story Generator:** Generate detailed User Stories based on your prompts or descriptions.
- **Gemini Repo to Multimodal Tasks:** Generate a user story, break it down into tasks, and create Python code snippets for implementation. 
- **Sprint Planning from Image:** Generate a sprint plan, including backend and frontend tasks and a Terraform deployment script, from an application screenshot.
- **Gemini Selenium Task from Video:** Analyze a video of web browser interactions and generate a Selenium script to automate the task. 
- **Test Plan from Image:** Create a comprehensive test plan, including test cases and Selenium scripts, from an application screenshot.
- **Gemini User Story to Code:** Move from User Story to a code implementation plan, including suggested Google Cloud services and Terraform code. 

## How to Use

### Prerequisites:

1. **Google Cloud Project:** You'll need a Google Cloud Project with billing enabled.
2. **Vertex AI API Enabled:** Enable the Vertex AI API in your project.
3. **Service Account:** Create a Service Account with the necessary permissions for Vertex AI and (if needed) other Google Cloud services used in the demos (e.g., Secret Manager). 
4. **Environment Variables:**  Set the following environment variables:
    * `GCP_PROJECT`: Your Google Cloud Project ID
    * `GCP_REGION`: Your preferred Google Cloud Region (e.g., 'us-central1')

### Installation:

1. **Clone the repository:**  `git clone https://github.com/GoogleCloudPlatform/gemini-dev-demos.git`
2. **Navigate to the directory:** `cd gemini-dev-demos`
3. **Install dependencies:** `pip install -r requirements.txt`

### Running the app:

1. **Start the Streamlit app:**  `streamlit run home.py`
2. **Access the demos:** Select the desired demo from the sidebar menu.
3. **Interact with the demos:** Follow the instructions on each demo page to provide input and generate results.

## Notes:

- Ensure your Service Account has the necessary roles/permissions to access the APIs used in the demos (e.g., Gemini, Text Embedding, etc.). 
- Some demos may require additional setup (e.g., creating a GitHub personal access token for accessing repositories).  The demo page will provide instructions for such cases.
- Use the "Reset Demo State" button on the home page or individual demo pages to clear the session state and start fresh. 
