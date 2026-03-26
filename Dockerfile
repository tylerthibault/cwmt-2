# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=run.py \
    FLASK_ENV=production

# Required security secrets — must be provided at runtime via environment.
# Do NOT bake these into the image.  Provide them through your container
# orchestration secrets manager (e.g. CapRover app env, Docker secrets):
#   FIELD_ENCRYPTION_KEY  — Fernet key for PII field encryption at rest
#   SEARCH_HASH_KEY       — HMAC key for blind-index search hashes
#   SECRET_KEY            — Flask session signing key

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p instance logs

# Expose port (CapRover will map this)
EXPOSE 80

# Run the application with Gunicorn
# CapRover expects the app to run on port 80
# Use preload to catch errors early and set config to production
CMD ["gunicorn", "--bind", "0.0.0.0:80", "--workers", "2", "--threads", "2", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "--log-level", "info", "--preload", "--env", "FLASK_ENV=production", "run:app"]
