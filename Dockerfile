# Production Dockerfile for Hugging Face Spaces (Port 7860)
FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=7860

WORKDIR /app

# Install system dependencies required for OpenCV, PyTorch and PostgreSQL
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy backend application source code
COPY backend/ /app/

# Create necessary directories for media, staticfiles, and weights
RUN mkdir -p /app/staticfiles /app/media/uploads /app/media/annotated /app/media/crops /app/weights

# Ensure user 1000 (standard Hugging Face Spaces user) owns the directory
RUN useradd -m -u 1000 user && \
    chown -R user:user /app

USER user

# Collect static files into STATIC_ROOT using WhiteNoise
RUN python manage.py collectstatic --noinput

# Expose Hugging Face Spaces standard port 7860
EXPOSE 7860

# Start Gunicorn server bound to 0.0.0.0:7860 with 120s timeout for AI inference
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:7860", "--workers", "2", "--timeout", "120"]
