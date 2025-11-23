import MySQLdb
import os

class Database:
    def __init__(self):
        # Configuración para PlanetScale
        self.host = os.getenv('DATABASE_HOST')
        self.database = os.getenv('DATABASE')  
        self.user = os.getenv('DATABASE_USERNAME')
        self.password = os.getenv('DATABASE_PASSWORD')
        
        # Validar que todas las variables estén presentes
        if not all([self.host, self.database, self.user, self.password]):
            missing = []
            if not self.host: missing.append('DATABASE_HOST')
            if not self.database: missing.append('DATABASE')
            if not self.user: missing.append('DATABASE_USERNAME')
            if not self.password: missing.append('DATABASE_PASSWORD')
            raise Exception(f"Missing environment variables: {', '.join(missing)}")
    
    def get_connection(self):
        try:
            # Configuración SSL para MySQLdb (diferente a mysql-connector-python)
            ssl_config = {
                'ssl': {
                    'ca': '/etc/ssl/certs/ca-certificates.crt'
                }
            }
            
            connection = MySQLdb.connect(
                host=self.host,
                user=self.user,
                passwd=self.password,
                db=self.database,
                autocommit=True,
                ssl=ssl_config['ssl']  # Solo pasar el dict ssl, sin ssl_mode
            )
            print("✅ Conexión exitosa a PlanetScale")
            return connection
        except Exception as e:
            print(f"❌ Error conectando a PlanetScale: {e}")
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