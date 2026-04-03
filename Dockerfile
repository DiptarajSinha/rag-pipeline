# Stage 1: Build stage
FROM python:3.11-slim-bookworm as builder

WORKDIR /app

# Install build dependencies if needed (none currently for our lean requirements)
# but good for future-proofing
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies into a local directory
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Final runtime stage
FROM python:3.11-slim-bookworm

WORKDIR /app

# Copy installed dependencies from builder
COPY --from=builder /install /usr/local

# Copy application source code
COPY ./app ./app

# Create necessary directories for local storage with proper permissions
RUN mkdir -p /app/uploads /app/data /app/chroma_data && \
    chmod 777 /app/uploads /app/data /app/chroma_data

# Use a default port which can be overridden by environment variable
# Hugging Face Spaces default port is 7860
ENV PORT=7860
EXPOSE 7860

# Run using the uvicorn server, binding to the PORT environment variable
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
