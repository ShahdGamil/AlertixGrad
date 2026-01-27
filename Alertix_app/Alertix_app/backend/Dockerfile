# Dockerfile for Alertix YOLO Theft Detection API
# =================================================
# This Dockerfile creates a containerized version of the API
# for easy deployment across different platforms.
#
# Build:
#   docker build -t alertix-api .
#
# Run:
#   docker run -p 8000:8000 -v $(pwd):/app alertix-api
#
# =================================================

FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libopencv-dev \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend.py .
COPY config.py .

# Copy model file (if available)
# COPY Final_Copy_of_YOLO_Ensemble_Colab_Full_(3)_final.pt .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run the application
CMD ["uvicorn", "backend:app", "--host", "0.0.0.0", "--port", "8000"]
