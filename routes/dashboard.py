"""
routes/dashboard.py — Panel admin. PyMySQL puro.
"""
from flask import Blueprint, render_template, flash, redirect, url_for, request
from models.db import get_connection
from routes.auth import admin_required
from datetime import date

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


@dashboard_bp.route('/')
@admin_required
def panel():
    stats, citas_hoy, ultimos_pacientes = {}, [], []
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            hoy = date.today().isoformat()

            cur.execute("SELECT COUNT(*) AS t FROM pacientes WHERE activo=1")
            stats['total_pacientes'] = cur.fetchone()['t']

            cur.execute(
                "SELECT COUNT(*) AS t FROM citas WHERE fecha=%s AND estado!='Cancelada'", (hoy,)
            )
            stats['citas_hoy'] = cur.fetchone()['t']

            cur.execute("SELECT COUNT(*) AS t FROM citas WHERE estado='Pendiente'")
            stats['pendientes'] = cur.fetchone()['t']

            cur.execute("SELECT COUNT(*) AS t FROM medicos WHERE activo=1")
            stats['total_medicos'] = cur.fetchone()['t']

            cur.execute("SELECT COUNT(*) AS t FROM usuarios WHERE activo=1")
            stats['total_usuarios'] = cur.fetchone()['t']

            cur.execute("""
                SELECT c.id,
                       CONCAT(p.nombre,' ',p.apellido) AS paciente,
                       p.cedula, m.nombre AS medico,
                       c.tipo_cita, c.hora, c.estado
                FROM citas c
                JOIN pacientes p ON p.cedula = c.cedula_paciente
                JOIN medicos   m ON m.id     = c.id_medico
                WHERE c.fecha = %s
                ORDER BY c.hora ASC LIMIT 20
            """, (hoy,))
            citas_hoy = cur.fetchall()

            cur.execute("""
                SELECT p.cedula, p.nombre, p.apellido, p.eps,
                       p.fecha_registro, u.correo
                FROM pacientes p
                LEFT JOIN usuarios u ON u.id = p.id_usuario
                WHERE p.activo=1
                ORDER BY p.fecha_registro DESC LIMIT 8
            """)
            ultimos_pacientes = cur.fetchall()

    except Exception as e:
        flash(f'Error al cargar el panel: {e}', 'danger')
    finally:
        conn.close()

    return render_template('dashboard.html',
                           stats=stats,
                           citas_hoy=citas_hoy,
                           ultimos_pacientes=ultimos_pacientes,
                           seccion='panel')


@dashboard_bp.route('/usuarios')
@admin_required
def usuarios():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT u.id, u.nombre, u.correo, u.rol,
                       u.activo, u.fecha_registro,
                       p.cedula AS paciente_cedula
                FROM usuarios u
                LEFT JOIN pacientes p ON p.id_usuario = u.id
                ORDER BY u.fecha_registro DESC
            """)
            usuarios = cur.fetchall()
    except Exception as e:
        flash(f'Error: {e}', 'danger')
        usuarios = []
    finally:
        conn.close()
    return render_template('dashboard.html', usuarios=usuarios, seccion='usuarios')


@dashboard_bp.route('/usuarios/desactivar/<int:uid>', methods=['POST'])
@admin_required
def desactivar_usuario(uid):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("UPDATE usuarios SET activo=0 WHERE id=%s", (uid,))
        conn.commit()
        flash('Usuario desactivado.', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error: {e}', 'danger')
    finally:
        conn.close()
    return redirect(url_for('dashboard.usuarios'))


@dashboard_bp.route('/citas')
@admin_required
def citas():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT c.id, c.cedula_paciente,
                       CONCAT(p.nombre,' ',p.apellido) AS paciente,
                       m.nombre AS medico,
                       c.tipo_cita, c.fecha, c.hora, c.eps, c.estado
                FROM citas c
                JOIN pacientes p ON p.cedula = c.cedula_paciente
                JOIN medicos   m ON m.id     = c.id_medico
                ORDER BY c.fecha DESC, c.hora DESC LIMIT 100
            """)
            citas = cur.fetchall()
    except Exception as e:
        flash(f'Error: {e}', 'danger')
        citas = []
    finally:
        conn.close()
    return render_template('dashboard.html', citas=citas, seccion='citas')


@dashboard_bp.route('/pacientes')
@admin_required
def pacientes():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT p.cedula, p.nombre, p.apellido,
                       p.telefono, p.correo, p.eps,
                       p.fecha_registro, p.activo
                FROM pacientes p
                WHERE p.activo=1
                ORDER BY p.fecha_registro DESC
            """)
            pacientes = cur.fetchall()
    except Exception as e:
        flash(f'Error: {e}', 'danger')
        pacientes = []
    finally:
        conn.close()
    return render_template('dashboard.html', pacientes=pacientes, seccion='pacientes')
