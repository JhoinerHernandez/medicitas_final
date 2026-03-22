# 🏥 MediCitas v2.0 — Sistema de Citas con Autenticación y Roles

Flask + MySQL + Autenticación completa con dos roles: **admin** y **paciente**.

---

## 📁 Estructura del Proyecto

```
MediCitas/
├── app.py                        ← Punto de entrada Flask
├── config.py                     ← Configuración MySQL, claves
├── database.sql                  ← Script SQL (tablas + datos iniciales)
├── requirements.txt
├── .env.example
│
├── models/
│   └── db.py                     ← Conexión MySQL
│
├── routes/
│   ├── auth.py           ← LOGIN / LOGOUT / REGISTRO + decoradores
│   ├── paciente.py       ← PANEL PACIENTE (solo rol=paciente)
│   ├── dashboard.py      ← PANEL ADMIN   (solo rol=admin)
│   ├── citas.py          ← CRUD citas    (solo rol=admin)
│   └── pacientes.py      ← CRUD pacientes (solo rol=admin)
│
├── templates/
│   ├── base.html                 ← Layout con navbar dinámica
│   ├── login.html                ← Página de inicio de sesión
│   ├── register.html             ← Registro de nuevos pacientes
│   ├── panel_paciente.html       ← Dashboard del paciente
│   ├── nueva_cita_paciente.html  ← Formulario nueva cita (paciente)
│   ├── dashboard.html            ← Panel admin (citas, usuarios, pacientes)
│   ├── reservar_cita.html        ← Reservar cita (admin)
│   ├── consultar_cita.html       ← Consultar cita (admin)
│   ├── actualizar_cita.html      ← Actualizar cita (admin)
│   ├── registro_paciente.html    ← Registro paciente (admin)
│   ├── index.html                ← Página pública
│   └── error.html                ← Páginas 404/500
│
└── static/
    ├── css/styles.css
    └── js/scripts.js
```

---

## 🚀 Instalación Paso a Paso

### 1. Descomprimir y entrar a la carpeta

```bash
cd MediCitas
```

### 2. Activar entorno virtual (usa el que ya tienes)

```bash
# Windows
venv\Scripts\activate

# Linux / Mac
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Crear la base de datos

```bash
mysql -u root -p < database.sql
```

O abre MySQL Workbench y ejecuta el contenido de `database.sql`.

### 5. Configurar contraseña de MySQL

Edita `config.py` línea:
```python
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'TU_CONTRASEÑA_AQUI')
```

O crea un archivo `.env`:
```
MYSQL_PASSWORD=tu_contraseña
SECRET_KEY=clave_secreta_segura
```

### 6. ⚠️ IMPORTANTE: Regenerar hashes de contraseñas

El archivo `database.sql` incluye hashes, pero por seguridad **debes regenerarlos**.

Ejecuta este script Python una sola vez:

```bash
python3 generar_hashes.py
```

O manualmente en Python:
```python
from werkzeug.security import generate_password_hash

hash_admin    = generate_password_hash('Admin123*')
hash_paciente = generate_password_hash('Paciente123*')

print("Admin hash:   ", hash_admin)
print("Paciente hash:", hash_paciente)
```

Luego en MySQL:
```sql
USE citas_medicas_db;
UPDATE usuarios SET password_hash = 'HASH_GENERADO' WHERE correo = 'admin@medicitas.co';
UPDATE usuarios SET password_hash = 'HASH_GENERADO' WHERE correo = 'paciente@ejemplo.co';
```

### 7. Ejecutar la aplicación

```bash
python app.py
```

Accede en: **http://localhost:5000**

---

## 🔑 Credenciales por Defecto

| Rol | Correo | Contraseña | Panel |
|-----|--------|-----------|-------|
| **Admin** | admin@medicitas.co | Admin123* | /dashboard/ |
| **Paciente** | paciente@ejemplo.co | Paciente123* | /paciente/ |

---

## 🔐 Sistema de Roles

### Decoradores de seguridad (`routes/auth.py`)

```python
from routes.auth import login_required, admin_required, paciente_required

# Requiere sesión activa (cualquier rol)
@login_required
def mi_vista():
    ...

# Solo admins — redirige a /paciente si no es admin
@admin_required
def vista_admin():
    ...

# Solo pacientes — redirige a /dashboard si no es paciente
@paciente_required
def vista_paciente():
    ...
```

### Flujo de autenticación

```
GET /          → Redirige según sesión
  ├── Sin sesión   → /login
  ├── rol=admin    → /dashboard/
  └── rol=paciente → /paciente/

POST /login    → Verifica credenciales en tabla usuarios
  ├── Éxito admin    → /dashboard/
  └── Éxito paciente → /paciente/

GET /logout    → Limpia sesión → /login
GET /register  → Formulario de registro
POST /register → Crea usuario (rol=paciente) + paciente en BD
```

### Variables de sesión

```python
session['user_id']         # ID del usuario
session['user_nombre']     # Nombre completo
session['user_correo']     # Correo/email
session['user_rol']        # 'admin' o 'paciente'
session['paciente_cedula'] # Cédula (solo si rol=paciente)
```

### Context processor en templates

En todos los templates Jinja2 está disponible `current_user`:

```html
{{ current_user.nombre }}        <!-- Nombre del usuario -->
{{ current_user.rol }}           <!-- 'admin' o 'paciente' -->
{{ current_user.is_auth }}       <!-- True si hay sesión -->
{{ current_user.is_admin }}      <!-- True si es admin -->

{% if current_user.is_admin %}
  <!-- Solo visible para admins -->
{% endif %}
```

---

## 🌐 Rutas del Sistema

| Método | Ruta | Acceso | Descripción |
|--------|------|--------|-------------|
| GET | `/` | Público | Redirige según rol |
| GET/POST | `/login` | Público | Login |
| GET | `/logout` | Auth | Cerrar sesión |
| GET/POST | `/register` | Público | Registro de paciente |
| GET | `/paciente/` | Paciente | Panel del paciente |
| GET/POST | `/paciente/nueva-cita` | Paciente | Crear cita |
| POST | `/paciente/cancelar/<id>` | Paciente | Cancelar propia cita |
| GET | `/dashboard/` | Admin | Panel general |
| GET | `/dashboard/usuarios` | Admin | Gestión de usuarios |
| GET | `/dashboard/citas` | Admin | Todas las citas |
| GET | `/dashboard/pacientes` | Admin | Todos los pacientes |
| POST | `/dashboard/usuarios/desactivar/<id>` | Admin | Desactivar usuario |
| GET/POST | `/citas/reservar` | Admin | Reservar cita |
| GET/POST | `/citas/consultar` | Admin | Consultar cita |
| GET/POST | `/citas/actualizar` | Admin | Actualizar cita |
| POST | `/citas/cancelar/<id>` | Admin | Cancelar cita |
| GET | `/citas/api/<cedula>` | Público | API JSON |
| GET/POST | `/pacientes/registrar` | Admin | Registrar paciente |
| GET | `/pacientes/<cedula>` | Público | API JSON paciente |

---

## 🗄️ Base de Datos

### Tabla `usuarios` (NUEVA)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | INT PK | Auto incremental |
| nombre | VARCHAR(100) | Nombre completo |
| correo | VARCHAR(150) UNIQUE | Email (login) |
| password_hash | VARCHAR(512) | Hash werkzeug |
| rol | ENUM | 'admin' o 'paciente' |
| activo | TINYINT | 1=activo, 0=inactivo |
| fecha_registro | DATETIME | Automático |

### Tabla `pacientes` (MODIFICADA)

Se agregó el campo `id_usuario` (FK → usuarios.id) para vincular el registro clínico con el usuario del sistema.

---

## ✅ Qué cambió respecto a la v1

| Elemento | v1 | v2 |
|----------|----|----|
| Login | ❌ No existía | ✅ /login con sesiones Flask |
| Roles | ❌ No existía | ✅ admin / paciente |
| Panel paciente | ❌ No existía | ✅ /paciente/ completo |
| Protección rutas | ❌ No existía | ✅ Decoradores auth |
| Registro | ❌ Manual BD | ✅ /register automático |
| Tabla usuarios | ❌ No existía | ✅ Con password_hash |
| Navbar dinámica | ❌ Estática | ✅ Según rol y sesión |
| Panel admin | ✅ Básico | ✅ + Gestión de usuarios |
