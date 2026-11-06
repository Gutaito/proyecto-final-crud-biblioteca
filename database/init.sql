CREATE DATABASE IF NOT EXISTS clinica
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE clinica;

CREATE TABLE IF NOT EXISTS especialidades (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    descripcion TEXT
);

CREATE TABLE IF NOT EXISTS medicos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    matricula VARCHAR(50) NOT NULL UNIQUE,
    telefono VARCHAR(30),
    email VARCHAR(120),
    especialidad_id INT NOT NULL,
    CONSTRAINT fk_medicos_especialidades
        FOREIGN KEY (especialidad_id)
        REFERENCES especialidades(id)
);

CREATE TABLE IF NOT EXISTS pacientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    dni VARCHAR(20) NOT NULL UNIQUE,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    fecha_nacimiento DATE,
    telefono VARCHAR(30),
    email VARCHAR(120)
);

CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre_usuario VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    rol ENUM('administrador', 'recepcionista', 'medico')
        NOT NULL DEFAULT 'recepcionista',
    activo BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS turnos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    paciente_id INT NOT NULL,
    medico_id INT NOT NULL,
    fecha DATE NOT NULL,
    hora TIME NOT NULL,
    estado ENUM(
        'pendiente',
        'confirmado',
        'cancelado',
        'completado'
    ) NOT NULL DEFAULT 'pendiente',
    CONSTRAINT fk_turnos_pacientes
        FOREIGN KEY (paciente_id) REFERENCES pacientes(id),
    CONSTRAINT fk_turnos_medicos
        FOREIGN KEY (medico_id) REFERENCES medicos(id),
    CONSTRAINT uq_turno_medico_fecha_hora
        UNIQUE (medico_id, fecha, hora),
    CONSTRAINT uq_turno_paciente_fecha_hora
        UNIQUE (paciente_id, fecha, hora)
);

CREATE TABLE IF NOT EXISTS consultas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    turno_id INT NOT NULL UNIQUE,
    fecha_consulta DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    observaciones TEXT,
    CONSTRAINT fk_consultas_turnos
        FOREIGN KEY (turno_id) REFERENCES turnos(id)
);

INSERT IGNORE INTO especialidades (nombre, descripcion) VALUES
('Clínica médica', 'Atención médica general'),
('Cardiología', 'Especialidad del corazón y sistema circulatorio'),
('Pediatría', 'Atención médica infantil'),
('Dermatología', 'Especialidad de la piel'),
('Traumatología', 'Especialidad del sistema musculoesquelético');
