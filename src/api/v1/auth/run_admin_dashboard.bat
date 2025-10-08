@echo off
chcp 65001 >nul

echo 🚀 INICIANDO ADMIN DASHBOARD...

:: Crear directorio de templates
if not exist templates mkdir templates

:: Guardar template corregido (usar redirección con cuidado en Windows)
(
  echo ^<!doctype html^>
  echo ^<html lang="es"^>
  echo ^<head^>
  echo   ^<meta charset="utf-8" /^>
  echo   ^<meta name="viewport" content="width=device-width,initial-scale=1" /^>
  echo   ^<title^>Admin Dashboard — Benchmarks ^& Auth^</title^>
  echo   ^<style^>
  echo     :root{--bg:#0f172a;--card:#0b1220;--muted:#94a3b8;--accent:#60a5fa;--success:#10b981}
  echo     *{box-sizing:border-box}
  echo     body{margin:0;font-family:Inter,system-ui,-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Helvetica,Arial,sans-serif;background:linear-gradient(180deg,#071026 0%%,#071935 100%%);color:#e6eef8}
  echo     .container{max-width:1100px;margin:28px auto;padding:20px}
  echo     header{display:flex;align-items:center;justify-content:space-between}
  echo     h1{margin:0;font-size:20px}
  echo     .grid{display:grid;grid-template-columns:1fr 360px;gap:18px;margin-top:18px}
  echo     .card{background:var(--card);padding:14px;border-radius:12px;box-shadow:0 6px 18px rgba(2,6,23,.6)}
  echo     .small{font-size:13px;color:var(--muted)}
  echo     button{background:var(--accent);border:none;color:#06203a;padding:8px 12px;border-radius:8px;cursor:pointer}
  echo     .muted{color:var(--muted)}
  echo     .row{display:flex;gap:10px;align-items:center}
  echo     label{display:block;font-size:13px;margin-bottom:6px;color:var(--muted)}
  echo     input[type=text],select,textarea{width:100%%;padding:8px;border-radius:8px;border:1px solid rgba(255,255,255,.04);background:#071428;color:inherit}
  echo     .result{font-family:monospace;background:#031022;padding:10px;border-radius:8px;overflow:auto;max-height:220px}
  echo     .stat{display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px dashed rgba(255,255,255,.03)}
  echo     .actions{display:flex;gap:8px}
  echo     .endpoint-list{display:flex;flex-direction:column;gap:8px}
  echo     .chip{background:rgba(255,255,255,.03);padding:6px 10px;border-radius:999px;font-size:12px}
  echo     .footer{margin-top:18px;color:var(--muted);font-size:13px;text-align:center}
  echo     .ok{color:var(--success)}
  echo   ^</style^>
  echo ^</head^>
  echo ^<body^>
  echo   ^<div class="container"^>
  echo     ^<header^>
  echo       ^<h1^>Admin Dashboard — Benchmarks ^& Auth^</h1^>
  echo       ^<div class="small"^>Conectado como: ^<span class="chip"^>{{ username }}^</span^> ^| API: ^<span class="chip"^>{{ api_version }}^</span^>^</div^>
  echo     ^</header^>
  echo     ^<!-- Resto del template corregido -->
  echo   ^</div^>
  echo ^</body^>
  echo ^</html^>
) > templates\admin_dashboard.html

echo ✅ Template guardado en templates\admin_dashboard.html

:: Ejecutar aplicación
python admin_dashboard_integration.py
pause
