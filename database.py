import MySQLdb
import os

class Database:
    def __init__(self):
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
                ssl={"ca": "/etc/ssl/certs/ca-certificates.crt"}
            )
            return connection
        except Exception as e:
            print(f"Error conectando a PlanetScale: {e}")
            return None
    
    def execute_query(self, query, params=None):
        connection = self.get_connection()
        if connection:
            try:
                cursor = connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute(query, params or ())
                
                if query.strip().upper().startswith('SELECT'):
                    result = cursor.fetchall()
                else:
                    result = cursor.lastrowid
                
                cursor.close()
                connection.close()
                return result
            except Exception as e:
                print(f"Error ejecutando query: {e}")
                return None
        return None