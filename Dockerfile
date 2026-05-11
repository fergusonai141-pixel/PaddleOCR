# Use a lightweight Python base image
FROM python:3.10-slim

# Set environment variables to prevent Python from writing .pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies for OpenCV, PaddlePaddle, and other libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    libgomp1 \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

# Copy the entire project
COPY . .

# Install the root PaddleOCR package and its dependencies
RUN pip install --no-cache-dir -e .

# Install the MCP server with local CPU support
# This will install paddlepaddle (CPU) and other required dependencies
RUN pip install --no-cache-dir -e "./mcp_server[local-cpu]"

# Expose the port used by the MCP server in HTTP mode
EXPOSE 8000

# Default environment variables for the MCP server
ENV PADDLEOCR_MCP_PIPELINE=OCR
ENV PADDLEOCR_MCP_PPOCR_SOURCE=local
ENV PADDLEOCR_MCP_DEVICE=cpu
ENV PADDLEOCR_MCP_TIMEOUT=60

# Command to run the MCP server in HTTP mode
# Using '0.0.0.0' to allow external access within the Docker network
CMD ["python", "-m", "mcp_server.paddleocr_mcp", "--http", "--host", "0.0.0.0", "--port", "8000"]
