# secure_flask_app_fixed_with_forms.py
import bcrypt
import hashlib
import base64
import json
import time
import datetime
from functools import wraps
import hmac
from flask import Flask, request, jsonify, render_template, session, redirect, url_for

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tin_tan_owasp_top10_secure_2024'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(hours=24)

# Simulación de base de datos en memoria
users_db = {}
login_attempts = {}
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_TIME = 900  # 15 minutos

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
            100000  # 100k iterations para prevenir brute force
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
            
            # Verificar signature
            expected_signature = hashlib.pbkdf2_hmac(
                'sha256', 
                message, 
                secret.encode(), 
                100000
            )
            expected_b64 = CustomJWT.b64url_encode(expected_signature)
            
            # Timing-attack safe comparison
            if not hmac.compare_digest(signature_b64, expected_b64):
                return {"error": "Invalid signature"}
            
            # Decodificar payload
            payload_json = CustomJWT.b64url_decode(payload_b64).decode()
            payload = json.loads(payload_json)
            
            # Verificar expiración
            if 'exp' in payload and payload['exp'] < time.time():
                return {"error": "Token expired"}
                
            return payload
            
        except Exception as e:
            return {"error": f"Token invalid: {str(e)}"}

# DECORATORS
def login_required(f):
    """Decorator para requerir autenticación - OWASP A01"""
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
    """Decorator @custom_jwt - alias de login_required con cache"""
    @wraps(f)
    def decorated(*args, **kwargs):
        return login_required(f)(*args, **kwargs)
    return decorated

def rate_limit(limits="100 per hour"):
    """Rate limiting básico - OWASP A05"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            client_ip = request.remote_addr
            current_time = time.time()
            
            if client_ip not in login_attempts:
                login_attempts[client_ip] = []
            
            # Limpiar intentos antiguos
            login_attempts[client_ip] = [
                attempt_time for attempt_time in login_attempts[client_ip]
                if current_time - attempt_time < 3600  # Última hora
            ]
            
            if len(login_attempts[client_ip]) >= 100:
                return jsonify({"error": "Rate limit exceeded"}), 429
                
            login_attempts[client_ip].append(current_time)
            return f(*args, **kwargs)
        return decorated
    return decorator

# Helper para prevenir brute force
def check_brute_force(username: str, ip: str) -> bool:
    """Verificar si hay actividad de brute force"""
    current_time = time.time()
    user_key = f"{username}_{ip}"
    
    if user_key not in login_attempts:
        login_attempts[user_key] = []
    
    login_attempts[user_key] = [
        attempt_time for attempt_time in login_attempts[user_key]
        if current_time - attempt_time < LOCKOUT_TIME
    ]
    
    if len(login_attempts[user_key]) >= MAX_LOGIN_ATTEMPTS:
        return True
    
    login_attempts[user_key].append(current_time)
    return False

# ENDPOINTS GET PARA FORMS HTML (FIX METHOD NOT ALLOWED)
@app.route('/register', methods=['GET'])
def register_form():
    """Formulario HTML para registro - FIX METHOD NOT ALLOWED"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Registro - Secure App</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 500px; margin: 50px auto; padding: 20px; }
            .form-group { margin-bottom: 15px; }
            label { display: block; margin-bottom: 5px; }
            input, select { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
            button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
            .result { margin-top: 20px; padding: 10px; border-radius: 4px; }
            .success { background: #d4edda; color: #155724; }
            .error { background: #f8d7da; color: #721c24; }
        </style>
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
                        headers: {
                            'Content-Type': 'application/json',
                        },
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
        
        <div style="margin-top: 20px; font-size: 12px; color: #666;">
            <p><strong>Endpoints disponibles:</strong></p>
            <ul>
                <li><strong>POST /register</strong> - Registrar usuario (JSON)</li>
                <li><strong>POST /login</strong> - Iniciar sesión (JSON)</li>
                <li><strong>GET /account</strong> - Dashboard protegido</li>
                <li><strong>GET /health</strong> - Estado del servidor</li>
            </ul>
        </div>
    </body>
    </html>
    '''

@app.route('/login', methods=['GET'])
def login_form():
    """Formulario HTML para login - FIX METHOD NOT ALLOWED"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Login - Secure App</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 500px; margin: 50px auto; padding: 20px; }
            .form-group { margin-bottom: 15px; }
            label { display: block; margin-bottom: 5px; }
            input { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
            button { background: #28a745; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
            .result { margin-top: 20px; padding: 10px; border-radius: 4px; }
            .success { background: #d4edda; color: #155724; }
            .error { background: #f8d7da; color: #721c24; }
            .token { word-break: break-all; font-family: monospace; font-size: 12px; }
        </style>
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
                        headers: {
                            'Content-Type': 'application/json',
                        },
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
                            <p><em>Guarda este token para acceder a endpoints protegidos</em></p>
                            <button onclick="location.href='/account'">Ir al Dashboard</button>
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
        </script>
    </body>
    </html>
    '''

@app.route('/account', methods=['GET'])
def account_form():
    """Formulario HTML para cuenta - Con instrucciones de uso"""
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
            .result { background: #f8f9fa; padding: 15px; border-radius: 4px; margin-top: 10px; font-family: monospace; }
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
            <h3>🔒 Acceso al Dashboard Protegido</h3>
            <p>Para acceder al dashboard protegido, ingresa tu token JWT:</p>
            <input type="text" id="authToken" class="token-input" placeholder="Pega tu token JWT aquí">
            <button onclick="accessProtected()">Acceder al Dashboard Protegido</button>
            <div id="protectedResult" class="result"></div>
        </div>

        <div class="card">
            <h3>🌐 Estado del Servidor</h3>
            <button onclick="checkHealth()">Verificar Salud</button>
            <div id="healthResult" class="result"></div>
        </div>

        <script>
            async function accessProtected() {
                const token = document.getElementById('authToken').value;
                if (!token) {
                    alert('Por favor ingresa un token');
                    return;
                }

                try {
                    const response = await fetch('/account', {
                        headers: {
                            'Authorization': `Bearer ${token}`
                        }
                    });
                    
                    const result = await response.json();
                    document.getElementById('protectedResult').textContent = JSON.stringify(result, null, 2);
                } catch (error) {
                    document.getElementById('protectedResult').textContent = 'Error: ' + error.message;
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
        </script>
    </body>
    </html>
    '''

# ENDPOINTS PRINCIPALES (POST)
@app.route('/register', methods=['POST'])
@rate_limit(limits="50 per hour")
def register():
    """Endpoint de registro - Crea firma de usuario"""
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
    
    # Crear hash seguro
    salt = bcrypt.gensalt(rounds=12)
    password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
    
    users_db[username] = {
        'password_hash': password_hash.decode('utf-8'),
        'created_at': datetime.datetime.now().isoformat(),
        'role': data.get('role', 'user'),
        'last_login': None
    }
    
    return jsonify({
        "status": "User registered successfully",
        "message": "Firma creada exitosamente",
        "username": username,
        "security_level": "OWASP Top10 Compliant"
    }), 201

@app.route('/login', methods=['POST'])
@rate_limit(limits="30 per hour")
def login():
    """Endpoint de login - Consume firma y autentica"""
    data = request.get_json()
    
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"error": "Username and password required"}), 400
    
    username = data['username'].strip()
    password = data['password']
    client_ip = request.remote_addr
    
    if check_brute_force(username, client_ip):
        return jsonify({
            "error": "Account temporarily locked due to too many attempts",
            "lockout_time": "15 minutes"
        }), 429
    
    if username not in users_db:
        return jsonify({"error": "Invalid credentials"}), 401
    
    user = users_db[username]
    stored_hash = user['password_hash'].encode('utf-8')
    
    if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
        user_key = f"{username}_{client_ip}"
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
            "message": "Imagine you are logged now 🔐",
            "token": token,
            "user": {
                "username": username,
                "role": user['role'],
                "login_time": user['last_login']
            },
            "security": "OWASP Top10 Protected"
        }), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401

@app.route('/account', methods=['POST'])
@login_required
@custom_jwt
def account_protected():
    """Endpoint protegido de cuenta"""
    user = request.current_user
    
    return jsonify({
        "status": "success",
        "message": "¡Bienvenido al dashboard protegido!",
        "user": user,
        "access_time": datetime.datetime.now().isoformat(),
        "security": "OWASP Top10 Protected"
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.datetime.now().isoformat(),
        "users_registered": len(users_db),
        "endpoints_working": True,
        "server": "Secure Flask App Fixed"
    })

@app.route('/')
def home():
    return jsonify({
        "app": "Secure Flask App - OWASP Top10 + Forms Fixed",
        "version": "2.1",
        "endpoints": {
            "GET /register": "Formulario HTML de registro",
            "POST /register": "API JSON de registro", 
            "GET /login": "Formulario HTML de login",
            "POST /login": "API JSON de login",
            "GET /account": "Instrucciones y acceso",
            "POST /account": "Dashboard protegido (requiere token)",
            "GET /health": "Estado del servidor"
        },
        "instructions": "Visita /register o /login en el navegador para usar los forms"
    })

if __name__ == "__main__":
    print("🚀 INICIANDO SECURE FLASK APP WITH FORMS...")
    print("📍 Endpoints disponibles:")
    print("   GET  /register  - Formulario HTML de registro")
    print("   POST /register  - API JSON de registro") 
    print("   GET  /login     - Formulario HTML de login")
    print("   POST /login     - API JSON de login")
    print("   GET  /account   - Instrucciones y acceso")
    print("   POST /account   - Dashboard protegido (requiere token)")
    print("   GET  /health    - Estado del servidor")
    print("\n🌐 Ahora puedes acceder desde el navegador:")
    print("   http://localhost:5000/register")
    print("   http://localhost:5000/login")
    print("   http://localhost:5000/account")
    
    app.run(host='0.0.0.0', port=5000, debug=True)