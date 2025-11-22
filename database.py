import mysql.connector
from mysql.connector import Error
import os

class Database:
    def __init__(self):
        # Configuración para PlanetScale - solo variables de entorno
        self.host = os.getenv('DATABASE_HOST')
        self.database = os.getenv('DATABASE')  
        self.user = os.getenv('DATABASE_USERNAME')
        self.password = os.getenv('DATABASE_PASSWORD')
    
    def get_connection(self):
        try:
            connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                ssl_ca='/etc/ssl/certs/ca-certificates.crt',
                ssl_verify_cert=True
            )
            return connection
        except Error as e:
            print(f"Error conectando a PlanetScale: {e}")
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