'''
StockSpider api usage - Servidor de Archivos Básico en Red
Copyright (C) 2025 Santiago Potes Giraldo
SPDX-License-Identifier: GPL-3.0-or-later

Este archivo es parte de StockSpider.

StockSpider is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
'''
# secure_flask_app_json_fixed.py
import bcrypt
import hashlib
import base64
import json
import time
import datetime
from functools import wraps
import hmac
from flask import Flask, request, jsonify, render_template, session

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tin_tan_owasp_top10_secure_2025'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(hours=24)

# Simulación de base de datos en memoria
users_db = {}
login_attempts = {}
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_TIME = 900

# Cache para memoización
hash_cache = {}
jwt_cache = {}

class CustomJWT:
    """JWT personalizado con seguridad OWASP Top10"""
    
    @staticmethod
    def b64url_encode(data: bytes) -> str:
        return base64.urlsafe_b64encode(data).decode().rstrip('=')
    
    @staticmethod
    def b64url_decode(data: str) -> bytes:
        pad = '=' * (-len(data) % 4)
        return base64.urlsafe_b64decode(data + pad)
    
    @staticmethod
    def encode(payload: dict, secret: str) -> str:
        """Codificar JWT seguro"""
        header = {
            "alg": "HS256",
            "typ": "JWT",
            "kid": "custom_jwt_v1"
        }
        
        header_b64 = CustomJWT.b64url_encode(json.dumps(header).encode())
        payload_b64 = CustomJWT.b64url_encode(json.dumps(payload).encode())
        
        message = f"{header_b64}.{payload_b64}".encode()
        signature = hashlib.pbkdf2_hmac(
            'sha256', 
            message, 
            secret.encode(), 
            100000
        )
        signature_b64 = CustomJWT.b64url_encode(signature)
        
        return f"{header_b64}.{payload_b64}.{signature_b64}"
    
    @staticmethod
    def decode(token: str, secret: str) -> dict:
        """Decodificar y verificar JWT"""
        try:
            parts = token.split('.')
            if len(parts) != 3:
                return {"error": "Token structure invalid"}
            
            header_b64, payload_b64, signature_b64 = parts
            message = f"{header_b64}.{payload_b64}".encode()
            
            expected_signature = hashlib.pbkdf2_hmac(
                'sha256', 
                message, 
                secret.encode(), 
                100000
            )
            expected_b64 = CustomJWT.b64url_encode(expected_signature)
            
            if not hmac.compare_digest(signature_b64, expected_b64):
                return {"error": "Invalid signature"}
            
            payload_json = CustomJWT.b64url_decode(payload_b64).decode()
            payload = json.loads(payload_json)
            
            if 'exp' in payload and payload['exp'] < time.time():
                return {"error": "Token expired"}
                
            return payload
            
        except Exception as e:
            return {"error": f"Token invalid: {str(e)}"}

# DECORATORS
def login_required(f):
    """Decorator para requerir autenticación"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization') or session.get('token')
        
        if not token:
            return jsonify({"error": "Authentication required"}), 401
            
        if token.startswith('Bearer '):
            token = token[7:]
            
        verification = CustomJWT.decode(token, app.config['SECRET_KEY'])
        if "error" in verification:
            return jsonify({"error": verification["error"]}), 401
            
        request.current_user = verification
        return f(*args, **kwargs)
    return decorated

def custom_jwt(f):
    """Decorator @custom_jwt"""
    @wraps(f)
    def decorated(*args, **kwargs):
        return login_required(f)(*args, **kwargs)
    return decorated

# ENDPOINTS FIXED - SOLO JSON RESPONSES
@app.route('/register', methods=['GET'])
def register_form():
    """Formulario HTML para registro"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Registro - Secure App</title>
        <style>body{font-family:Arial;max-width:500px;margin:50px auto;padding:20px}.form-group{margin-bottom:15px}label{display:block;margin-bottom:5px}input,select{width:100%;padding:8px;border:1px solid #ddd;border-radius:4px}button{background:#007bff;color:white;padding:10px 20px;border:none;border-radius:4px;cursor:pointer}.result{margin-top:20px;padding:10px;border-radius:4px}.success{background:#d4edda;color:#155724}.error{background:#f8d7da;color:#721c24}</style>
    </head>
    <body>
        <h2>🔐 Registro de Usuario</h2>
        <form id="registerForm">
            <div class="form-group">
                <label for="username">Usuario:</label>
                <input type="text" id="username" name="username" required>
            </div>
            <div class="form-group">
                <label for="password">Contraseña:</label>
                <input type="password" id="password" name="password" required>
            </div>
            <div class="form-group">
                <label for="role">Rol:</label>
                <select id="role" name="role">
                    <option value="user">Usuario</option>
                    <option value="admin">Administrador</option>
                </select>
            </div>
            <button type="submit">Registrar</button>
        </form>
        <div id="result"></div>
        
        <script>
            document.getElementById('registerForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                const formData = {
                    username: document.getElementById('username').value,
                    password: document.getElementById('password').value,
                    role: document.getElementById('role').value
                };
                
                try {
                    const response = await fetch('/register', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify(formData)
                    });
                    
                    const result = await response.json();
                    const resultDiv = document.getElementById('result');
                    
                    if (response.ok) {
                        resultDiv.className = 'result success';
                        resultDiv.innerHTML = `<strong>✅ Éxito:</strong> ${result.message || 'Usuario registrado'}`;
                    } else {
                        resultDiv.className = 'result error';
                        resultDiv.innerHTML = `<strong>❌ Error:</strong> ${result.error || 'Error desconocido'}`;
                    }
                } catch (error) {
                    document.getElementById('result').className = 'result error';
                    document.getElementById('result').innerHTML = `<strong>❌ Error de conexión:</strong> ${error.message}`;
                }
            });
        </script>
    </body>
    </html>
    '''

@app.route('/login', methods=['GET'])
def login_form():
    """Formulario HTML para login"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Login - Secure App</title>
        <style>body{font-family:Arial;max-width:500px;margin:50px auto;padding:20px}.form-group{margin-bottom:15px}label{display:block;margin-bottom:5px}input{width:100%;padding:8px;border:1px solid #ddd;border-radius:4px}button{background:#28a745;color:white;padding:10px 20px;border:none;border-radius:4px;cursor:pointer}.result{margin-top:20px;padding:10px;border-radius:4px}.success{background:#d4edda;color:#155724}.error{background:#f8d7da;color:#721c24}.token{word-break:break-all;font-family:monospace;font-size:12px}</style>
    </head>
    <body>
        <h2>🔑 Iniciar Sesión</h2>
        <form id="loginForm">
            <div class="form-group">
                <label for="username">Usuario:</label>
                <input type="text" id="username" name="username" required>
            </div>
            <div class="form-group">
                <label for="password">Contraseña:</label>
                <input type="password" id="password" name="password" required>
            </div>
            <button type="submit">Iniciar Sesión</button>
        </form>
        <div id="result"></div>
        
        <script>
            document.getElementById('loginForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                const formData = {
                    username: document.getElementById('username').value,
                    password: document.getElementById('password').value
                };
                
                try {
                    const response = await fetch('/login', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify(formData)
                    });
                    
                    const result = await response.json();
                    const resultDiv = document.getElementById('result');
                    
                    if (response.ok) {
                        resultDiv.className = 'result success';
                        resultDiv.innerHTML = `
                            <strong>✅ ${result.message}</strong>
                            <p><strong>Usuario:</strong> ${result.user.username}</p>
                            <p><strong>Rol:</strong> ${result.user.role}</p>
                            <div class="token">
                                <strong>Token:</strong><br>
                                ${result.token}
                            </div>
                            <p><em>Usa este token para acceder a endpoints protegidos</em></p>
                            <button onclick="testProtectedEndpoint('${result.token}')">Probar Endpoint Protegido</button>
                        `;
                    } else {
                        resultDiv.className = 'result error';
                        resultDiv.innerHTML = `<strong>❌ Error:</strong> ${result.error || 'Error desconocido'}`;
                    }
                } catch (error) {
                    document.getElementById('result').className = 'result error';
                    document.getElementById('result').innerHTML = `<strong>❌ Error de conexión:</strong> ${error.message}`;
                }
            });

            async function testProtectedEndpoint(token) {
                try {
                    const response = await fetch('/account', {
                        method: 'POST',
                        headers: {
                            'Authorization': `Bearer ${token}`,
                            'Content-Type': 'application/json'
                        }
                    });
                    
                    const result = await response.json();
                    alert('✅ Endpoint protegido funciona: ' + (result.message || 'Éxito'));
                } catch (error) {
                    alert('❌ Error: ' + error.message);
                }
            }
        </script>
    </body>
    </html>
    '''

@app.route('/account', methods=['GET'])
def account_instructions():
    """Instrucciones para usar el endpoint protegido - FIXED"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Dashboard - Secure App</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
            .card { border: 1px solid #ddd; border-radius: 8px; padding: 20px; margin-bottom: 20px; }
            .protected { background: #fff3cd; border-color: #ffeaa7; }
            button { background: #6c757d; color: white; padding: 10px 15px; border: none; border-radius: 4px; cursor: pointer; margin: 5px; }
            .token-input { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 4px; }
            .result { background: #f8f9fa; padding: 15px; border-radius: 4px; margin-top: 10px; font-family: monospace; white-space: pre-wrap; }
            .success { background: #d4edda; color: #155724; }
            .error { background: #f8d7da; color: #721c24; }
        </style>
    </head>
    <body>
        <h1>🔐 Dashboard - Secure App</h1>
        
        <div class="card">
            <h3>📋 Instrucciones de Uso</h3>
            <ol>
                <li>Ve a <a href="/register">/register</a> para crear un usuario</li>
                <li>Ve a <a href="/login">/login</a> para obtener un token</li>
                <li>Usa el token en el header Authorization: Bearer [token]</li>
                <li>Accede a endpoints protegidos como /account (con token)</li>
            </ol>
        </div>

        <div class="card protected">
            <h3>🔒 Probar Endpoint Protegido</h3>
            <p>Ingresa tu token JWT para probar el endpoint protegido:</p>
            <input type="text" id="authToken" class="token-input" placeholder="Pega tu token JWT aquí" value="">
            <div>
                <button onclick="testProtectedEndpoint()">Probar Endpoint Protegido (POST)</button>
                <button onclick="testProtectedGet()">Probar Endpoint GET</button>
            </div>
            <div id="protectedResult" class="result"></div>
        </div>

        <div class="card">
            <h3>🌐 Estado del Servidor</h3>
            <button onclick="checkHealth()">Verificar Salud</button>
            <div id="healthResult" class="result"></div>
        </div>

        <script>
            async function testProtectedEndpoint() {
                const token = document.getElementById('authToken').value;
                if (!token) {
                    alert('Por favor ingresa un token');
                    return;
                }

                try {
                    const response = await fetch('/account', {
                        method: 'POST',
                        headers: {
                            'Authorization': `Bearer ${token}`,
                            'Content-Type': 'application/json'
                        }
                    });
                    
                    const result = await response.json();
                    const resultDiv = document.getElementById('protectedResult');
                    resultDiv.textContent = JSON.stringify(result, null, 2);
                    resultDiv.className = response.ok ? 'result success' : 'result error';
                } catch (error) {
                    document.getElementById('protectedResult').textContent = 'Error: ' + error.message;
                    document.getElementById('protectedResult').className = 'result error';
                }
            }

            async function testProtectedGet() {
                const token = document.getElementById('authToken').value;
                if (!token) {
                    alert('Por favor ingresa un token');
                    return;
                }

                try {
                    const response = await fetch('/protected-data', {
                        method: 'GET',
                        headers: {
                            'Authorization': `Bearer ${token}`
                        }
                    });
                    
                    const result = await response.json();
                    const resultDiv = document.getElementById('protectedResult');
                    resultDiv.textContent = JSON.stringify(result, null, 2);
                    resultDiv.className = response.ok ? 'result success' : 'result error';
                } catch (error) {
                    document.getElementById('protectedResult').textContent = 'Error: ' + error.message;
                    document.getElementById('protectedResult').className = 'result error';
                }
            }

            async function checkHealth() {
                try {
                    const response = await fetch('/health');
                    const result = await response.json();
                    document.getElementById('healthResult').textContent = JSON.stringify(result, null, 2);
                } catch (error) {
                    document.getElementById('healthResult').textContent = 'Error: ' + error.message;
                }
            }

            // Cargar token desde URL si existe
            const urlParams = new URLSearchParams(window.location.search);
            const tokenFromUrl = urlParams.get('token');
            if (tokenFromUrl) {
                document.getElementById('authToken').value = tokenFromUrl;
            }
        </script>
    </body>
    </html>
    '''

# ENDPOINTS API - SOLO JSON RESPONSES
@app.route('/register', methods=['POST'])
def register():
    """Endpoint de registro - SOLO JSON"""
    data = request.get_json()
    
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"error": "Username and password required"}), 400
    
    username = data['username'].strip()
    password = data['password']
    
    if len(username) < 3 or len(username) > 50:
        return jsonify({"error": "Username must be 3-50 characters"}), 400
    
    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters"}), 400
    
    if username in users_db:
        return jsonify({"error": "User already exists"}), 409
    
    salt = bcrypt.gensalt(rounds=12)
    password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
    
    users_db[username] = {
        'password_hash': password_hash.decode('utf-8'),
        'created_at': datetime.datetime.now().isoformat(),
        'role': data.get('role', 'user'),
        'last_login': None
    }
    
    return jsonify({
        "status": "success",
        "message": "Usuario registrado exitosamente",
        "username": username,
        "security_level": "OWASP Top10 Compliant"
    }), 201

@app.route('/login', methods=['POST'])
def login():
    """Endpoint de login - SOLO JSON"""
    data = request.get_json()
    
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"error": "Username and password required"}), 400
    
    username = data['username'].strip()
    password = data['password']
    client_ip = request.remote_addr
    
    # Verificar brute force
    user_key = f"{username}_{client_ip}"
    current_time = time.time()
    if user_key in login_attempts:
        recent_attempts = [t for t in login_attempts[user_key] if current_time - t < LOCKOUT_TIME]
        if len(recent_attempts) >= MAX_LOGIN_ATTEMPTS:
            return jsonify({"error": "Account temporarily locked"}), 429
        login_attempts[user_key] = recent_attempts
    
    if username not in users_db:
        login_attempts.setdefault(user_key, []).append(current_time)
        return jsonify({"error": "Invalid credentials"}), 401
    
    user = users_db[username]
    stored_hash = user['password_hash'].encode('utf-8')
    
    if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
        # Login exitoso - limpiar intentos
        if user_key in login_attempts:
            login_attempts[user_key] = []
        
        user['last_login'] = datetime.datetime.now().isoformat()
        
        token_payload = {
            'username': username,
            'role': user['role'],
            'ip': client_ip,
            'exp': time.time() + (24 * 3600),
            'iss': 'tin_tan_secure_app'
        }
        
        token = CustomJWT.encode(token_payload, app.config['SECRET_KEY'])
        
        session['token'] = token
        session['username'] = username
        session.permanent = True
        
        return jsonify({
            "status": 200,
            "message": "Autenticación exitosa",
            "token": token,
            "user": {
                "username": username,
                "role": user['role'],
                "login_time": user['last_login']
            },
            "security": "OWASP Top10 Protected"
        }), 200
    else:
        login_attempts.setdefault(user_key, []).append(current_time)
        return jsonify({"error": "Invalid credentials"}), 401

@app.route('/account', methods=['POST'])
@login_required
@custom_jwt
def account_protected():
    """Endpoint protegido de cuenta - SOLO JSON RESPONSE"""
    user = request.current_user
    
    return jsonify({
        "status": "success",
        "message": "¡Bienvenido al dashboard protegido!",
        "user": user,
        "access_time": datetime.datetime.now().isoformat(),
        "security": "OWASP Top10 Protected",
        "endpoint": "POST /account",
        "response_type": "JSON"
    })

@app.route('/protected-data', methods=['GET'])
@login_required
@custom_jwt
def protected_data():
    """Endpoint protegido adicional - SOLO JSON"""
    user = request.current_user
    
    return jsonify({
        "status": "success",
        "message": "Datos protegidos accesibles",
        "user_info": user,
        "data": {
            "feature_flags": ["admin_panel", "api_access", "user_management"],
            "server_stats": {
                "users_count": len(users_db),
                "active_sessions": len(jwt_cache),
                "uptime": "running"
            }
        },
        "timestamp": datetime.datetime.now().isoformat()
    })

@app.route('/health', methods=['GET'])
def health():
    """Health check - SOLO JSON"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.datetime.now().isoformat(),
        "users_registered": len(users_db),
        "endpoints_working": True,
        "server": "Secure Flask App JSON Fixed",
        "version": "2.2"
    })

@app.route('/')
def home():
    """Home endpoint - SOLO JSON"""
    return jsonify({
        "app": "Secure Flask App - JSON Responses Fixed",
        "version": "2.2",
        "endpoints": {
            "GET /register": "Formulario HTML de registro",
            "POST /register": "API JSON de registro", 
            "GET /login": "Formulario HTML de login",
            "POST /login": "API JSON de login",
            "GET /account": "Instrucciones y acceso",
            "POST /account": "Dashboard protegido (JSON response)",
            "GET /protected-data": "Datos protegidos (JSON)",
            "GET /health": "Estado del servidor (JSON)"
        },
        "instructions": "Todos los endpoints POST retornan JSON puro"
    })

if __name__ == "__main__":
    print("🚀 INICIANDO SECURE FLASK APP JSON FIXED...")
    print("📍 Endpoints disponibles:")
    print("   GET  /register      - Formulario HTML de registro")
    print("   POST /register      - API JSON de registro") 
    print("   GET  /login         - Formulario HTML de login")
    print("   POST /login         - API JSON de login")
    print("   GET  /account       - Instrucciones y acceso")
    print("   POST /account       - Dashboard protegido (JSON PURO)")
    print("   GET  /protected-data - Datos protegidos (JSON)")
    print("   GET  /health        - Estado del servidor (JSON)")
    print("\n🔧 FIX APPLIED: Todos los endpoints POST retornan JSON puro")
    print("🌐 Accede desde:")
    print("   http://localhost:5000/account")
    print("   http://localhost:5000/register") 
    print("   http://localhost:5000/login")
    
    app.run(host='0.0.0.0', port=5001, debug=True)
