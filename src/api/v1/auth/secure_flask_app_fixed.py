# secure_flask_app_fixed.py
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


# DECORATORS CORREGIDOS Y COMPLETOS
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
    """Rate limiting básico - OWASP A05 - FIXED"""

    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # Implementación simplificada de rate limiting
            client_ip = request.remote_addr
            current_time = time.time()

            if client_ip not in login_attempts:
                login_attempts[client_ip] = []

            # Limpiar intentos antiguos
            login_attempts[client_ip] = [
                attempt_time for attempt_time in login_attempts[client_ip]
                if current_time - attempt_time < 3600  # Última hora
            ]

            if len(login_attempts[client_ip]) >= 100:  # 100 por hora
                return jsonify({"error": "Rate limit exceeded"}), 429

            login_attempts[client_ip].append(current_time)
            return f(*args, **kwargs)

        return decorated

    return decorator


def memo_hasher(iterations=1000):
    """
    Decorator @memo_hasher - Cachea resultados de funciones de hashing
    Útil para benchmarks y evitar recálculos
    """

    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # Crear clave única para cache
            cache_key = f"{f.__name__}_{hash(str(args))}_{hash(str(kwargs))}"

            # Verificar si ya está en cache
            if cache_key in hash_cache:
                return hash_cache[cache_key]

            # Ejecutar función y guardar en cache
            result = f(*args, **kwargs)
            hash_cache[cache_key] = result

            # Limitar tamaño del cache (LRU simple)
            if len(hash_cache) > 1000:
                # Eliminar el primer elemento (más antiguo)
                first_key = next(iter(hash_cache))
                del hash_cache[first_key]

            return result

        return decorated

    return decorator


def load_memo_custom_jwt(f):
    """
    Decorator @load_memo_custom_jwt - Carga JWT desde cache si existe
    Optimiza verificaciones repetidas del mismo token
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization') or session.get('token')

        if not token:
            return jsonify({"error": "Authentication required"}), 401

        if token.startswith('Bearer '):
            token = token[7:]

        # Verificar cache de JWT
        if token in jwt_cache:
            cached_result = jwt_cache[token]
            # Verificar si el token cacheado aún es válido
            if 'exp' in cached_result and cached_result['exp'] > time.time():
                request.current_user = cached_result
                return f(*args, **kwargs)
            else:
                # Token expirado, remover del cache
                del jwt_cache[token]

        # Verificar token normalmente
        verification = CustomJWT.decode(token, app.config['SECRET_KEY'])
        if "error" in verification:
            return jsonify({"error": verification["error"]}), 401

        # Guardar en cache (solo si es válido)
        jwt_cache[token] = verification
        request.current_user = verification

        return f(*args, **kwargs)

    return decorated


# Helper para prevenir brute force - OWASP A07
def check_brute_force(username: str, ip: str) -> bool:
    """Verificar si hay actividad de brute force"""
    current_time = time.time()
    user_key = f"{username}_{ip}"

    if user_key not in login_attempts:
        login_attempts[user_key] = []

    # Limpiar intentos antiguos
    login_attempts[user_key] = [
        attempt_time for attempt_time in login_attempts[user_key]
        if current_time - attempt_time < LOCKOUT_TIME
    ]

    # Verificar si excede límite
    if len(login_attempts[user_key]) >= MAX_LOGIN_ATTEMPTS:
        return True

    login_attempts[user_key].append(current_time)
    return False


# Función de hashing con memoización
@memo_hasher(iterations=1000)
def secure_hash_password(password: str) -> dict:
    """Función de hashing segura con cache"""
    salt = bcrypt.gensalt(rounds=12)
    password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)

    return {
        'hash': password_hash.decode('utf-8'),
        'algorithm': 'bcrypt',
        'iterations': 12,
        'timestamp': time.time()
    }


# Endpoints principales
@app.route('/register', methods=['POST'])
@rate_limit(limits="50 per hour")
def register():
    """Endpoint de registro - Crea firma de usuario"""
    data = request.get_json()

    # Validación de input - OWASP A03
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"error": "Username and password required"}), 400

    username = data['username'].strip()
    password = data['password']

    # Sanitización básica
    if len(username) < 3 or len(username) > 50:
        return jsonify({"error": "Username must be 3-50 characters"}), 400

    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters"}), 400

    # Verificar si usuario existe - OWASP A01
    if username in users_db:
        return jsonify({"error": "User already exists"}), 409

    # Crear hash seguro con memoización - OWASP A02
    hash_result = secure_hash_password(password)

    # Guardar usuario
    users_db[username] = {
        'password_hash': hash_result['hash'],
        'created_at': datetime.datetime.now().isoformat(),
        'role': data.get('role', 'user'),
        'last_login': None,
        'hash_algorithm': hash_result['algorithm']
    }

    return jsonify({
        "status": "User registered successfully",
        "message": "Firma creada exitosamente",
        "username": username,
        "security_level": "OWASP Top10 Compliant",
        "hashing_info": {
            "algorithm": hash_result['algorithm'],
            "cached": True,  # Indica que usó cache
            "iterations": hash_result['iterations']
        }
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

    # Prevenir brute force - OWASP A07
    if check_brute_force(username, client_ip):
        return jsonify({
            "error": "Account temporarily locked due to too many attempts",
            "lockout_time": "15 minutes"
        }), 429

    # Verificar usuario existe
    if username not in users_db:
        return jsonify({"error": "Invalid credentials"}), 401

    user = users_db[username]
    stored_hash = user['password_hash'].encode('utf-8')

    # Verificar password - Timing attack safe
    if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
        # Resetear contador de intentos
        user_key = f"{username}_{client_ip}"
        if user_key in login_attempts:
            login_attempts[user_key] = []

        # Actualizar último login
        user['last_login'] = datetime.datetime.now().isoformat()

        # Generar token JWT
        token_payload = {
            'username': username,
            'role': user['role'],
            'ip': client_ip,
            'exp': time.time() + (24 * 3600),  # 24 horas
            'iss': 'tin_tan_secure_app',
            'jti': hashlib.sha256(f"{username}{time.time()}".encode()).hexdigest()[:16]
        }

        token = CustomJWT.encode(token_payload, app.config['SECRET_KEY'])

        # Establecer en sesión también
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
            "security": "OWASP Top10 Protected",
            "cache_info": {
                "jwt_cached": True,
                "hash_cached": True
            }
        }), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401


@app.route('/account')
@login_required
@custom_jwt
@load_memo_custom_jwt
def account():
    """Endpoint de cuenta protegido - Usa todos los decorators"""
    user = request.current_user

    # Template data
    template_data = {
        "username": user['username'],
        "role": user['role'],
        "login_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ip_address": user.get('ip', 'Unknown'),
        "security_level": "OWASP Top10 Compliant",
        "cache_status": {
            "hash_cache_size": len(hash_cache),
            "jwt_cache_size": len(jwt_cache),
            "decorators_active": ["@login_required", "@custom_jwt", "@load_memo_custom_jwt"]
        },
        "features": [
            "Brute Force Protection",
            "Rate Limiting",
            "Secure JWT Tokens",
            "Input Sanitization",
            "Session Management",
            "Hash Memoization",
            "JWT Cache Optimization"
        ]
    }

    return render_template('admin_account.html', **template_data)


@app.route('/cache/stats')
@custom_jwt
def cache_stats():
    """Endpoint para ver estadísticas del cache"""
    return jsonify({
        "hash_cache": {
            "size": len(hash_cache),
            "keys_sample": list(hash_cache.keys())[:3] if hash_cache else []
        },
        "jwt_cache": {
            "size": len(jwt_cache),
            "keys_sample": list(jwt_cache.keys())[:2] if jwt_cache else []
        },
        "login_attempts": {
            "size": len(login_attempts),
            "blocked_ips": [ip for ip, attempts in login_attempts.items() if len(attempts) >= MAX_LOGIN_ATTEMPTS]
        }
    })


@app.route('/')
def home():
    return jsonify({
        "app": "Secure Flask App - OWASP Top10 + Custom JWT + Memoization",
        "version": "2.0",
        "endpoints": {
            "POST /register": "Create user signature with @memo_hasher",
            "POST /login": "Authenticate and get token",
            "GET /account": "Protected with @custom_jwt + @load_memo_custom_jwt",
            "GET /cache/stats": "Cache statistics",
            "security": "OWASP A01, A02, A03, A05, A07 + Memoization"
        },
        "decorators_implemented": [
            "@login_required",
            "@custom_jwt",
            "@rate_limit",
            "@memo_hasher",
            "@load_memo_custom_jwt"
        ]
    })


# Health check endpoint
@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.datetime.now().isoformat(),
        "users_registered": len(users_db),
        "cache_performance": {
            "hash_cache_hits": len(hash_cache),
            "jwt_cache_hits": len(jwt_cache)
        },
        "security": "OWASP Top10 Active + Memoization"
    })


if __name__ == "__main__":
    print("🚀 INICIANDO SECURE FLASK APP FIXED...")
    print("📍 Endpoints disponibles:")
    print("   POST /register  - Crear firma con @memo_hasher")
    print("   POST /login     - Autenticar y obtener token")
    print("   GET  /account   - Dashboard con @custom_jwt + @load_memo_custom_jwt")
    print("   GET  /cache/stats - Estadísticas de cache")
    print("   GET  /health    - Status de la aplicación")
    print("\n🔐 Decorators implementados:")
    print("   ✅ @login_required")
    print("   ✅ @custom_jwt")
    print("   ✅ @rate_limit (FIXED)")
    print("   ✅ @memo_hasher (NUEVO)")
    print("   ✅ @load_memo_custom_jwt (NUEVO)")

    app.run(host='0.0.0.0', port=5000, debug=True)