FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies including FFmpeg
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libmariadb-dev \
    libgl1 \
    libglib2.0-0 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app /app/app

# Run Celery worker
CMD ["celery", "-A", "app.celery_app", "worker", "--loglevel=info"]