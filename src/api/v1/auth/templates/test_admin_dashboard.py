# test_admin_dashboard.py
import requests
import json


def test_admin_dashboard():
    """Test del dashboard admin"""
    BASE_URL = "http://localhost:5001"

    print("🧪 TESTING ADMIN DASHBOARD...")

    # Primero necesitamos un token de autenticación
    print("\n1. Obteniendo token de autenticación...")
    login_data = {
        "username": "admin",
        "password": "admin123"  # Asumiendo que existe en el sistema
    }

    # En un sistema real, esto vendría del endpoint /login
    test_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImFkbWluIiwicm9sZSI6ImFkbWluIiwiaXAiOiIxMjcuMC4wLjEiLCJleHAiOjE3MzM2NDAwMDAsImlzcyI6InRpbl90YW5fYWRtaW5fZGFzaGJvYXJkIn0.test_token_simulado"

    headers = {"Authorization": f"Bearer {test_token}"}

    # Test del dashboard principal
    print("\n2. Accediendo al dashboard admin...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/admin/account", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Dashboard accesible")
        else:
            print(f"   ❌ Error: {response.json()}")
    except Exception as e:
        print(f"   ❌ Connection error: {e}")

    # Test de endpoints de API
    print("\n3. Probando endpoints de API...")
    endpoints = [
        "/api/v1/benchmark/bcrypt",
        "/api/v1/benchmark/paranoid",
        "/api/v1/network/info"
    ]

    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
            print(f"   {endpoint}: Status {response.status_code}")
        except Exception as e:
            print(f"   {endpoint}: Error {e}")


if __name__ == "__main__":
    test_admin_dashboard()