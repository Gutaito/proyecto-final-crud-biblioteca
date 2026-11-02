import mysql.connector
from mysql.connector import Error

def create_connection():
    connection = None
    try:
        connection = mysql.connector.connect(
            host="localhost",      
            user="pipper",     
            password="1234",  
            database="biblioteca"  
        )
        if connection.is_connected():
            print("Conexión exitosa a la base de datos MySQL")
    except Error as e:
        print(f"Error al conectar a MySQL: {e}")
    
    return connection