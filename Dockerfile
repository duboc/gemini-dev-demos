FROM python:3.12

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables (replace with your values)
ENV GCP_PROJECT=conventodapenha
ENV GCP_REGION=us-central1
ENV STREAMLIT_SERVER_ENABLE_STATIC_SERVING=true
ENV DEMO_ASSETS_BUCKET=bucket-name

# Ensure the prompt directory exists and copy files if they exist
RUN mkdir -p /app/apps/firebase/prompts && \
    if [ -d "apps/firebase/prompts" ] && [ "$(ls -A apps/firebase/prompts)" ]; then \
    cp -r apps/firebase/prompts/*.md /app/apps/firebase/prompts/ || true; \
    fi

EXPOSE 8080

# Run Streamlit app
CMD ["streamlit", "run", "home.py", "--server.port=8080"]