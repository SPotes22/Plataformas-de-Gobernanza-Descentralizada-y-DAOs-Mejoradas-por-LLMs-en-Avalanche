# test_decorators_fixed.py
import requests
import json
import time


def test_all_decorators():
    """Tests para verificar todos los decorators funcionando"""
    BASE_URL = "http://localhost:5000"

    print("🧪 TESTING ALL DECORATORS...")

    # Test 1: Cache stats antes de registros
    print("\n1. Testing cache stats (empty)...")
    response = requests.get(f"{BASE_URL}/cache/stats")
    print(f"   Status: {response.status_code}")
    if response.status_code == 401:
        print("   ✅ @custom_jwt working - blocked unauthorized access")

    # Test 2: User registration con @memo_hasher
    print("\n2. Testing registration with @memo_hasher...")
    reg_data = {
        "username": "decorator_test_user",
        "password": "SecurePass123!",
        "role": "admin"
    }
    response = requests.post(f"{BASE_URL}/register", json=reg_data)
    print(f"   Status: {response.status_code}")
    result = response.json()
    print(f"   Hashing cached: {result.get('hashing_info', {}).get('cached', False)}")

    # Test 3: User login
    print("\n3. Testing login...")
    login_data = {
        "username": "decorator_test_user",
        "password": "SecurePass123!"
    }
    response = requests.post(f"{BASE_URL}/login", json=login_data)
    print(f"   Status: {response.status_code}")
    login_response = response.json()

    if response.status_code == 200:
        token = login_response.get('token')
        print(f"   Token received: {token[:50]}...")
        print(f"   JWT cached: {login_response.get('cache_info', {}).get('jwt_cached', False)}")

        # Test 4: Protected account con múltiples decorators
        print("\n4. Testing account with multiple decorators...")
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/account", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ All decorators working: @login_required + @custom_jwt + @load_memo_custom_jwt")

        # Test 5: Cache stats después de uso
        print("\n5. Testing cache stats after usage...")
        response = requests.get(f"{BASE_URL}/cache/stats", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            stats = response.json()
            print(f"   Hash cache size: {stats['hash_cache']['size']}")
            print(f"   JWT cache size: {stats['jwt_cache']['size']}")

    # Test 6: Rate limiting
    print("\n6. Testing rate limiting...")
    for i in range(3):
        response = requests.post(f"{BASE_URL}/login", json={"username": "test", "password": "wrong"})
        print(f"   Attempt {i + 1}: Status {response.status_code}")

    print("\n🎯 ALL TESTS COMPLETED!")


if __name__ == "__main__":
    test_all_decorators()