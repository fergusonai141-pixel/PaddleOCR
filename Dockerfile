FROM python:3.10-bookworm

# Instalare dependințe sistem pentru OpenCV și Paddle
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiere dependințe
COPY requirements.txt .
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# Copiere cod
COPY main.py .

# Portul API
EXPOSE 8000

# Pornire server
CMD ["python", "main.py"]
