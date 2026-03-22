"""
app.py — MediCitas con PyMySQL puro (Flask 3 compatible)
Listo para Render.com
"""
from flask import Flask, render_template, redirect, url_for, session
from config import Config
from models.db import init_db

from routes.auth      import auth_bp
from routes.paciente  import paciente_bp
from routes.dashboard import dashboard_bp
from routes.citas     import citas_bp
from routes.pacientes import pacientes_bp


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    init_db(app)  # no-op con PyMySQL puro, mantiene compatibilidad

    app.register_blueprint(auth_bp)
    app.register_blueprint(paciente_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(citas_bp)
    app.register_blueprint(pacientes_bp)

    @app.route('/')
    def index():
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return redirect(url_for('dashboard.panel') if session.get('user_rol') == 'admin'
                        else url_for('paciente_bp.panel'))

    @app.errorhandler(404)
    def not_found(e):
        return render_template('error.html', codigo=404, mensaje='Página no encontrada'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('error.html', codigo=500, mensaje='Error interno del servidor'), 500

    # ── Filtros Jinja2 ────────────────────────────────────────────
    @app.template_filter('fecha_es')
    def fecha_es(value):
        if not value:
            return '-'
        try:
            from datetime import date
            if isinstance(value, str):
                value = date.fromisoformat(value)
            meses = ['enero','febrero','marzo','abril','mayo','junio',
                     'julio','agosto','septiembre','octubre','noviembre','diciembre']
            dias  = ['lunes','martes','miércoles','jueves','viernes','sábado','domingo']
            return f"{dias[value.weekday()].capitalize()} {value.day} de {meses[value.month-1]} de {value.year}"
        except Exception:
            return str(value)

    @app.template_filter('hora_fmt')
    def hora_fmt(value):
        if not value:
            return '-'
        try:
            from datetime import timedelta
            if isinstance(value, timedelta):
                total = int(value.total_seconds())
                h, m = total // 3600, (total % 3600) // 60
            else:
                partes = str(value).split(':')
                h, m = int(partes[0]), int(partes[1])
            ampm = 'AM' if h < 12 else 'PM'
            h12  = h if h <= 12 else h - 12
            h12  = 12 if h12 == 0 else h12
            return f"{h12:02d}:{m:02d} {ampm}"
        except Exception:
            return str(value)

    @app.context_processor
    def inject_user():
        return {
            'current_user': {
                'id':       session.get('user_id'),
                'nombre':   session.get('user_nombre', ''),
                'correo':   session.get('user_correo', ''),
                'rol':      session.get('user_rol', ''),
                'is_auth':  'user_id' in session,
                'is_admin': session.get('user_rol') == 'admin',
            }
        }

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
