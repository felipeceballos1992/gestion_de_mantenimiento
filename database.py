import psycopg2
from psycopg2 import Error
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        self.host = os.getenv('DATABASE_HOST')
        self.port = os.getenv('DATABASE_PORT')
        self.database = os.getenv('DATABASE_NAME')
        self.user = os.getenv('DATABASE_USERNAME')
        self.password = os.getenv('DATABASE_PASSWORD')
    
    def get_connection(self):
        try:
            connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password,
                sslmode="require"
            )
            return connection
        except Error as e:
            print(f"Error conectando a PostgreSQL: {e}")
            return None
    
    def execute_query(self, query, params=None):
        connection = self.get_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute(query, params or ())
                
                if query.strip().upper().startswith('SELECT'):
                    columns = [desc[0] for desc in cursor.description]
                    result = [dict(zip(columns, row)) for row in cursor.fetchall()]
                else:
                    connection.commit()
                    result = cursor.rowcount
                
                cursor.close()
                connection.close()
                return result
            except Error as e:
                print(f"Error ejecutando query: {e}")
                connection.rollback()
                return None
        return None
