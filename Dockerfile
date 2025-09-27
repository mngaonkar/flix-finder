# Use Python 3.12 slim image as base
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs

# Expose the port that Streamlit runs on
EXPOSE 443

# Health check
HEALTHCHECK CMD curl --fail http://localhost:443/_stcore/health

# Command to run the application
CMD ["streamlit", "run", "main.py", "--server.port=443", "--server.address=0.0.0.0", "--ui.hideTopBar", "True", "--client.toolbarMode", "viewer", "--server.sslCertFile", "/etc/letsencrypt/live/movies.altbox.one/fullchain.pem", "--server.sslKeyFile", "/etc/letsencrypt/live/movies.altbox.one/privkey.pem"]