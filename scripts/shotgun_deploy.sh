#!/bin/bash
# shotgun_deploy.sh
# DEPLOYMENT EN 1 COMANDO - ZERO ENTROPY

echo "🔫 INICIANDO ZERO-ENTROPY SHOTGUN..."
python zero_entropy_shotgun.py

curl -s http://localhost:8501/health | grep "status" || echo "DEPLOYMENT FALLIDO"

echo "✅ SHOTGUN DEPLOYMENT COMPLETADO"
echo "🎯 SIGUIENTE TAN: Implementar auto-scaling para picos de votación"