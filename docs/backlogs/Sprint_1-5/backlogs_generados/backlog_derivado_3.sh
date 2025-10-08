#!/bin/bash
# Backlog Dynamic Reader: BL_02_2
# ⚡ MODO DINÁMICO - Lee backlog.json actual

BACKLOG_FILE="$(dirname "$0")/../backlog.json"

echo "🚀 BACKLOG DINÁMICO - LIVE"
echo "=========================================="

if [ ! -f "$BACKLOG_FILE" ]; then
    echo "❌ Error: Backlog no encontrado"
    exit 1
fi

# Buscar la entrada específica
echo "📝 Backlog: BL_02_2"
echo "📊 Contenido:"
grep -A 10 -B 2 "BL_02_2" "$BACKLOG_FILE" | grep -E "(contenido|id|timestamp)" | head -10
echo "=========================================="
echo "💡 Modifica backlog.json y vuelve a ejecutar!"
