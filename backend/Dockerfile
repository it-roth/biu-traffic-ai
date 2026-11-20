# Production Dockerfile for Hugging Face Spaces & Render (Port 7860)
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
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . /app/

# Create necessary directories for media, staticfiles, and weights
RUN mkdir -p /app/staticfiles /app/media/uploads /app/media/annotated /app/media/crops /app/weights

# Ensure user 1000 (standard container user) owns the directory
RUN useradd -m -u 1000 user && \
    chown -R user:user /app

USER user

# Collect static files into STATIC_ROOT using WhiteNoise
RUN python manage.py collectstatic --noinput

# Expose production port 7860
EXPOSE 7860

# Run database migrations and start Gunicorn server with 120s timeout
CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:7860 --workers 2 --timeout 120"]
