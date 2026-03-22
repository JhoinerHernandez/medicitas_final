"""
config.py — Configuración global de MediCitas
"""
import os

class Config:
    # ── Clave secreta (CAMBIA esto en producción) ─────────────────
    SECRET_KEY = os.environ.get('SECRET_KEY', 'medicitas_secret_key_2024_CAMBIAR_EN_PRODUCCION')

    # ── MySQL ─────────────────────────────────────────────────────
    MYSQL_HOST      = os.environ.get('MYSQL_HOST',     'localhost')
    MYSQL_USER      = os.environ.get('MYSQL_USER',     'root')
    MYSQL_PASSWORD  = os.environ.get('MYSQL_PASSWORD', '')   # ← pon tu contraseña aquí
    MYSQL_DB        = os.environ.get('MYSQL_DB',       'citas_medicas_db')
    MYSQL_CURSORCLASS = 'DictCursor'

    # ── Sesión ────────────────────────────────────────────────────
    # Tiempo de vida de la sesión (30 minutos de inactividad)
    PERMANENT_SESSION_LIFETIME = 1800  # segundos

    # ── Directorios de EPS ────────────────────────────────────────
    EPS_DIRECCIONES = {
        'sura':       'Cra. 43A #5A-113, Medellín · Tel: (604) 369-9000',
        'sanitas':    'Av. 19 #103-73, Bogotá · Tel: (601) 648-1800',
        'nueva-eps':  'Cll. 26 #51-53, Bogotá · Tel: 018000-9100-33',
        'compensar':  'Av. Ciudad de Cali #51-66, Bogotá · Tel: (601) 395-9000',
        'coosalud':   'Cll. 30 #17-36, Cartagena · Tel: (605) 660-4444',
        'coomeva':    'Cra. 100 #11A-35, Cali · Tel: (602) 661-5961',
        'salud-total':'Cra. 14 #93-44, Bogotá · Tel: (601) 742-7000',
        'medimas':    'Av. El Dorado #68D-35, Bogotá · Tel: (601) 423-1990',
        'famisanar':  'Cll. 100 #19-61, Bogotá · Tel: (601) 742-4400',
    }

    DEBUG = os.environ.get('DEBUG', 'True') == 'True'
