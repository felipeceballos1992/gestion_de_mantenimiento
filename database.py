import MySQLdb
from MySQLdb import Error
import os
from contextlib import contextmanager

class Database:
    def __init__(self):
        # Configuración para PlanetScale
        self.host = os.getenv('DATABASE_HOST')
        self.database = os.getenv('DATABASE')  
        self.user = os.getenv('DATABASE_USERNAME')
        self.password = os.getenv('DATABASE_PASSWORD')
    
    def get_connection(self):
        try:
            connection = MySQLdb.connect(
                host=self.host,
                user=self.user,
                passwd=self.password,
                db=self.database,
                autocommit=True,
                ssl_mode="VERIFY_IDENTITY",
                ssl={"ca": "C:\ssl\cacert.pem"}
            )
            return connection
        except Error as e:
            print(f"Error conectando a PlanetScale: {e}")
            return None
    
    @contextmanager
    def get_cursor(self):
        """Context manager para manejar conexiones y cursores automáticamente"""
        connection = self.get_connection()
        if connection:
            try:
                cursor = connection.cursor(MySQLdb.cursors.DictCursor)
                yield cursor
            except Error as e:
                print(f"Error con cursor: {e}")
                raise
            finally:
                cursor.close()
                connection.close()
        else:
            yield None
    
    def execute_query(self, query, params=None):
        with self.get_cursor() as cursor:
            if cursor:
                cursor.execute(query, params or ())
                
                if query.strip().upper().startswith('SELECT'):
                    return cursor.fetchall()
                else:
                    return cursor.lastrowid
        return None
    
    def execute_many(self, query, params_list):
        """Para inserciones múltiples más eficientes"""
        with self.get_cursor() as cursor:
            if cursor:
                cursor.executemany(query, params_list)
                return cursor.rowcount
        return None
    
    def test_connection(self):
        """Test de conexión a la base de datos"""
        try:
            with self.get_cursor() as cursor:
                if cursor:
                    cursor.execute("SELECT 1 as test")
                    result = cursor.fetchone()
                    return result is not None
            return False
        except Error as e:
            print(f"Error testeando conexión: {e}")
            return False