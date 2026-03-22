"""
routes/paciente.py — Panel del paciente. PyMySQL puro.
"""
from flask import (Blueprint, render_template, request,
                   redirect, url_for, flash, session, current_app)
from models.db import get_connection
from routes.auth import paciente_required
from datetime import date

paciente_bp = Blueprint('paciente_bp', __name__, url_prefix='/paciente')


@paciente_bp.route('/')
@paciente_required
def panel():
    cedula = session.get('paciente_cedula')

    if not cedula:
        flash('Tu perfil de paciente aún no está completo. Contacta al administrador.', 'warning')
        return render_template('panel_paciente.html',
                               citas_activas=[], citas_historial=[], paciente=None)

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT p.*, u.correo AS correo_usuario
                FROM pacientes p
                JOIN usuarios u ON u.id = p.id_usuario
                WHERE p.cedula = %s AND p.activo = 1
            """, (cedula,))
            paciente = cur.fetchone()

            cur.execute("""
                SELECT c.id, c.tipo_cita, c.fecha, c.hora,
                       c.eps, c.direccion_eps, c.estado,
                       m.nombre AS medico, m.especialidad
                FROM citas c
                JOIN medicos m ON m.id = c.id_medico
                WHERE c.cedula_paciente = %s
                  AND c.estado IN ('Pendiente','Confirmada')
                ORDER BY c.fecha ASC, c.hora ASC
            """, (cedula,))
            citas_activas = cur.fetchall()

            cur.execute("""
                SELECT c.id, c.tipo_cita, c.fecha, c.hora,
                       c.estado, m.nombre AS medico
                FROM citas c
                JOIN medicos m ON m.id = c.id_medico
                WHERE c.cedula_paciente = %s
                  AND c.estado IN ('Cancelada','Completada')
                ORDER BY c.fecha DESC LIMIT 10
            """, (cedula,))
            citas_historial = cur.fetchall()

    except Exception as e:
        flash(f'Error al cargar tus citas: {e}', 'danger')
        citas_activas, citas_historial, paciente = [], [], None
    finally:
        conn.close()

    return render_template('panel_paciente.html',
                           citas_activas=citas_activas,
                           citas_historial=citas_historial,
                           paciente=paciente)


@paciente_bp.route('/nueva-cita', methods=['GET', 'POST'])
@paciente_required
def nueva_cita():
    cedula = session.get('paciente_cedula')
    if not cedula:
        flash('Tu perfil no tiene cédula registrada.', 'danger')
        return redirect(url_for('paciente_bp.panel'))

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, nombre, especialidad FROM medicos "
                "WHERE activo=1 ORDER BY especialidad, nombre"
            )
            medicos = cur.fetchall()
    except Exception:
        medicos = []
    finally:
        conn.close()

    if request.method == 'POST':
        id_medico = request.form.get('medico',   '').strip()
        tipo      = request.form.get('tipoCita', '').strip()
        fecha     = request.form.get('fechaCita','').strip()
        hora      = request.form.get('horaCita', '').strip()
        eps_key   = request.form.get('eps',      '').strip()

        errores = []
        if not id_medico: errores.append('Selecciona un médico.')
        if not tipo:      errores.append('Selecciona el tipo de cita.')
        if not fecha:     errores.append('Selecciona la fecha.')
        if not hora:      errores.append('Selecciona la hora.')
        if not eps_key:   errores.append('Selecciona tu EPS.')
        if fecha:
            try:
                if date.fromisoformat(fecha) < date.today():
                    errores.append('La fecha no puede ser en el pasado.')
            except ValueError:
                errores.append('Fecha inválida.')

        if errores:
            for e in errores:
                flash(e, 'danger')
            return render_template('nueva_cita_paciente.html', medicos=medicos)

        conn2 = get_connection()
        try:
            with conn2.cursor() as cur:
                cur.execute(
                    "SELECT id FROM citas WHERE id_medico=%s AND fecha=%s "
                    "AND hora=%s AND estado NOT IN ('Cancelada')",
                    (id_medico, fecha, hora)
                )
                if cur.fetchone():
                    flash('Ese médico ya tiene una cita a esa hora. Elige otro horario.', 'danger')
                    return render_template('nueva_cita_paciente.html', medicos=medicos)

                direccion = current_app.config['EPS_DIRECCIONES'].get(eps_key, '')
                cur.execute(
                    "INSERT INTO citas "
                    "(cedula_paciente, id_medico, tipo_cita, fecha, hora, eps, direccion_eps, estado) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, 'Confirmada')",
                    (cedula, id_medico, tipo, fecha, hora, eps_key, direccion)
                )
            conn2.commit()
            flash('¡Cita reservada exitosamente!', 'success')
            return redirect(url_for('paciente_bp.panel'))
        except Exception as e:
            conn2.rollback()
            flash(f'Error al guardar la cita: {e}', 'danger')
        finally:
            conn2.close()

    return render_template('nueva_cita_paciente.html', medicos=medicos)


@paciente_bp.route('/cancelar/<int:id_cita>', methods=['POST'])
@paciente_required
def cancelar_cita(id_cita):
    cedula = session.get('paciente_cedula')
    if not cedula:
        flash('No se pudo identificar tu perfil.', 'danger')
        return redirect(url_for('paciente_bp.panel'))

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM citas WHERE id=%s AND cedula_paciente=%s",
                (id_cita, cedula)
            )
            if not cur.fetchone():
                flash('No tienes permiso para cancelar esa cita.', 'danger')
                return redirect(url_for('paciente_bp.panel'))
            cur.execute("UPDATE citas SET estado='Cancelada' WHERE id=%s", (id_cita,))
        conn.commit()
        flash('Cita cancelada correctamente.', 'info')
    except Exception as e:
        conn.rollback()
        flash(f'Error al cancelar: {e}', 'danger')
    finally:
        conn.close()

    return redirect(url_for('paciente_bp.panel'))
