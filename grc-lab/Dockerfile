FROM python:3.11-slim

WORKDIR /app

# Dipendenze di sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Installazione ordinata per evitare conflitti di import
RUN pip install --no-cache-dir langchain
RUN pip install --no-cache-dir langchain-community langchain-ollama pypdf faiss-cpu fastapi uvicorn

COPY ./app /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]