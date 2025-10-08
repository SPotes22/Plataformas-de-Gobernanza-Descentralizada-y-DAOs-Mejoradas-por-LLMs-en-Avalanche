# Dockerfile para auth service
FROM python:3.11-slim

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el código de auth al contenedor
COPY . .

# Exponer puerto (por defecto Flask)
EXPOSE 5001

# Comando de inicio
CMD ["python", "app.py"]

