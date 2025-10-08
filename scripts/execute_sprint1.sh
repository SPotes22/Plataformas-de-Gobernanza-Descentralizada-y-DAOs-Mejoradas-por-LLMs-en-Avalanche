#!/bin/bash
# execute_sprint1.sh
# EJECUTOR SPRINT DÍA 1 - DAO FOUNDATION

echo "🏁 INICIANDO SPRINT DÍA 1: DAO Governance Foundation"

python sprint1_dao_foundation.py

echo "🧪 EJECUTANDO TEST SUITE..."
forge test
forge coverage

forge test --gas-report
forge snapshot

echo "✅ SPRINT DÍA 1 COMPLETADO"
echo "📊 Reportes generados: sprint1_report.json, SPRINT1_SUMMARY.md"
echo "🎯 NEXT: Sistema de votación ponderada con quórum"