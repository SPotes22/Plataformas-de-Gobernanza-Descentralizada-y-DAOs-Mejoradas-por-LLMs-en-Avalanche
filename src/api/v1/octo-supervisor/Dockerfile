# Dockerfile para Octo Supervisor Microservice
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Crear estructura de directorios
RUN mkdir -p /app/secrets/models/compressed \
    /app/logs \
    /app/admin/dashboard/actions

# Copiar código del microservicio
COPY octo-module-1.py .
COPY src/api/v1/octo-supervisor/ ./src/api/v1/octo-supervisor/

# Exponer puerto
EXPOSE 5003

# Variables de entorno
ENV KAFKA_BROKER=kafka:9092
ENV OCTO_GROUP=octo-supervisor
ENV CONFIDENCE_THRESHOLD=0.82
ENV PYTHONPATH=/app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5003/health || exit 1

# Comando de ejecución
CMD ["python", "src/api/v1/octo-supervisor/octo-module-1.py"]
