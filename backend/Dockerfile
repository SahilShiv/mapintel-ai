# Multi-stage/Debian image with Google Chrome for Selenium headless scraping
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    CHROME_BIN=/usr/bin/google-chrome \
    CHROMEDRIVER_PATH=/usr/bin/chromedriver

WORKDIR /app

# Install system dependencies, Chromium, and ChromeDriver
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    curl \
    gnupg \
    unzip \
    ca-certificates \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install python packages
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy codebase
COPY . /app

# Expose FastAPI port
EXPOSE 8000

# Run migrations and start server
CMD ["sh", "-c", "python backend/app/migrate.py && python -m uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
