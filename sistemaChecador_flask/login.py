from pymongo import MongoClient

MONGO_URI = 'mongodb+srv://tilino:_A1234__5678A_@checador.97iiilw.mongodb.net/?retryWrites=true&w=majority'
#MONGO_URI = 'mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh'
def db_connection():
    """ Establece la conexión a la base de datos. """
    try:
        client = MongoClient(MONGO_URI)
        db = client['prueba_checador']  # Selecciona la base de datos
        print('Conexión establecida con éxito.')
        return db
    except Exception as e:
        print('Error conectando a MongoDB: ', e)
        return None

def add_rfc(collection):
    """ Añade RFCs a la colección de login interactivamente. """
    while True:
        rfc = input('Ingrese un RFC para añadir a la base de datos (escriba "0" para salir): ')
        if rfc == '0':
            print('Terminando programa...')
            break
        try:
            result = collection.insert_one({'RFC': rfc})
            print(f'RFC añadido con ID: {result.inserted_id}')
        except Exception as e:
            print('Error añadiendo el RFC a MongoDB: ', e)


def main():
    db = db_connection()
    if db is not None:
        login = db['login']
        add_rfc(login)
    else:
        print("No se pudo establecer la conexión a la base de datos.")

if __name__ == '__main__':
    main()
