FROM python:3.10-slim

WORKDIR /app

# Install torch separately with CPU wheel
RUN pip install --no-cache-dir torch==2.0.1 -f https://download.pytorch.org/whl/cpu

# Copy requirements and install rest
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy app source
COPY ./app ./app

EXPOSE 8000

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
