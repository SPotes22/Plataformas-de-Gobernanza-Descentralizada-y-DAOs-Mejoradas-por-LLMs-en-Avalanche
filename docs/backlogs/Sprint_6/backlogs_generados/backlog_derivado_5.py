#!/usr/bin/env python3
# Backlog Dynamic Reader: BL_06_5
# ⚡ MODO DINÁMICO - Lee backlog.json actual

import json
from pathlib import Path

def load_current_backlog():
    """Carga el backlog actual desde JSON"""
    backlog_file = Path(__file__).parent.parent / 'backlog.json'
    
    if not backlog_file.exists():
        return {"error": "Backlog no encontrado"}
    
    try:
        with open(backlog_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Buscar esta entrada específica
        for entry in data:
            if entry.get('id') == 'BL_06_5':
                return entry
        
        return {"error": "Entrada no encontrada en backlog"}
    
    except Exception as e:
        return {"error": str(e)}

def main():
    backlog_data = load_current_backlog()
    
    print("🎯 BACKLOG DINÁMICO - LIVE")
    print("=" * 50)
    
    if 'error' in backlog_data:
        print("❌ Error: {}".format(backlog_data['error']))
        return
    
    print("ID        : {}".format(backlog_data.get('id', 'N/A')))
    print("QUÉ       : {}".format(backlog_data.get('contenido', 'Sin contenido')))
    print("FECHA     : {}".format(backlog_data.get('timestamp', 'N/A')))
    print("USUARIO   : {}".format('arachne'))  # Hardcodeado por ahora
    print("=" * 50)
    print("💡 Este script lee el backlog.json ACTUAL")
    print("   Modifica el JSON y vuelve a ejecutar!")

if __name__ == "__main__":
    main()
