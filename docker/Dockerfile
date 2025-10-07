#FROM python:3.11-slim
# WORKDIR /app
# COPY requirements.txt .
# mantained
#RUN pip install --no-cache-dir -r requirements.txt
#COPY . .
# EXPOSE 8000 # <- backend bone
#CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
# Base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy scripts
COPY ../scripts/ ./scripts/

# Create logs and backup directories
RUN mkdir -p /app/arachne_backups /app/logs

# Expose ports if needed
EXPOSE 9650 9651 8000  5001 5000 5050 5051
# <- testnets

# Default command
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
# files > test 
CMD ["python", "scripts/safe_writer_v3.py"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

