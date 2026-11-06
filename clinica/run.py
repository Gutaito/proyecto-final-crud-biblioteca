import os
from datetime import datetime

from flask import (
    Flask, render_template, request,
    redirect, url_for, flash
)
from mysql.connector import Error, IntegrityError

from db import create_connection


app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "clave-desarrollo-clinica")


def obtener_conexion():
    connection = create_connection()

    if connection is None:
        raise RuntimeError("No se pudo conectar con la base de datos.")

    return connection


@app.route("/")
def index():
    connection = obtener_conexion()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM pacientes ORDER BY apellido, nombre")
        pacientes = cursor.fetchall()

        cursor.execute("SELECT COUNT(*) AS total FROM pacientes")
        total_pacientes = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM medicos")
        total_medicos = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM turnos")
        total_turnos = cursor.fetchone()["total"]

        return render_template(
            "index.html",
            pacientes=pacientes,
            total_pacientes=total_pacientes,
            total_medicos=total_medicos,
            total_turnos=total_turnos
        )
    finally:
        cursor.close()
        connection.close()


# ---------------- PACIENTES ----------------

@app.route("/pacientes/add", methods=["GET", "POST"])
def add_patient():
    if request.method == "POST":
        datos = (
            request.form["dni"].strip(),
            request.form["nombre"].strip(),
            request.form["apellido"].strip(),
            request.form.get("fecha_nacimiento") or None,
            request.form.get("telefono", "").strip(),
            request.form.get("email", "").strip()
        )

        connection = obtener_conexion()
        cursor = connection.cursor()

        try:
            cursor.execute("""
                INSERT INTO pacientes
                (dni, nombre, apellido, fecha_nacimiento, telefono, email)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, datos)

            connection.commit()
            flash("Paciente registrado correctamente.", "success")
            return redirect(url_for("index"))

        except IntegrityError:
            connection.rollback()
            flash("Ya existe un paciente registrado con ese DNI.", "error")

        except Error as error:
            connection.rollback()
            flash(f"Error al registrar el paciente: {error}", "error")

        finally:
            cursor.close()
            connection.close()

    return render_template("paciente_form.html", paciente=None)


@app.route("/pacientes/edit/<int:id>", methods=["GET", "POST"])
def edit_patient(id):
    connection = obtener_conexion()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM pacientes WHERE id = %s", (id,))
        paciente = cursor.fetchone()

        if paciente is None:
            flash("El paciente no existe.", "error")
            return redirect(url_for("index"))

        if request.method == "POST":
            datos = (
                request.form["dni"].strip(),
                request.form["nombre"].strip(),
                request.form["apellido"].strip(),
                request.form.get("fecha_nacimiento") or None,
                request.form.get("telefono", "").strip(),
                request.form.get("email", "").strip(),
                id
            )

            cursor.execute("""
                UPDATE pacientes
                SET dni=%s, nombre=%s, apellido=%s,
                    fecha_nacimiento=%s, telefono=%s, email=%s
                WHERE id=%s
            """, datos)

            connection.commit()
            flash("Paciente actualizado correctamente.", "success")
            return redirect(url_for("index"))

        return render_template("paciente_form.html", paciente=paciente)

    except IntegrityError:
        connection.rollback()
        flash("El DNI ingresado ya pertenece a otro paciente.", "error")
        return redirect(url_for("edit_patient", id=id))

    finally:
        cursor.close()
        connection.close()


@app.route("/pacientes/delete/<int:id>", methods=["POST"])
def delete_patient(id):
    connection = obtener_conexion()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "SELECT COUNT(*) FROM turnos WHERE paciente_id = %s",
            (id,)
        )

        if cursor.fetchone()[0] > 0:
            flash("No se puede eliminar: el paciente tiene turnos registrados.", "error")
        else:
            cursor.execute("DELETE FROM pacientes WHERE id = %s", (id,))
            connection.commit()
            flash("Paciente eliminado correctamente.", "success")

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for("index"))


# ---------------- MEDICOS ----------------

@app.route("/medicos")
def medicos():
    connection = obtener_conexion()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT m.*, e.nombre AS especialidad
            FROM medicos m
            INNER JOIN especialidades e ON m.especialidad_id = e.id
            ORDER BY m.apellido, m.nombre
        """)

        lista_medicos = cursor.fetchall()
        return render_template("medicos.html", medicos=lista_medicos)

    finally:
        cursor.close()
        connection.close()


@app.route("/medicos/add", methods=["GET", "POST"])
def add_medico():
    connection = obtener_conexion()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM especialidades ORDER BY nombre")
        especialidades = cursor.fetchall()

        if request.method == "POST":
            datos = (
                request.form["nombre"].strip(),
                request.form["apellido"].strip(),
                request.form["matricula"].strip(),
                request.form.get("telefono", "").strip(),
                request.form.get("email", "").strip(),
                request.form["especialidad_id"]
            )

            cursor.execute("""
                INSERT INTO medicos
                (nombre, apellido, matricula, telefono, email, especialidad_id)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, datos)

            connection.commit()
            flash("Médico registrado correctamente.", "success")
            return redirect(url_for("medicos"))

        return render_template(
            "medico_form.html",
            medico=None,
            especialidades=especialidades
        )

    except IntegrityError:
        connection.rollback()
        flash("La matrícula ingresada ya está registrada.", "error")
        return redirect(url_for("add_medico"))

    finally:
        cursor.close()
        connection.close()


@app.route("/medicos/edit/<int:id>", methods=["GET", "POST"])
def edit_medico(id):
    connection = obtener_conexion()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM medicos WHERE id = %s", (id,))
        medico = cursor.fetchone()

        if medico is None:
            flash("El médico no existe.", "error")
            return redirect(url_for("medicos"))

        cursor.execute("SELECT * FROM especialidades ORDER BY nombre")
        especialidades = cursor.fetchall()

        if request.method == "POST":
            cursor.execute("""
                UPDATE medicos
                SET nombre=%s, apellido=%s, matricula=%s,
                    telefono=%s, email=%s, especialidad_id=%s
                WHERE id=%s
            """, (
                request.form["nombre"].strip(),
                request.form["apellido"].strip(),
                request.form["matricula"].strip(),
                request.form.get("telefono", "").strip(),
                request.form.get("email", "").strip(),
                request.form["especialidad_id"],
                id
            ))

            connection.commit()
            flash("Médico actualizado correctamente.", "success")
            return redirect(url_for("medicos"))

        return render_template(
            "medico_form.html",
            medico=medico,
            especialidades=especialidades
        )

    except IntegrityError:
        connection.rollback()
        flash("La matrícula ingresada ya está registrada.", "error")
        return redirect(url_for("edit_medico", id=id))

    finally:
        cursor.close()
        connection.close()


@app.route("/medicos/delete/<int:id>", methods=["POST"])
def delete_medico(id):
    connection = obtener_conexion()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "SELECT COUNT(*) FROM turnos WHERE medico_id = %s",
            (id,)
        )

        if cursor.fetchone()[0] > 0:
            flash("No se puede eliminar: el médico tiene turnos registrados.", "error")
        else:
            cursor.execute("DELETE FROM medicos WHERE id = %s", (id,))
            connection.commit()
            flash("Médico eliminado correctamente.", "success")

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for("medicos"))


# ---------------- ESPECIALIDADES ----------------

@app.route("/especialidades")
def especialidades():
    connection = obtener_conexion()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT e.*, COUNT(m.id) AS cantidad_medicos
            FROM especialidades e
            LEFT JOIN medicos m ON e.id = m.especialidad_id
            GROUP BY e.id
            ORDER BY e.nombre
        """)

        lista = cursor.fetchall()
        return render_template("especialidades.html", especialidades=lista)

    finally:
        cursor.close()
        connection.close()


@app.route("/especialidades/add", methods=["GET", "POST"])
def add_especialidad():
    if request.method == "POST":
        connection = obtener_conexion()
        cursor = connection.cursor()

        try:
            cursor.execute("""
                INSERT INTO especialidades (nombre, descripcion)
                VALUES (%s, %s)
            """, (
                request.form["nombre"].strip(),
                request.form.get("descripcion", "").strip()
            ))

            connection.commit()
            flash("Especialidad agregada correctamente.", "success")
            return redirect(url_for("especialidades"))

        except IntegrityError:
            connection.rollback()
            flash("Esa especialidad ya existe.", "error")

        finally:
            cursor.close()
            connection.close()

    return render_template("especialidad_form.html", especialidad=None)


@app.route("/especialidades/edit/<int:id>", methods=["GET", "POST"])
def edit_especialidad(id):
    connection = obtener_conexion()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM especialidades WHERE id = %s", (id,))
        especialidad = cursor.fetchone()

        if especialidad is None:
            flash("La especialidad no existe.", "error")
            return redirect(url_for("especialidades"))

        if request.method == "POST":
            cursor.execute("""
                UPDATE especialidades
                SET nombre=%s, descripcion=%s
                WHERE id=%s
            """, (
                request.form["nombre"].strip(),
                request.form.get("descripcion", "").strip(),
                id
            ))

            connection.commit()
            flash("Especialidad actualizada correctamente.", "success")
            return redirect(url_for("especialidades"))

        return render_template(
            "especialidad_form.html",
            especialidad=especialidad
        )

    except IntegrityError:
        connection.rollback()
        flash("Ya existe una especialidad con ese nombre.", "error")
        return redirect(url_for("edit_especialidad", id=id))

    finally:
        cursor.close()
        connection.close()


@app.route("/especialidades/delete/<int:id>", methods=["POST"])
def delete_especialidad(id):
    connection = obtener_conexion()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "SELECT COUNT(*) FROM medicos WHERE especialidad_id = %s",
            (id,)
        )

        if cursor.fetchone()[0] > 0:
            flash("No se puede eliminar: hay médicos asociados.", "error")
        else:
            cursor.execute("DELETE FROM especialidades WHERE id = %s", (id,))
            connection.commit()
            flash("Especialidad eliminada correctamente.", "success")

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for("especialidades"))


# ---------------- TURNOS ----------------

@app.route("/turnos")
def turnos():
    connection = obtener_conexion()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT t.*, 
                   p.nombre AS paciente_nombre,
                   p.apellido AS paciente_apellido,
                   m.nombre AS medico_nombre,
                   m.apellido AS medico_apellido,
                   e.nombre AS especialidad
            FROM turnos t
            INNER JOIN pacientes p ON t.paciente_id = p.id
            INNER JOIN medicos m ON t.medico_id = m.id
            INNER JOIN especialidades e ON m.especialidad_id = e.id
            ORDER BY t.fecha DESC, t.hora DESC
        """)

        lista = cursor.fetchall()
        return render_template("turnos.html", turnos=lista)

    finally:
        cursor.close()
        connection.close()


@app.route("/turnos/add", methods=["GET", "POST"])
def add_turno():
    connection = obtener_conexion()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM pacientes ORDER BY apellido, nombre")
        pacientes = cursor.fetchall()

        cursor.execute("""
            SELECT m.id, m.nombre, m.apellido, e.nombre AS especialidad
            FROM medicos m
            INNER JOIN especialidades e ON m.especialidad_id = e.id
            ORDER BY m.apellido, m.nombre
        """)
        medicos = cursor.fetchall()

        if request.method == "POST":
            cursor.execute("""
                INSERT INTO turnos (paciente_id, medico_id, fecha, hora)
                VALUES (%s, %s, %s, %s)
            """, (
                request.form["paciente_id"],
                request.form["medico_id"],
                request.form["fecha"],
                request.form["hora"]
            ))

            connection.commit()
            flash("Turno registrado correctamente.", "success")
            return redirect(url_for("turnos"))

        return render_template(
            "turno_form.html",
            pacientes=pacientes,
            medicos=medicos
        )

    except IntegrityError:
        connection.rollback()
        flash("Ese horario ya está ocupado para el médico o el paciente.", "error")
        return redirect(url_for("add_turno"))

    except Error as error:
        connection.rollback()
        flash(f"No se pudo registrar el turno: {error}", "error")
        return redirect(url_for("add_turno"))

    finally:
        cursor.close()
        connection.close()


@app.route("/turnos/estado/<int:id>", methods=["POST"])
def cambiar_estado_turno(id):
    estados_validos = ("pendiente", "confirmado", "cancelado", "completado")
    nuevo_estado = request.form.get("estado")

    if nuevo_estado not in estados_validos:
        flash("Estado de turno no válido.", "error")
        return redirect(url_for("turnos"))

    connection = obtener_conexion()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "UPDATE turnos SET estado = %s WHERE id = %s",
            (nuevo_estado, id)
        )
        connection.commit()
        flash("Estado del turno actualizado.", "success")

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for("turnos"))


# ---------------- CONSULTAS ----------------

@app.route("/consultas")
def consultas():
    connection = obtener_conexion()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT c.*, t.fecha, t.hora,
                   p.nombre AS paciente_nombre,
                   p.apellido AS paciente_apellido,
                   m.nombre AS medico_nombre,
                   m.apellido AS medico_apellido
            FROM consultas c
            INNER JOIN turnos t ON c.turno_id = t.id
            INNER JOIN pacientes p ON t.paciente_id = p.id
            INNER JOIN medicos m ON t.medico_id = m.id
            ORDER BY c.fecha_consulta DESC
        """)

        lista = cursor.fetchall()
        return render_template("consultas.html", consultas=lista)

    finally:
        cursor.close()
        connection.close()


@app.route("/consultas/add", methods=["GET", "POST"])
def add_consulta():
    connection = obtener_conexion()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT t.id, t.fecha, t.hora,
                   p.nombre AS paciente_nombre,
                   p.apellido AS paciente_apellido,
                   m.nombre AS medico_nombre,
                   m.apellido AS medico_apellido
            FROM turnos t
            INNER JOIN pacientes p ON t.paciente_id = p.id
            INNER JOIN medicos m ON t.medico_id = m.id
            LEFT JOIN consultas c ON t.id = c.turno_id
            WHERE t.estado = 'completado' AND c.id IS NULL
            ORDER BY t.fecha DESC, t.hora DESC
        """)

        turnos_disponibles = cursor.fetchall()

        if request.method == "POST":
            cursor.execute("""
                INSERT INTO consultas (turno_id, observaciones)
                VALUES (%s, %s)
            """, (
                request.form["turno_id"],
                request.form.get("observaciones", "").strip()
            ))

            connection.commit()
            flash("Consulta médica registrada correctamente.", "success")
            return redirect(url_for("consultas"))

        return render_template(
            "consulta_form.html",
            turnos=turnos_disponibles
        )

    except IntegrityError:
        connection.rollback()
        flash("Ese turno ya tiene una consulta registrada.", "error")
        return redirect(url_for("add_consulta"))

    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
