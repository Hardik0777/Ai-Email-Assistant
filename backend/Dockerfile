FROM python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

COPY requirements.txt .
# Python 3.12 has onnxruntime wheels, so ChromaDB installs here even when it can't locally.
RUN pip install --no-cache-dir -r requirements.txt chromadb

COPY app ./app

EXPOSE 8001
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
