"""
routes/pacientes.py — Gestión de pacientes (solo admin). PyMySQL puro.
"""
from flask import (Blueprint, render_template, request,
                   redirect, url_for, flash, jsonify)
from werkzeug.security import generate_password_hash
from models.db import get_connection
from routes.auth import admin_required

pacientes_bp = Blueprint('pacientes', __name__, url_prefix='/pacientes')


@pacientes_bp.route('/<cedula>', methods=['GET'])
def obtener_paciente(cedula):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT cedula, nombre, apellido, telefono, correo, eps "
                "FROM pacientes WHERE cedula=%s AND activo=1",
                (cedula,)
            )
            p = cur.fetchone()
        if not p:
            return jsonify({'error': 'Paciente no encontrado'}), 404
        return jsonify({'ok': True, 'paciente': p})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


@pacientes_bp.route('/registrar', methods=['GET', 'POST'])
@admin_required
def registrar():
    if request.method == 'GET':
        return render_template('registro_paciente.html')

    cedula   = request.form.get('cedula',   '').strip()
    nombre   = request.form.get('nombre',   '').strip()
    apellido = request.form.get('apellido', '').strip()
    telefono = request.form.get('telefono', '').strip()
    correo   = request.form.get('correo',   '').strip().lower()
    eps      = request.form.get('eps',      '').strip()

    errores = []
    if not cedula or not cedula.isdigit(): errores.append('Cédula numérica requerida.')
    if len(nombre) < 2:   errores.append('Nombre requerido.')
    if len(apellido) < 2: errores.append('Apellido requerido.')
    if '@' not in correo: errores.append('Correo inválido.')
    if not eps:           errores.append('Selecciona EPS.')

    if errores:
        for e in errores:
            flash(e, 'danger')
        return render_template('registro_paciente.html', form=request.form)

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            hash_pw = generate_password_hash(f"Paciente{cedula}*")
            cur.execute(
                "INSERT INTO usuarios (nombre, correo, password_hash, rol) "
                "VALUES (%s, %s, %s, 'paciente')",
                (f"{nombre} {apellido}", correo, hash_pw)
            )
            id_usuario = cur.lastrowid
            cur.execute(
                "INSERT INTO pacientes "
                "(cedula, nombre, apellido, telefono, correo, eps, id_usuario) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s)",
                (cedula, nombre, apellido, telefono, correo, eps, id_usuario)
            )
        conn.commit()
        flash(
            f'Paciente {nombre} {apellido} registrado. '
            f'Contraseña temporal: Paciente{cedula}*',
            'success'
        )
        return redirect(url_for('pacientes.registrar'))
    except Exception as e:
        conn.rollback()
        err = str(e)
        if 'correo' in err:
            flash('Ese correo ya está registrado.', 'danger')
        elif 'cedula' in err:
            flash('Esa cédula ya está registrada.', 'danger')
        else:
            flash(f'Error: {err}', 'danger')
        return render_template('registro_paciente.html', form=request.form)
    finally:
        conn.close()


@pacientes_bp.route('/lista')
@admin_required
def lista():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM pacientes WHERE activo=1 ORDER BY fecha_registro DESC")
            pacientes = cur.fetchall()
        return render_template('dashboard.html', pacientes=pacientes, seccion='pacientes')
    except Exception as e:
        flash(f'Error: {e}', 'danger')
        return redirect(url_for('dashboard.panel'))
    finally:
        conn.close()
