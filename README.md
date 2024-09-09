# Generative AI = Developer Lifecyle Demos ✨

<center>
<img src="images/gemini_gif.gif" alt="Gemini Gif" width="250" height="250">
</center>

This repository showcases a suite of interactive demos leveraging Google's Gemini AI models to revolutionize software development workflows. Built with Streamlit, these demos cover various aspects of the development lifecycle, providing practical examples of AI-assisted software engineering.

## 🚀 Features

- **Code Intelligence**: Repo inspection, image-to-code generation, and legacy code migration.
- **Test Automation**: Selenium, Firebase Robo Script, and Appium automation.
- **UX/UI Design**: Heuristic analysis, friction log generation, and accessibility testing.
- **User Story Automation**: Generating code, data models, and APIs from user stories.
- **DataOps**: Dataform ELT generation.

## 🛠 Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/generative-ai-demos.git
   cd generative-ai-demos
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Google Cloud Project:**
   - Create or select a project in the [Google Cloud Console](https://console.cloud.google.com/).
   - Enable required APIs: Vertex AI, Cloud Run, Cloud Build, Artifact Registry, IAM, and Cloud Storage.
   - Create a service account with necessary permissions and download the JSON key file.

4. **Configure environment variables:**
   ```bash
   export GCP_PROJECT="your-project-id"
   export GCP_REGION="your-preferred-region"
   export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/service-account-key.json"
   ```

## 🚀 Running the Demos

To run the demos locally:

```bash
streamlit run home.py
```

This will start the Streamlit server and open the home page in your default web browser. Navigate through the sidebar to explore different demo categories and individual demos.

## 🐳 Docker Support

A Dockerfile is provided for containerizing the application. To build and run the Docker container:

1. Build the Docker image:
   ```bash
   docker build -t generative-ai-demos .
   ```

2. Run the container:
   ```bash
   docker run -p 8080:8080 -e GCP_PROJECT=your-project-id -e GCP_REGION=your-region generative-ai-demos
   ```

Access the application at `http://localhost:8080` in your web browser.

## ☁️ Deployment with Cloud Build

This project includes a `cloudbuild.yaml` file for automated builds and deployments using Google Cloud Build. Here's how to use it:

1. **Set up Artifact Registry:**
   Create a Docker repository in Artifact Registry:
   ```bash
   gcloud artifacts repositories create dev-lifecycle --repository-format=docker --location=us-central1 --description="Gemini Developer Lifecycle Demo"
   ```

2. **Trigger a build:**
   Submit a build to Cloud Build:
   ```bash
   gcloud builds submit . --config=./cloudbuild.yaml --substitutions SHORT_SHA=1.0
   ```

3. **Customizing the build:**
   The `cloudbuild.yaml` file defines the following steps:
   - Install Python dependencies
   - Build a Docker image
   - Push the image to Artifact Registry
   - Deploy the image to Cloud Run

   You can customize the build by modifying the `cloudbuild.yaml` file. Key substitution variables include:
   - `_ARTIFACT_REGISTRY_REPO`: Name of your Artifact Registry repository
   - `_REPO_LOCATION`: Location of your Artifact Registry
   - `_SERVICE_NAME`: Name of your Cloud Run service
   - `_SERVICE_REGION`: Region for your Cloud Run service

4. **Environment Variables:**
   The Cloud Run deployment step sets the following environment variables:
   - `GCP_PROJECT`: Set to your project ID
   - `GCP_REGION`: Set to the specified service region

Ensure you have the necessary permissions in your Google Cloud project to use Cloud Build, Artifact Registry, and Cloud Run.

## 🔧 Troubleshooting

- **API Errors**: Ensure your Google Cloud Project has the necessary APIs enabled and your service account has appropriate permissions.
- **Model Unavailable**: Check if the selected Gemini model is available in your region. Some models may have limited availability.
- **Memory Issues**: If encountering out-of-memory errors, try running the demos on a machine with more RAM or reduce the input size for large repositories or videos.
- **Docker Issues**: Make sure Docker is installed and running on your system. Check Docker logs for any error messages.
- **Cloud Build Issues**: Verify that you have the correct permissions and that all required APIs are enabled in your Google Cloud project.

## 🤝 Contributing

We welcome contributions to improve and expand these demos! Please refer to our [Contribution Guidelines](docs/CONTRIBUTING.md) for detailed information on how to contribute to this project.

## 🔒 Security

This project uses Google Cloud services. Ensure that you follow best practices for securing your Google Cloud environment:

- Use the principle of least privilege when setting up service accounts.
- Regularly rotate service account keys.
- Keep your `GOOGLE_APPLICATION_CREDENTIALS` secure and never commit them to version control.

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgements

- Google Cloud Platform and the Gemini AI team for their cutting-edge AI models
- Streamlit for their excellent framework for building interactive data applications
- The open-source community for various libraries and tools used in this project

---

For questions, issues, or feature requests, please open an issue in the GitHub repository or contact the maintainers.