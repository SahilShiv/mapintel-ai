FROM python:3.11-slim

# Install system dependencies including Chrome & Chromedriver dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    gnupg \
    unzip \
    curl \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements & install
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r ./backend/requirements.txt

# Copy application source code
COPY backend ./backend

ENV PYTHONUNBUFFERED=1
ENV PORT=8000
EXPOSE 8000

# Seed database and start uvicorn
CMD python -m backend.app.seed_demo && uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT}
