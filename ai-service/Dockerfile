FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

#  IMPORTANT: PyAV system deps
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    pkg-config \
    ffmpeg \
    libavcodec-dev \
    libavformat-dev \
    libavdevice-dev \
    libavutil-dev \
    libswscale-dev \
    libswresample-dev \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip

# Torch CPU
RUN pip install --no-cache-dir \
    torch==2.1.2 \
    torchvision==0.16.2 \
    --index-url https://download.pytorch.org/whl/cpu

# باقي الباكيدجات (فيهم av)
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

RUN mkdir -p /app/models

EXPOSE 5001

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5001"]