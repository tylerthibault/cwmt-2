FROM python:3.11-slim
WORKDIR /app

EXPOSE 80

# Start a tiny server on port 80 that prints a startup message to stdout
CMD ["sh", "-c", "echo 'DEBUG SERVER: starting http.server on :80' >&2; echo 'OK' > /app/index.html; python -m http.server 80"]