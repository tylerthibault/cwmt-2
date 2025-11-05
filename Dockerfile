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

# Install system deps needed for some wheels and curl for health checks
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p instance logs

# CapRover expects port 3000 by default
EXPOSE 3000

# Add a simple health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:3000/ || exit 1

# Start with more verbose logging and single worker for debugging
CMD ["gunicorn", "--bind", "0.0.0.0:3000", "--workers", "1", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "--log-level", "debug", "--capture-output", "run:app"]