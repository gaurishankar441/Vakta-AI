FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# minimal system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# --- deps install (no editable install, no package named 'app' to site-packages) ---
COPY app/requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip && pip install -r /tmp/requirements.txt

# --- copy source last to avoid caching issues ---
COPY app /app/app

EXPOSE 8000

CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000","--proxy-headers"]
