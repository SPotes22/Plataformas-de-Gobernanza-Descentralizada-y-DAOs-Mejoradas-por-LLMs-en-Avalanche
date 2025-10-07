#!/bin/bash
# scripts/ci_cd_safe_copy.sh

echo "🔒 CI/CD Safe Copy - Entropy Control <3.14%"

# Verificar existencia del safe writer
if [ ! -f "secure_file_writer_cicd.py" ]; then
    echo "❌ Safe File Writer no encontrado"
    exit 1
fi

# Copiar archivos con verificación de entropía
for file in *.py; do
    if [ "$file" != "secure_file_writer_cicd.py" ]; then
        echo "📁 Procesando: $file"
        python3 -c "
from secure_file_writer_cicd import cicd_writer
result = cicd_writer.cicd_safe_write('$file', open('$file').read(), 'py')
print(f'  Entropy: {result.get(\"entropy\", \"N/A\")}% - Status: {result[\"status\"]}')
if result['status'] != 'success':
    exit(1)
"
    fi
done

echo "✅ CI/CD Safe Copy completado"
echo "📊 Vector Space actualizado: vector_space_6x128.json"