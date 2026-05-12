FROM python:3.10-bookworm

# Setări globale de mediu pentru a preveni erorile de motor
ENV FLAGS_use_pir_api=0
ENV FLAGS_use_onednn=0
ENV OMP_NUM_THREADS=1
ENV MKL_NUM_THREADS=1
ENV PYTHONUNBUFFERED=1

# Instalare dependințe sistem
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

COPY main.py .

EXPOSE 8000

CMD ["python", "main.py"]
