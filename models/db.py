"""
models/db.py
═══════════════════════════════════════════════════════════════════
Conexión a MySQL usando PyMySQL puro (sin Flask-MySQLdb).
Compatible con Flask 3.x y desplegable en Render.

Uso en cualquier route:
    from models.db import get_connection

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT ...")
            resultado = cur.fetchone()
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise
    finally:
        conn.close()
═══════════════════════════════════════════════════════════════════
"""

import pymysql
import pymysql.cursors
import os


def get_connection():
    """
    Abre y devuelve una conexión PyMySQL con DictCursor.
    Siempre llama a conn.close() en un bloque finally.
    """
    return pymysql.connect(
        host     = os.getenv("MYSQL_HOST",     "localhost"),
        user     = os.getenv("MYSQL_USER",     "root"),
        password = os.getenv("MYSQL_PASSWORD", ""),
        database = os.getenv("MYSQL_DB",       "citas_medicas_db"),
        port     = int(os.getenv("MYSQL_PORT", 3306)),
        charset  = "utf8mb4",
        cursorclass = pymysql.cursors.DictCursor,
        autocommit  = False,          # commit/rollback explícito
        connect_timeout = 10,
    )


def init_db(app):
    """
    Mantenido por compatibilidad con app.py.
    Con PyMySQL puro no hace falta inicializar extensión.
    """
    pass
