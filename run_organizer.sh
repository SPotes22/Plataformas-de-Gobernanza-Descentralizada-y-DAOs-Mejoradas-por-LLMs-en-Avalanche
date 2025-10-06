#!/bin/bash
# run_organizer.sh
# EJECUTOR DEL SCRIPT DE ORGANIZACIÓN

echo "🏗️  INICIANDO ORGANIZACIÓN DE ARCHIVOS..."

# Crear directorio scripts si no existe
mkdir -p scripts

# Ejecutar el organizador
source venv/bin/activate
python organize_chat_files.py

echo "✅ ORGANIZACIÓN COMPLETADA!"
echo "📁 Estructura creada:"
echo ""
tree -I '__pycache__|*.pyc' || find . -type f -not -path '*/\.*' | head -20
