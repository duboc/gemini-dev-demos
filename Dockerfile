FROM python:3.9

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
EXPOSE 8080

# Run Streamlit app
CMD ["streamlit", "run", "gemini-repo.py", "--server.port=8080"]