# scripts/test_docker.py
import os
from pathlib import Path

def test_docker_environment():
    print("🧪 Probando entorno Docker...")
    
    # Verificar paths
    base_path = Path("/app")
    print(f"📁 Path base: {base_path}")
    print(f"📁 Existe: {base_path.exists()}")
    
    # Verificar scripts
    scripts_path = base_path / "scripts"
    print(f"📂 Scripts path: {scripts_path}")
    print(f"📂 Contenido: {list(scripts_path.glob('*.py')) if scripts_path.exists() else 'NO EXISTE'}")
    
    # Verificar variables de entorno
    print(f"🔧 CICD_MODE: {os.environ.get('CICD_MODE', 'No definido')}")
    print(f"🔧 ENVIRONMENT: {os.environ.get('ENVIRONMENT', 'No definido')}")
    
    print("✅ Prueba completada")

if __name__ == "__main__":
    test_docker_environment()
