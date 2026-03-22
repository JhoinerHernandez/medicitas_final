-- ================================================================
--  MediCitas v2.0 — Script SQL COMPLETO CON AUTENTICACIÓN Y ROLES
--  Base de datos: citas_medicas_db
--
--  EJECUTAR: mysql -u root -p < database.sql
-- ================================================================

CREATE DATABASE IF NOT EXISTS citas_medicas_db
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE citas_medicas_db;

-- ── Tabla: usuarios ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS usuarios (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    nombre         VARCHAR(100) NOT NULL,
    correo         VARCHAR(150) NOT NULL UNIQUE,
    password_hash  VARCHAR(512) NOT NULL,
    rol            ENUM('admin','paciente') NOT NULL DEFAULT 'paciente',
    activo         TINYINT(1)   NOT NULL DEFAULT 1,
    fecha_registro DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ── Tabla: pacientes ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS pacientes (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    cedula         VARCHAR(20)  NOT NULL UNIQUE,
    nombre         VARCHAR(80)  NOT NULL,
    apellido       VARCHAR(80)  NOT NULL,
    telefono       VARCHAR(20),
    correo         VARCHAR(150) NOT NULL UNIQUE,
    eps            VARCHAR(60)  NOT NULL,
    id_usuario     INT          DEFAULT NULL,
    fecha_registro DATETIME     DEFAULT CURRENT_TIMESTAMP,
    activo         TINYINT(1)   DEFAULT 1,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ── Tabla: medicos ───────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS medicos (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    nombre       VARCHAR(120) NOT NULL,
    especialidad VARCHAR(80)  NOT NULL,
    activo       TINYINT(1)   DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ── Tabla: citas ─────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS citas (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    cedula_paciente VARCHAR(20)  NOT NULL,
    id_medico       INT          NOT NULL,
    tipo_cita       ENUM('General','Odontología','Especialista','Control','Urgencias') NOT NULL,
    fecha           DATE         NOT NULL,
    hora            TIME         NOT NULL,
    eps             VARCHAR(60)  NOT NULL,
    direccion_eps   VARCHAR(200),
    estado          ENUM('Pendiente','Confirmada','Cancelada','Completada') DEFAULT 'Pendiente',
    fecha_reserva   DATETIME     DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cedula_paciente) REFERENCES pacientes(cedula) ON UPDATE CASCADE,
    FOREIGN KEY (id_medico)       REFERENCES medicos(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ── Médicos iniciales ─────────────────────────────────────────────
INSERT INTO medicos (nombre, especialidad) VALUES
('Dr. Cesar Aguas',     'Medicina General'),
('Dra. Heidi Paba',     'Medicina General'),
('Dr. Jeanpool',        'Medicina General'),
('Dra. Sandra Guerra',  'Odontología'),
('Dr. Fabian Florian',  'Odontología'),
('Dr. Johan Hernandez', 'Cardiología'),
('Dra. Samara Taborda', 'Pediatría'),
('Dr. Jhon Majanrresz', 'Ortopedia'),
('Dra. Yesica Perez',   'Ginecología')
ON DUPLICATE KEY UPDATE nombre = nombre;

-- ── Usuario ADMIN por defecto ────────────────────────────────────
-- Correo:     admin@medicitas.co
-- Contraseña: Admin123*
-- (hash generado con werkzeug.security.generate_password_hash)
INSERT INTO usuarios (nombre, correo, password_hash, rol) VALUES
('Administrador MediCitas', 'admin@medicitas.co',
 'scrypt:32768:8:1$ZV6aQgQaCElJKQoq$c49265904e4e9c4753d8a6c79f0fe3144f9632cc1d7da8e44ea944ec54bad96265525ae242c31def4532597c47746a5b25adc68a75318fd54632900ea5026789',
 'admin')
ON DUPLICATE KEY UPDATE correo = correo;

-- ── Usuario PACIENTE de ejemplo ──────────────────────────────────
-- Correo:     paciente@ejemplo.co
-- Contraseña: Paciente123*
INSERT INTO usuarios (nombre, correo, password_hash, rol) VALUES
('Juan Pérez', 'paciente@ejemplo.co',
 'scrypt:32768:8:1$ZV6aQgQaCElJKQoq$c49265904e4e9c4753d8a6c79f0fe3144f9632cc1d7da8e44ea944ec54bad96265525ae242c31def4532597c47746a5b25adc68a75318fd54632900ea5026789',
 'paciente')
ON DUPLICATE KEY UPDATE correo = correo;

-- ── Paciente de ejemplo vinculado al usuario ──────────────────────
INSERT INTO pacientes (cedula, nombre, apellido, telefono, correo, eps, id_usuario)
SELECT '1000000001','Juan','Pérez','3001234567','paciente@ejemplo.co','sura', id
FROM usuarios WHERE correo = 'paciente@ejemplo.co'
ON DUPLICATE KEY UPDATE cedula = cedula;
