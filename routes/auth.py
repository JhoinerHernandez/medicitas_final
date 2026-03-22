"""
routes/auth.py — Autenticación y decoradores de seguridad (PyMySQL puro)
"""
from functools import wraps
from flask import (Blueprint, render_template, request,
                   redirect, url_for, flash, session)
from werkzeug.security import generate_password_hash, check_password_hash
from models.db import get_connection

auth_bp = Blueprint('auth', __name__)


# ══════════════════════════════════════════════════════════════════
#  DECORADORES
# ══════════════════════════════════════════════════════════════════

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Debes iniciar sesión para acceder.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Debes iniciar sesión.', 'warning')
            return redirect(url_for('auth.login'))
        if session.get('user_rol') != 'admin':
            flash('No tienes permiso para acceder a esa sección.', 'danger')
            return redirect(url_for('paciente_bp.panel'))
        return f(*args, **kwargs)
    return decorated


def paciente_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Debes iniciar sesión.', 'warning')
            return redirect(url_for('auth.login'))
        if session.get('user_rol') != 'paciente':
            flash('Esta sección es solo para pacientes.', 'danger')
            return redirect(url_for('dashboard.panel'))
        return f(*args, **kwargs)
    return decorated


# ══════════════════════════════════════════════════════════════════
#  LOGIN
# ══════════════════════════════════════════════════════════════════

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return _redirigir_por_rol(session.get('user_rol'))

    if request.method == 'POST':
        correo   = request.form.get('correo', '').strip().lower()
        password = request.form.get('password', '')

        if not correo or not password:
            flash('Completa todos los campos.', 'danger')
            return render_template('login.html')

        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, nombre, correo, password_hash, rol "
                    "FROM usuarios WHERE correo = %s AND activo = 1",
                    (correo,)
                )
                usuario = cur.fetchone()
        except Exception as e:
            flash(f'Error de conexión: {e}', 'danger')
            return render_template('login.html')
        finally:
            conn.close()

        if usuario and check_password_hash(usuario['password_hash'], password):
            session.permanent = True
            session['user_id']     = usuario['id']
            session['user_nombre'] = usuario['nombre']
            session['user_correo'] = usuario['correo']
            session['user_rol']    = usuario['rol']

            # Si es paciente, guardar su cédula
            if usuario['rol'] == 'paciente':
                conn2 = get_connection()
                try:
                    with conn2.cursor() as cur2:
                        cur2.execute(
                            "SELECT cedula FROM pacientes "
                            "WHERE id_usuario = %s AND activo = 1",
                            (usuario['id'],)
                        )
                        pac = cur2.fetchone()
                    session['paciente_cedula'] = pac['cedula'] if pac else None
                finally:
                    conn2.close()

            flash(f'¡Bienvenido/a, {usuario["nombre"]}!', 'success')
            return _redirigir_por_rol(usuario['rol'])
        else:
            flash('Correo o contraseña incorrectos.', 'danger')

    return render_template('login.html')


# ══════════════════════════════════════════════════════════════════
#  LOGOUT
# ══════════════════════════════════════════════════════════════════

@auth_bp.route('/logout')
def logout():
    nombre = session.get('user_nombre', '')
    session.clear()
    flash(f'Hasta pronto, {nombre}. Sesión cerrada correctamente.', 'info')
    return redirect(url_for('auth.login'))


# ══════════════════════════════════════════════════════════════════
#  REGISTRO DE PACIENTE
# ══════════════════════════════════════════════════════════════════

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return _redirigir_por_rol(session.get('user_rol'))

    if request.method == 'POST':
        nombre    = request.form.get('nombre',    '').strip()
        apellido  = request.form.get('apellido',  '').strip()
        cedula    = request.form.get('cedula',    '').strip()
        telefono  = request.form.get('telefono',  '').strip()
        correo    = request.form.get('correo',    '').strip().lower()
        eps       = request.form.get('eps',       '').strip()
        password  = request.form.get('password',  '')
        password2 = request.form.get('password2', '')

        errores = []
        if not nombre:                         errores.append('El nombre es obligatorio.')
        if not apellido:                       errores.append('El apellido es obligatorio.')
        if not cedula or not cedula.isdigit(): errores.append('La cédula debe ser numérica.')
        if not correo or '@' not in correo:    errores.append('Ingresa un correo válido.')
        if not eps:                            errores.append('Selecciona una EPS.')
        if len(password) < 8:                  errores.append('La contraseña debe tener al menos 8 caracteres.')
        if password != password2:              errores.append('Las contraseñas no coinciden.')

        if errores:
            for e in errores:
                flash(e, 'danger')
            return render_template('register.html', form=request.form)

        conn = get_connection()
        try:
            with conn.cursor() as cur:
                hash_pw = generate_password_hash(password)
                cur.execute(
                    "INSERT INTO usuarios (nombre, correo, password_hash, rol) "
                    "VALUES (%s, %s, %s, 'paciente')",
                    (f"{nombre} {apellido}", correo, hash_pw)
                )
                id_usuario = cur.lastrowid
                cur.execute(
                    "INSERT INTO pacientes "
                    "(cedula, nombre, apellido, telefono, correo, eps, id_usuario) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (cedula, nombre, apellido, telefono, correo, eps, id_usuario)
                )
            conn.commit()
            flash('¡Cuenta creada exitosamente! Ya puedes iniciar sesión.', 'success')
            return redirect(url_for('auth.login'))

        except Exception as e:
            conn.rollback()
            err = str(e)
            if 'correo' in err or 'Duplicate' in err and 'correo' in err:
                flash('Ese correo ya está registrado.', 'danger')
            elif 'cedula' in err:
                flash('Esa cédula ya está registrada.', 'danger')
            else:
                flash(f'Error al registrar: {err}', 'danger')
            return render_template('register.html', form=request.form)
        finally:
            conn.close()

    return render_template('register.html', form={})


# ══════════════════════════════════════════════════════════════════
#  HELPER
# ══════════════════════════════════════════════════════════════════

def _redirigir_por_rol(rol):
    if rol == 'admin':
        return redirect(url_for('dashboard.panel'))
    return redirect(url_for('paciente_bp.panel'))
