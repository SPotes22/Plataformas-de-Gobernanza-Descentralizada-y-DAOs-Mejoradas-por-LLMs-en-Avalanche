# test_forms_fixed.py
import requests
import json

def test_forms_access():
    """Test que verifica que los forms HTML están accesibles"""
    BASE_URL = "http://localhost:5000"
    
    print("🧪 TESTING FORMS ACCESS...")
    
    # Test 1: Home endpoint
    print("\n1. Testing home endpoint...")
    response = requests.get(f"{BASE_URL}/")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    
    # Test 2: Register form (GET)
    print("\n2. Testing register form (GET)...")
    response = requests.get(f"{BASE_URL}/register")
    print(f"   Status: {response.status_code}")
    print(f"   HTML form: {'✅' if response.status_code == 200 else '❌'}")
    
    # Test 3: Login form (GET)
    print("\n3. Testing login form (GET)...")
    response = requests.get(f"{BASE_URL}/login")
    print(f"   Status: {response.status_code}")
    print(f"   HTML form: {'✅' if response.status_code == 200 else '❌'}")
    
    # Test 4: Account instructions (GET)
    print("\n4. Testing account instructions (GET)...")
    response = requests.get(f"{BASE_URL}/account")
    print(f"   Status: {response.status_code}")
    print(f"   HTML instructions: {'✅' if response.status_code == 200 else '❌'}")
    
    # Test 5: Health check
    print("\n5. Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"   Status: {response.status_code}")
    print(f"   Health: {response.json().get('status')}")

def test_api_functionality():
    """Test de la funcionalidad API"""
    BASE_URL = "http://localhost:5000"
    
    print("\n🧪 TESTING API FUNCTIONALITY...")
    
    # Test registration via API
    print("\n1. Testing user registration via API...")
    reg_data = {
        "username": "testuser_forms",
        "password": "SecurePass123!",
        "role": "user"
    }
    response = requests.post(f"{BASE_URL}/register", json=reg_data)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json().get('message', 'Error')}")
    
    # Test login via API
    print("\n2. Testing user login via API...")
    login_data = {
        "username": "testuser_forms", 
        "password": "SecurePass123!"
    }
    response = requests.post(f"{BASE_URL}/login", json=login_data)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        token = response.json().get('token')
        print(f"   Token received: {'✅' if token else '❌'}")
        
        # Test protected endpoint
        print("\n3. Testing protected endpoint...")
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"{BASE_URL}/account", headers=headers)
        print(f"   Status: {response.status_code}")
        print(f"   Protected access: {'✅' if response.status_code == 200 else '❌'}")

if __name__ == "__main__":
    test_forms_access()
    test_api_functionality()