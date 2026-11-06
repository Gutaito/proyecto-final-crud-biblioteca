import os
import mysql.connector
from mysql.connector import Error


def create_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST", "db"),
            port=int(os.getenv("DB_PORT", "3306")),
            user=os.getenv("DB_USER", "pipper"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "clinica"),
            connection_timeout=10
        )

        if connection.is_connected():
            print("Conexión exitosa a MySQL")
            return connection

    except Error as error:
        print(f"Error al conectar con MySQL: {error}")

    return None
