FROM python:3.10-slim

WORKDIR /app

# Install only essential system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install torch CPU-only (smallest version)
RUN pip install --no-cache-dir torch==2.0.1 --index-url https://download.pytorch.org/whl/cpu

# Install other deps
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy only app code (not tests, uploads, etc.)
COPY ./app ./app

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
