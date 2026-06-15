# French Reader sidecar — OCR / TTS / AI / export API (:5002)
FROM python:3.12-slim-bookworm

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        tesseract-ocr \
        tesseract-ocr-fra \
        libgl1 \
        libglib2.0-0 \
        curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY extensions/french-reader-engine/pyproject.toml ./
COPY extensions/french-reader-engine/src ./src

RUN pip install --no-cache-dir hatchling \
    && pip install --no-cache-dir ".[bubble]"

ENV FRENCH_READER_ENABLED=true \
    FRENCH_READER_HOST=0.0.0.0 \
    FRENCH_READER_PORT=5002 \
    FRENCH_READER_CORS_ORIGINS=http://localhost:8080,http://127.0.0.1:8080

EXPOSE 5002

HEALTHCHECK --interval=15s --timeout=5s --start-period=20s --retries=5 \
    CMD curl -fsS http://127.0.0.1:5002/health || exit 1

CMD ["python", "-m", "uvicorn", "french_reader.main:app", "--host", "0.0.0.0", "--port", "5002"]
