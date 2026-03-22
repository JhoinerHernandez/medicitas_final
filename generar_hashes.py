"""
generar_hashes.py
═══════════════════════════════════════════════════════════════════
Script utilitario para generar hashes seguros de contraseñas.

Ejecutar UNA SOLA VEZ después de importar database.sql:
    python generar_hashes.py

Luego copia los comandos SQL que imprime y ejecútalos en MySQL.
═══════════════════════════════════════════════════════════════════
"""
from werkzeug.security import generate_password_hash

print("=" * 65)
print("  MediCitas — Generador de Hashes de Contraseñas")
print("=" * 65)

# Contraseñas por defecto
usuarios = [
    ("admin@medicitas.co",    "Admin123*",    "Administrador"),
    ("paciente@ejemplo.co",   "Paciente123*", "Paciente de ejemplo"),
]

print("\n📋 Copia y ejecuta en MySQL:\n")
print("USE citas_medicas_db;")
for correo, password, descripcion in usuarios:
    h = generate_password_hash(password)
    print(f"\n-- {descripcion}: {correo} / {password}")
    print(f"UPDATE usuarios SET password_hash = '{h}'")
    print(f"  WHERE correo = '{correo}';")

print("\n" + "=" * 65)
print("\n💡 Para agregar tu propio admin:")
print()
correo_nuevo = input("Correo del nuevo admin: ").strip()
if correo_nuevo:
    nombre  = input("Nombre: ").strip()
    pw      = input("Contraseña: ").strip()
    h       = generate_password_hash(pw)
    print(f"\nEjecuta en MySQL:")
    print(f"INSERT INTO usuarios (nombre, correo, password_hash, rol)")
    print(f"VALUES ('{nombre}', '{correo_nuevo}', '{h}', 'admin');")
else:
    print("(Omitido)")

print("\n✅ Listo.\n")
