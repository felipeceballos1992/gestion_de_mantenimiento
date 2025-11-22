import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()  # Carga las variables del archivo .env

class Database:
    def __init__(self):
        self.host = os.getenv('DB_HOST')
        self.database = os.getenv('DB_NAME')
        self.user = os.getenv('DB_USER')
        self.password = os.getenv('DB_PASSWORD')
    
    def get_connection(self):
        try:
            connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                ssl_ca="/etc/ssl/cert.pem"  # Necesario para PlanetScale
            )
            return connection
        except Error as e:
            print(f"Error conectando a MySQL: {e}")
            return None
    
    def execute_query(self, query, params=None):
        connection = self.get_connection()
        if connection:
            try:
                cursor = connection.cursor(dictionary=True)
                cursor.execute(query, params or ())
                
                if query.strip().upper().startswith('SELECT'):
                    result = cursor.fetchall()
                else:
                    connection.commit()
                    result = cursor.lastrowid
                
                cursor.close()
                connection.close()
                return result
            except Error as e:
                print(f"Error ejecutando query: {e}")
                return None
        return None