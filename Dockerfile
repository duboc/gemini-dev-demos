FROM python:3.12

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables (replace with your values)
ENV GCP_PROJECT=GCP_PROJECT=my-demo-project-400313
ENV GCP_REGION=us-central1
ENV STREAMLIT_SERVER_ENABLE_STATIC_SERVING=true
ENV DEMO_ASSETS_BUCKET=bucket-name

EXPOSE 8080

# Run Streamlit app
CMD ["streamlit", "run", "home.py", "--server.port=8080"]