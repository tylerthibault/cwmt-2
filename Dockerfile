# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Accept build arguments
ARG CAPROVER_GIT_COMMIT_SHA
ARG SETTINGS_ENCRYPTION_KEY

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=run.py \
    FLASK_ENV=production

# Set environment variable from build arg if provided
ENV SETTINGS_ENCRYPTION_KEY=${SETTINGS_ENCRYPTION_KEY}

# Install system deps needed for some wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p instance logs

# CapRover expects port 80 by default
EXPOSE 80

# Update Gunicorn to bind to port 80
CMD ["gunicorn", "--bind", "0.0.0.0:80", "--workers", "2", "--threads", "2", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "--log-level", "debug", "run:app"]