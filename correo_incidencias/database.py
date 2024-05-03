from pymongo import MongoClient
from configparser import ConfigParser

# Función para leer el archivo variables.ini y obtener el URI de MongoDB
def obtener_uri_mongo():
    try:
        config = ConfigParser()
        config.read('variables.ini')  # Ruta al archivo variables.ini

        # Obtener el URI de MongoDB del archivo variables.ini
        uri_mongo = config.get('variables', 'MONGO_URI')
        return uri_mongo
    except Exception as e:
        print('Error al obtener el URI de MongoDB:', e)
        return None

# Ahora puedes utilizar la función obtener_uri_mongo() para obtener el URI de MongoDB
MONGO_URI = obtener_uri_mongo()

# Continúa con tu función dbConnection() como la tienes actualmente, utilizando el URI obtenido
def dbConnection():
    try:
        client = MongoClient(MONGO_URI)
        db = client.get_database("prueba_checador")
        print('Conexión exitosa a la Base de Datos')
    except ConnectionError as e:
        print('Error de conexión a la Base de Datos:', e)
        return None
    return db

# Llamar a la función dbConnection para establecer la conexión con MongoDB
db = dbConnection()
