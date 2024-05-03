from pymongo import MongoClient
import certifi

MONGO_URI = 'mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh'

def dbConnection():
  try:
    client = MongoClient(MONGO_URI)
    db = client['sistemachecador']
  except ConnectionError:
    print('Error de conexion a la Base de Datos')
  return db