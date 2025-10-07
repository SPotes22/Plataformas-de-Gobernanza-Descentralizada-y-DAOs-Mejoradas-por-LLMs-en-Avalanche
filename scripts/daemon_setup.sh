#!/bin/bash
# Daemon Setup - Entropía controlada

# Configuración
DAEMON_SCRIPT="avalanche_logger_daemon.py"
REQ_FILE="requirements-daemon.txt"
VENV_NAME="avalanche_daemon_venv"
LOG_DIR="daemon_logs"
CONTAINER_TARGET="avalanche_node_logger_service"

echo "🕷️ Configurando Daemon para: $CONTAINER_TARGET"

# Crear directorio de logs
mkdir -p "$LOG_DIR"

# Requirements específicos
cat > "$REQ_FILE" << 'EOL'
# Paquetes mínimos - entropía controlada
psutil==5.9.0
docker==6.0.0
EOL

# Virtual environment
python3 -m venv "$VENV_NAME"
source "$VENV_NAME/bin/activate"

# Instalación segura
pip install --upgrade pip
pip install -r "$REQ_FILE"
deactivate

# Verificar que el contenedor objetivo existe
if ! docker ps -a --format "table {{.Names}}" | grep -q "$CONTAINER_TARGET"; then
    echo "⚠️  Contenedor $CONTAINER_TARGET no encontrado"
    echo "📋 Contenedores disponibles:"
    docker ps -a --format "table {{.Names}}\t{{.Status}}"
fi

# Iniciar daemon en background
echo "🚀 Iniciando daemon..."
nohup "$VENV_NAME/bin/python" "$DAEMON_SCRIPT" > "$LOG_DIR/daemon_output.log" 2>&1 &

# Verificar proceso
DAEMON_PID=$!
echo "📊 Daemon PID: $DAEMON_PID"
echo "📁 Logs: $LOG_DIR/"
echo "✅ Configuración completada"

# Log inicial
echo "$(date): Daemon iniciado para $CONTAINER_TARGET (PID: $DAEMON_PID)" >> "$LOG_DIR/daemon_audit.log"
