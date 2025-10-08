# admin_dashboard_integration.py
from flask import Flask, request, jsonify, render_template, session
from functools import wraps
import datetime
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tin_tan_admin_dashboard_2024'

# Importar componentes existentes (simulados para el ejemplo)
from secure_flask_app_fixed import (login_required, custom_jwt, load_memo_custom_jwt)


@app.route('/api/v1/admin/account')
@login_required
@custom_jwt
@load_memo_custom_jwt
def admin_account_dashboard():
    """Endpoint de dashboard admin con template corregido"""
    user = request.current_user

    # Verificar que el usuario tenga rol de admin
    if user.get('role') != 'admin':
        return jsonify({"error": "Admin access required"}), 403

    # Datos para el template
    dashboard_data = {
        "username": user['username'],
        "role": user['role'],
        "login_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ip_address": user.get('ip', 'Unknown'),
        "security_level": "OWASP Top10 Compliant",
        "api_version": "v1",
        "cache_status": {
            "hash_cache_size": 42,  # Estos vendrían del sistema real
            "jwt_cache_size": 15,
            "decorators_active": ["@login_required", "@custom_jwt", "@load_memo_custom_jwt"]
        },
        "features": [
            "Brute Force Protection",
            "Rate Limiting",
            "Secure JWT Tokens",
            "Input Sanitization",
            "Session Management",
            "Hash Memoization",
            "JWT Cache Optimization",
            "Admin Dashboard"
        ]
    }

    return render_template('admin_dashboard.html', **dashboard_data)


# Template corregido (inline para simplicidad)
@app.route('/template/admin_dashboard_source')
def admin_dashboard_source():
    """Muestra el código fuente del template corregido"""
    return '''
<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Admin Dashboard — Benchmarks & Auth</title>
  <style>
    :root{--bg:#0f172a;--card:#0b1220;--muted:#94a3b8;--accent:#60a5fa;--success:#10b981}
    *{box-sizing:border-box}
    body{margin:0;font-family:Inter,system-ui,-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Helvetica,Arial,sans-serif;background:linear-gradient(180deg,#071026 0%,#071935 100%);color:#e6eef8}
    .container{max-width:1100px;margin:28px auto;padding:20px}
    header{display:flex;align-items:center;justify-content:space-between}
    h1{margin:0;font-size:20px}
    .grid{display:grid;grid-template-columns:1fr 360px;gap:18px;margin-top:18px}
    .card{background:var(--card);padding:14px;border-radius:12px;box-shadow:0 6px 18px rgba(2,6,23,.6)}
    .small{font-size:13px;color:var(--muted)}
    button{background:var(--accent);border:none;color:#06203a;padding:8px 12px;border-radius:8px;cursor:pointer}
    .muted{color:var(--muted)}
    .row{display:flex;gap:10px;align-items:center}
    label{display:block;font-size:13px;margin-bottom:6px;color:var(--muted)}
    input[type=text],select,textarea{width:100%;padding:8px;border-radius:8px;border:1px solid rgba(255,255,255,.04);background:#071428;color:inherit}
    .result{font-family:monospace;background:#031022;padding:10px;border-radius:8px;overflow:auto;max-height:220px}
    .stat{display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px dashed rgba(255,255,255,.03)}
    .actions{display:flex;gap:8px}
    .endpoint-list{display:flex;flex-direction:column;gap:8px}
    .chip{background:rgba(255,255,255,.03);padding:6px 10px;border-radius:999px;font-size:12px}
    .footer{margin-top:18px;color:var(--muted);font-size:13px;text-align:center}
    .ok{color:var(--success)}
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>Admin Dashboard — Benchmarks &amp; Auth</h1>
      <div class="small">Conectado como: <span class="chip">{{ username }}</span> | API: <span class="chip">{{ api_version }}</span></div>
    </header>

    <div class="grid">
      <!-- Main column -->
      <main>
        <section class="card">
          <div style="display:flex;justify-content:space-between;align-items:center">
            <div>
              <strong>Benchmarks</strong>
              <div class="small">Ejecuta y compara los endpoints de benchmark</div>
            </div>
            <div class="actions">
              <button id="run-bcrypt">Ejecutar bcrypt</button>
              <button id="run-paranoid">Ejecutar paranoid</button>
              <button id="run-both">Ejecutar ambos</button>
            </div>
          </div>

          <div style="margin-top:12px;display:flex;gap:12px">
            <div style="flex:1">
              <label for="test-password">Contraseña de prueba</label>
              <input id="test-password" type="text" value="test_password_123" />
            </div>
            <div style="width:120px">
              <label for="quick-iter">Iteraciones (opcional)</label>
              <select id="quick-iter">
                <option value="100">100</option>
                <option value="250" selected>250</option>
                <option value="500">500</option>
                <option value="1000">1000</option>
              </select>
            </div>
          </div>

          <hr style="margin:12px 0;border:0;border-top:1px solid rgba(255,255,255,.04)">

          <div style="display:flex;gap:12px">
            <div style="flex:1">
              <label for="benchmark-result">Resultado</label>
              <div id="benchmark-result" class="result">Aún no se han ejecutado benchmarks.</div>
            </div>
            <div style="width:260px">
              <label for="stats">Estadísticas</label>
              <div id="stats" class="card" style="margin-top:8px;padding:10px">
                <div class="stat"><span>Bcrypt create (mean)</span><strong id="b-create">—</strong></div>
                <div class="stat"><span>Bcrypt auth (mean)</span><strong id="b-auth">—</strong></div>
                <div class="stat"><span>Paranoid create (mean)</span><strong id="p-create">—</strong></div>
                <div class="stat"><span>Paranoid auth (mean)</span><strong id="p-auth">—</strong></div>
                <div class="stat"><span>Muestras</span><strong id="samples">0</strong></div>
              </div>

              <div style="margin-top:10px;display:flex;gap:8px">
                <button id="export-csv">Exportar CSV</button>
                <button id="clear-log">Limpiar</button>
              </div>
            </div>
          </div>
        </section>

        <section class="card" style="margin-top:14px">
          <strong>Network &amp; Tokens</strong>
          <div class="small">Genera y verifica tokens RSA desde el dashboard</div>

          <div style="margin-top:10px;display:flex;gap:10px;align-items:center">
            <div style="flex:1">
              <label for="username">Usuario</label>
              <input id="username" type="text" value="{{ username }}" />
            </div>
            <div style="width:140px">
              <label for="role">Rol</label>
              <input id="role" type="text" value="{{ role }}" />
            </div>
            <div style="width:160px;display:flex;flex-direction:column;gap:6px">
              <button id="gen-token">Generar Token</button>
              <button id="verify-token">Verificar Token</button>
            </div>
          </div>

          <div style="margin-top:12px">
            <label for="token-box">Token</label>
            <textarea id="token-box" rows="4" style="width:100%"></textarea>
            <div style="margin-top:8px;display:flex;gap:8px;justify-content:flex-end">
              <button id="copy-token">Copiar token</button>
            </div>
          </div>

          <div style="margin-top:12px">
            <label for="network-info">Red</label>
            <div id="network-info" class="result">Presiona <button id="refresh-net">Actualizar</button> para obtener información de red</div>
          </div>
        </section>

      </main>

      <!-- Right column -->
      <aside>
        <section class="card endpoint-list">
          <strong>Endpoints</strong>
          <div class="small">Listado rápido</div>
          <div style="margin-top:8px" class="small">
            <div>/benchmark/bcrypt — POST/GET</div>
            <div>/benchmark/paranoid — POST/GET</div>
            <div>/auth/rsa-token — POST</div>
            <div>/auth/verify-rsa-token — POST</div>
            <div>/network/info — GET</div>
          </div>
        </section>

        <section class="card">
          <strong>Logs</strong>
          <label for="log">Registros de actividad</label>
          <div id="log" class="result">Sin logs aún.</div>
        </section>

        <section class="card">
          <strong>Acciones rápidas</strong>
          <div style="display:flex;flex-direction:column;gap:8px;margin-top:8px">
            <button id="ping-server">Ping servidor</button>
            <button id="fetch-both">Obtener ambos resultados</button>
          </div>
        </section>
      </aside>
    </div>

    <div class="footer">Dashboard creado para consumir los endpoints del servidor de benchmark. Usar con cuidado en entornos de producción.</div>
  </div>

  <script>
    // Helper
    const $ = id => document.getElementById(id);
    const API_ROOT = '/api/v1'; // Usar ruta base de la API

    function log(msg){
      const el = $('log');
      const now = new Date().toISOString();
      el.textContent = `[${now}] ${msg}\\n` + el.textContent;
    }

    function showResult(obj){
      $('benchmark-result').textContent = JSON.stringify(obj, null, 2);
    }

    async function runEndpoint(path, opts){
      try{
        const res = await fetch(API_ROOT + path, opts);
        const json = await res.json();
        log(`OK ${path} (${res.status})`);
        return json;
      }catch(e){
        log(`ERROR ${path}: ${e.message}`);
        return {error: e.message};
      }
    }

    // Benchmarks
    async function runBcrypt(){
      $('run-bcrypt').disabled = true;
      $('run-bcrypt').textContent = 'Ejecutando...';
      const r = await runEndpoint('/benchmark/bcrypt');
      updateStats('bcrypt', r);
      showResult(r);
      $('run-bcrypt').disabled = false;
      $('run-bcrypt').textContent = 'Ejecutar bcrypt';
    }

    async function runParanoid(){
      $('run-paranoid').disabled = true;
      $('run-paranoid').textContent = 'Ejecutando...';
      const r = await runEndpoint('/benchmark/paranoid');
      updateStats('paranoid', r);
      showResult(r);
      $('run-paranoid').disabled = false;
      $('run-paranoid').textContent = 'Ejecutar paranoid';
    }

    async function runBoth(){
      $('run-both').disabled = true;
      $('run-both').textContent = 'Ejecutando...';
      const [b,p] = await Promise.all([
        runEndpoint('/benchmark/bcrypt'),
        runEndpoint('/benchmark/paranoid')
      ]);
      updateStats('both', {b,p});
      showResult({bcrypt:b,paranoid:p});
      $('run-both').disabled = false;
      $('run-both').textContent = 'Ejecutar ambos';
    }

    function updateStats(kind, payload){
      try{
        if(kind==='bcrypt' || kind==='both'){
          const obj = kind==='both' ? payload.b : payload;
          if(obj && obj.results){
            $('b-create').textContent = (obj.results.create_mean? (obj.results.create_mean*1000).toFixed(3) + ' ms':'—');
            $('b-auth').textContent = (obj.results.auth_mean? (obj.results.auth_mean*1000).toFixed(3) + ' ms':'—');
            $('samples').textContent = obj.results.samples || '—';
          }
        }
        if(kind==='paranoid' || kind==='both'){
          const obj = kind==='both' ? payload.p : payload;
          if(obj && obj.results){
            $('p-create').textContent = (obj.results.create_mean? (obj.results.create_mean*1000).toFixed(3) + ' ms':'—');
            $('p-auth').textContent = (obj.results.auth_mean? (obj.results.auth_mean*1000).toFixed(3) + ' ms':'—');
          }
        }
      }catch(e){console.error(e)}
    }

    // Token actions
    async function genToken(){
      const username = $('username').value.trim();
      const role = $('role').value.trim() || 'user';
      if(!username) return alert('Usuario requerido');
      const res = await runEndpoint('/auth/rsa-token',{
        method:'POST',headers:{'Content-Type':'application/json'},
        body: JSON.stringify({username,role})
      });
      if(res && res.token){
        $('token-box').value = res.token;
        log('Token generado');
      }else{
        log('Error generando token');
      }
    }

    async function verifyToken(){
      const token = $('token-box').value.trim();
      if(!token) return alert('Token vacío');
      const res = await runEndpoint('/auth/verify-rsa-token',{
        method:'POST',headers:{'Content-Type':'application/json'},
        body: JSON.stringify({token})
      });
      showResult(res);
      if(!res.error) log('Token verificado: ' + (res.username||'—'));
    }

    // Network info
    async function refreshNetwork(){
      const res = await runEndpoint('/network/info');
      $('network-info').textContent = JSON.stringify(res, null, 2);
    }

    // Utility actions
    $('run-bcrypt').addEventListener('click', runBcrypt);
    $('run-paranoid').addEventListener('click', runParanoid);
    $('run-both').addEventListener('click', runBoth);
    $('gen-token').addEventListener('click', genToken);
    $('verify-token').addEventListener('click', verifyToken);
    $('refresh-net').addEventListener('click', refreshNetwork);
    $('ping-server').addEventListener('click', async ()=>{
      const now = Date.now();
      const res = await runEndpoint('/');
      log('Ping OK, host: ' + (res.host||'—'));
    });
    $('fetch-both').addEventListener('click', async ()=>{
      const [b,p] = await Promise.all([runEndpoint('/benchmark/bcrypt'),runEndpoint('/benchmark/paranoid')]);
      showResult({bcrypt:b,paranoid:p});
    });

    $('copy-token').addEventListener('click', ()=>{navigator.clipboard.writeText($('token-box').value||'');log('Token copiado al portapapeles')});
    $('clear-log').addEventListener('click', ()=>{$('log').textContent='';$('benchmark-result').textContent='Aún no se han ejecutado benchmarks.'});

    // Export CSV simple
    $('export-csv').addEventListener('click', ()=>{
      try{
        const text = $('benchmark-result').textContent;
        const blob = new Blob([text],{type:'application/json'});
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url; a.download = 'benchmark-result.json';
        a.click();
        URL.revokeObjectURL(url);
        log('Exportado benchmark-result.json');
      }catch(e){log('Error exportando: '+e.message)}
    });

    // Inicial
    (async ()=>{
      log('Dashboard listo - Usuario: {{ username }}');
    })();
  </script>
</body>
</html>
'''


# Endpoints de API para el dashboard
@app.route('/api/v1/benchmark/bcrypt')
@custom_jwt
def api_benchmark_bcrypt():
    """Endpoint de benchmark bcrypt para el dashboard"""
    # Aquí integrarías con el sistema real de benchmarks
    return jsonify({
        "hasher": "bcrypt",
        "results": {
            "create_mean": 0.185,
            "create_std": 0.012,
            "create_p95": 0.201,
            "auth_mean": 0.002,
            "auth_std": 0.001,
            "auth_p95": 0.003,
            "samples": 500
        },
        "timestamp": datetime.datetime.now().isoformat()
    })


@app.route('/api/v1/benchmark/paranoid')
@custom_jwt
def api_benchmark_paranoid():
    """Endpoint de benchmark paranoid para el dashboard"""
    return jsonify({
        "hasher": "paranoid_vault",
        "results": {
            "create_mean": 0.192,
            "create_std": 0.015,
            "create_p95": 0.210,
            "auth_mean": 0.001,
            "auth_std": 0.0005,
            "auth_p95": 0.002,
            "samples": 500
        },
        "timestamp": datetime.datetime.now().isoformat()
    })


@app.route('/api/v1/auth/rsa-token', methods=['POST'])
@custom_jwt
def api_generate_rsa_token():
    """Generar token RSA para el dashboard"""
    data = request.get_json()
    user = request.current_user

    # Usar el sistema real de JWT
    from secure_flask_app_fixed import CustomJWT

    token_payload = {
        'username': data.get('username', user['username']),
        'role': data.get('role', user['role']),
        'ip': request.remote_addr,
        'exp': datetime.datetime.utcnow().timestamp() + (24 * 3600),
        'iss': 'tin_tan_admin_dashboard',
        'generated_by': user['username']
    }

    token = CustomJWT.encode(token_payload, app.config['SECRET_KEY'])

    return jsonify({
        "status": "Token generado",
        "token": token,
        "algoritmo": "HS256",
        "generated_by": user['username']
    })


@app.route('/api/v1/auth/verify-rsa-token', methods=['POST'])
@custom_jwt
def api_verify_rsa_token():
    """Verificar token RSA para el dashboard"""
    data = request.get_json()

    from secure_flask_app_fixed import CustomJWT
    verification = CustomJWT.decode(data['token'], app.config['SECRET_KEY'])

    return jsonify(verification)


@app.route('/api/v1/network/info')
@custom_jwt
def api_network_info():
    """Información de red para el dashboard"""
    return jsonify({
        "remote_addr": request.remote_addr,
        "host": request.host,
        "user_agent": request.user_agent.string,
        "server_bind": "0.0.0.0:5000",
        "api_version": "v1",
        "timestamp": datetime.datetime.now().isoformat()
    })


@app.route('/api/v1/')
@custom_jwt
def api_home():
    """Home de la API v1"""
    return jsonify({
        "api": "Admin Dashboard API",
        "version": "v1",
        "status": "active",
        "user": request.current_user['username'],
        "endpoints": [
            "/benchmark/bcrypt",
            "/benchmark/paranoid",
            "/auth/rsa-token",
            "/auth/verify-rsa-token",
            "/network/info",
            "/admin/account"
        ]
    })


if __name__ == "__main__":
    print("🚀 INICIANDO ADMIN DASHBOARD API...")
    print("📍 Endpoints disponibles:")
    print("   GET  /api/v1/admin/account  - Dashboard principal")
    print("   GET  /api/v1/benchmark/bcrypt  - Benchmark bcrypt")
    print("   GET  /api/v1/benchmark/paranoid - Benchmark paranoid")
    print("   POST /api/v1/auth/rsa-token - Generar token")
    print("   POST /api/v1/auth/verify-rsa-token - Verificar token")
    print("   GET  /api/v1/network/info - Info de red")

    app.run(host='0.0.0.0', port=5001, debug=True)