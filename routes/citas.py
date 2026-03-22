"""
routes/citas.py — CRUD de citas (solo admin). PyMySQL puro.
"""
from flask import (Blueprint, render_template, request,
                   redirect, url_for, flash, jsonify, current_app)
from models.db import get_connection
from routes.auth import admin_required
from datetime import date

citas_bp = Blueprint('citas', __name__, url_prefix='/citas')


# ── API JSON ──────────────────────────────────────────────────────
@citas_bp.route('/api/<cedula>')
def api_cita(cedula):
    cita = _buscar_cita_activa(cedula)
    if not cita:
        return jsonify({'error': 'Sin cita activa'}), 404
    cita_json = dict(cita)
    for campo in ('fecha', 'hora', 'fecha_reserva'):
        if cita_json.get(campo):
            cita_json[campo] = str(cita_json[campo])
    return jsonify({'ok': True, 'cita': cita_json})


# ── RESERVAR ──────────────────────────────────────────────────────
@citas_bp.route('/reservar', methods=['GET', 'POST'])
@admin_required
def reservar():
    medicos = _get_medicos()
    if request.method == 'GET':
        return render_template('reservar_cita.html', medicos=medicos)

    cedula  = request.form.get('docPaciente', '').strip()
    id_med  = request.form.get('medico',      '').strip()
    tipo    = request.form.get('tipoCita',    '').strip()
    fecha   = request.form.get('fechaCita',   '').strip()
    hora    = request.form.get('horaCita',    '').strip()
    eps_key = request.form.get('epsReserva',  '').strip()

    errores = []
    if not cedula:  errores.append('Ingresa el documento.')
    if not id_med:  errores.append('Selecciona médico.')
    if not tipo:    errores.append('Selecciona tipo de cita.')
    if not fecha:   errores.append('Selecciona la fecha.')
    if not hora:    errores.append('Selecciona la hora.')
    if not eps_key: errores.append('Selecciona la EPS.')
    if fecha:
        try:
            if date.fromisoformat(fecha) < date.today():
                errores.append('La fecha no puede ser en el pasado.')
        except ValueError:
            errores.append('Fecha inválida.')

    if errores:
        for e in errores:
            flash(e, 'danger')
        return render_template('reservar_cita.html', medicos=medicos, form=request.form)

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM pacientes WHERE cedula=%s AND activo=1", (cedula,))
            if not cur.fetchone():
                flash('No existe paciente con esa cédula.', 'danger')
                return render_template('reservar_cita.html', medicos=medicos, form=request.form)

            cur.execute(
                "SELECT id FROM citas WHERE id_medico=%s AND fecha=%s "
                "AND hora=%s AND estado!='Cancelada'",
                (id_med, fecha, hora)
            )
            if cur.fetchone():
                flash('Ese médico ya tiene cita en esa fecha y hora.', 'danger')
                return render_template('reservar_cita.html', medicos=medicos, form=request.form)

            direccion = current_app.config['EPS_DIRECCIONES'].get(eps_key, '')
            cur.execute(
                "INSERT INTO citas "
                "(cedula_paciente, id_medico, tipo_cita, fecha, hora, eps, direccion_eps, estado) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,'Confirmada')",
                (cedula, id_med, tipo, fecha, hora, eps_key, direccion)
            )
            id_nueva = cur.lastrowid
        conn.commit()
        flash(f'¡Cita #{id_nueva} reservada!', 'success')
        return redirect(url_for('citas.reservar'))
    except Exception as e:
        conn.rollback()
        flash(f'Error: {e}', 'danger')
        return render_template('reservar_cita.html', medicos=medicos, form=request.form)
    finally:
        conn.close()


# ── CONSULTAR ─────────────────────────────────────────────────────
@citas_bp.route('/consultar', methods=['GET', 'POST'])
@admin_required
def consultar():
    cita, cedula_buscada = None, ''
    if request.method == 'POST':
        cedula_buscada = request.form.get('docConsulta', '').strip()
        if not cedula_buscada:
            flash('Ingresa el documento.', 'danger')
        else:
            conn = get_connection()
            try:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT c.id, c.cedula_paciente,
                               p.nombre, p.apellido,
                               m.nombre AS medico, m.especialidad,
                               c.tipo_cita, c.fecha, c.hora,
                               c.eps, c.direccion_eps, c.estado
                        FROM citas c
                        JOIN pacientes p ON p.cedula = c.cedula_paciente
                        JOIN medicos   m ON m.id     = c.id_medico
                        WHERE c.cedula_paciente = %s
                          AND c.estado NOT IN ('Cancelada','Completada')
                        ORDER BY c.fecha ASC LIMIT 1
                    """, (cedula_buscada,))
                    cita = cur.fetchone()
                if not cita:
                    flash('Sin cita activa para ese documento.', 'warning')
            except Exception as e:
                flash(f'Error: {e}', 'danger')
            finally:
                conn.close()
    return render_template('consultar_cita.html', cita=cita, cedula=cedula_buscada)


# ── ACTUALIZAR ────────────────────────────────────────────────────
@citas_bp.route('/actualizar', methods=['GET', 'POST'])
@admin_required
def actualizar():
    medicos = _get_medicos()
    cita_actual, cedula_buscada = None, ''

    if request.method == 'GET' and request.args.get('cedula'):
        cedula_buscada = request.args.get('cedula', '').strip()
        cita_actual = _buscar_cita_activa(cedula_buscada)
        if not cita_actual:
            flash('Sin cita activa para ese documento.', 'warning')

    if request.method == 'POST':
        accion = request.form.get('accion', '')

        if accion == 'buscar':
            cedula_buscada = request.form.get('docActualizar', '').strip()
            cita_actual = _buscar_cita_activa(cedula_buscada)
            if not cita_actual:
                flash('Sin cita activa.', 'warning')
            return render_template('actualizar_cita.html',
                                   medicos=medicos, cita=cita_actual, cedula=cedula_buscada)

        if accion == 'actualizar':
            id_cita = request.form.get('id_cita',    '').strip()
            id_med  = request.form.get('nuevoMedico','').strip()
            tipo    = request.form.get('nuevoTipo',  '').strip()
            nueva_f = request.form.get('nuevaFecha', '').strip()
            nueva_h = request.form.get('nuevaHora',  '').strip()

            errores = []
            if not id_med:  errores.append('Selecciona médico.')
            if not tipo:    errores.append('Selecciona tipo.')
            if not nueva_f: errores.append('Selecciona fecha.')
            if not nueva_h: errores.append('Selecciona hora.')
            if nueva_f:
                try:
                    if date.fromisoformat(nueva_f) < date.today():
                        errores.append('La fecha no puede ser en el pasado.')
                except ValueError:
                    errores.append('Fecha inválida.')

            if errores:
                for e in errores:
                    flash(e, 'danger')
                cita_actual = _buscar_cita_por_id(id_cita)
                return render_template('actualizar_cita.html',
                                       medicos=medicos, cita=cita_actual,
                                       cedula=cita_actual['cedula_paciente'] if cita_actual else '')

            conn = get_connection()
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        "UPDATE citas SET id_medico=%s, tipo_cita=%s, fecha=%s, hora=%s "
                        "WHERE id=%s",
                        (id_med, tipo, nueva_f, nueva_h, id_cita)
                    )
                conn.commit()
                flash('¡Cita actualizada!', 'success')
                return redirect(url_for('citas.actualizar'))
            except Exception as e:
                conn.rollback()
                flash(f'Error: {e}', 'danger')
            finally:
                conn.close()

    return render_template('actualizar_cita.html',
                           medicos=medicos, cita=cita_actual, cedula=cedula_buscada)


# ── CANCELAR ──────────────────────────────────────────────────────
@citas_bp.route('/cancelar/<int:id_cita>', methods=['POST'])
@admin_required
def cancelar(id_cita):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("UPDATE citas SET estado='Cancelada' WHERE id=%s", (id_cita,))
        conn.commit()
        flash('Cita cancelada.', 'info')
    except Exception as e:
        conn.rollback()
        flash(f'Error: {e}', 'danger')
    finally:
        conn.close()
    return redirect(url_for('citas.consultar'))


# ══════════════════════════════════════════════════════════════════
#  HELPERS PRIVADOS
# ══════════════════════════════════════════════════════════════════

def _get_medicos():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, nombre, especialidad FROM medicos "
                "WHERE activo=1 ORDER BY especialidad, nombre"
            )
            return cur.fetchall()
    except Exception:
        return []
    finally:
        conn.close()


def _buscar_cita_activa(cedula):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT c.id, c.cedula_paciente,
                       p.nombre, p.apellido,
                       m.id AS id_medico, m.nombre AS medico, m.especialidad,
                       c.tipo_cita, c.fecha, c.hora, c.eps, c.direccion_eps, c.estado
                FROM citas c
                JOIN pacientes p ON p.cedula = c.cedula_paciente
                JOIN medicos   m ON m.id     = c.id_medico
                WHERE c.cedula_paciente = %s
                  AND c.estado NOT IN ('Cancelada','Completada')
                ORDER BY c.fecha ASC LIMIT 1
            """, (cedula,))
            return cur.fetchone()
    except Exception:
        return None
    finally:
        conn.close()


def _buscar_cita_por_id(id_cita):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT c.*, p.nombre, p.apellido,
                       m.nombre AS medico, m.especialidad
                FROM citas c
                JOIN pacientes p ON p.cedula = c.cedula_paciente
                JOIN medicos   m ON m.id     = c.id_medico
                WHERE c.id = %s
            """, (id_cita,))
            return cur.fetchone()
    except Exception:
        return None
    finally:
        conn.close()
