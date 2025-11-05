# Use a multi-stage build to avoid keeping build tools (gcc) in the final image
FROM python:3.11-slim AS builder
ARG CAPROVER_GIT_COMMIT_SHA

WORKDIR /wheels
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install minimal build deps (removed in final stage)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and build wheels
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

###
### Final runtime image (no gcc/build deps kept)
###
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=run.py \
    FLASK_DEBUG=0 \
    APP_PORT=8080

# Create a non-root user for better security
RUN addgroup --system app && adduser --system --ingroup app app

# Copy pre-built wheels from builder and install ONLY wheel files
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/*.whl \
    && rm -rf /wheels

# Copy application files and set ownership to non-root user
COPY --chown=app:app . .

# Create runtime dirs and ensure ownership
RUN mkdir -p instance logs \
    && chown -R app:app /app /app/instance /app/logs

USER app

# Use the high port internally so binding works without root
EXPOSE 8080

# Healthcheck updated to use APP_PORT
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD wget -qO- http://127.0.0.1:${APP_PORT}/health || exit 1

# Bind Gunicorn to the APP_PORT
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--threads", "2", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "--log-level", "info", "run:app"]