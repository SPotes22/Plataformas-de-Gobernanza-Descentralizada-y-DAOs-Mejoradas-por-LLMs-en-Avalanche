'''
microNAS - Servidor de Archivos Básico en Red
Copyright (C) 2025 Santiago Potes Giraldo
SPDX-License-Identifier: GPL-3.0-or-later

Este archivo es parte de microNAS.

microNAS is free software: you can redistribute it and/or modify
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

from flask import Flask, request, redirect, url_for, send_from_directory, render_template_string
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from flask_bcrypt import Bcrypt
import os

secret = os.environ.get("MASTER_DEV_KEY")
admin_user = os.environ.get("admin_pass")
client_user = os.environ.get('client_pass')

app = Flask(__name__)
app.secret_key = secret
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

UPLOAD_FOLDER = './cuarentena'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# USUARIOS DE PRUEBA (puedes cargar desde archivo después)
usuarios = {
    'admin': {'password': bcrypt.generate_password_hash(admin_user).decode('utf-8'), 'rol': 'administrator'},
    'cliente': {'password': bcrypt.generate_password_hash(client_user).decode('utf-8'), 'rol': 'cliente'},
    'usuario': {'password': bcrypt.generate_password_hash('usuario123').decode('utf-8'), 'rol': 'usuario'},
}

# MODELO DE USUARIO
class Usuario(UserMixin):
    def __init__(self, username):
        self.id = username
        self.rol = usuarios[username]['rol']

@login_manager.user_loader
def load_user(user_id):
    if user_id in usuarios:
        return Usuario(user_id)
    return None

# LOGIN
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['usuario']
        password = request.form['clave']
        if user in usuarios and bcrypt.check_password_hash(usuarios[user]['password'], password):
            login_user(Usuario(user))
            return redirect(url_for('inicio'))
        return 'Credenciales inválidas'
    return render_template("login.html")


# CERRAR SESIÓN
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# PÁGINA PRINCIPAL
@app.route('/inicio')
@login_required
def inicio():
    return render_template('inicio.html', current_user=current_user)

# SUBIR ARCHIVOS
@app.route('/subir', methods=['GET', 'POST'])
@login_required
def subir():
    if current_user.rol == 'usuario':
        return 'No tienes permiso para subir archivos'
    if request.method == 'POST':
        archivo = request.files['archivo']
        archivo.save(os.path.join(UPLOAD_FOLDER, secure_filename(archivo.filename)))
        return 'Archivo subido'
    return render_template("subir.html")


# LISTAR ARCHIVOS
@app.route('/listar')
@login_required
def listar():
    archivos = os.listdir(UPLOAD_FOLDER)
    enlaces = ''.join(f'<li><a href="/descargar/{f}">{f}</a></li>' for f in archivos)
    return render_template("listar.html", archivos=archivos )

@app.route('/dashboard')
@login_required
def listar():
    archivos = os.listdir(UPLOAD_FOLDER)
    enlaces = ''.join(f'<li><a href="/descargar/{f}">{f}</a></li>' for f in archivos)
    return render_template("listar_UI_update.html", archivos=archivos )



# DESCARGAR ARCHIVO
@app.route('/descargar/<nombre>')
@login_required
def descargar(nombre):
    return send_from_directory(UPLOAD_FOLDER, nombre)

# ELIMINAR ARCHIVOS (solo admin)
@app.route('/eliminar', methods=['GET', 'POST'])
@login_required
def eliminar():
    if current_user.rol != 'administrator':
        return 'No tienes permiso para eliminar archivos'
    if request.method == 'POST':
        archivo = request.form['archivo']
        try:
            os.remove(os.path.join(UPLOAD_FOLDER, archivo))
            return f'{archivo} eliminado'
        except:
            return 'Error al eliminar'
    archivos = os.listdir(UPLOAD_FOLDER)
    opciones = ''.join(f'<option value="{f}">{f}</option>' for f in archivos)
    return f'''
    <form method="post">
        <select name="archivo">{opciones}</select>
        <input type="submit" value="Eliminar">
    </form><a href="/inicio">Volver</a>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
