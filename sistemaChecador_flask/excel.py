from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')  # Ajusta esta URL a tu configuración de MongoDB
db = client['prueba']  # Asegúrate de que el nombre de la base de datos sea correcto

import pandas as pd

def generar_excel():
    # Colección dentro de tu base de datos MongoDB
    coleccion = db['UI']  # Asegúrate de que 'UI' es el nombre correcto de tu colección

    # Obtener todos los documentos de la colección 'UI'
    documentos = coleccion.find()

    # Convertir los documentos MongoDB a una lista de diccionarios para usar con Pandas
    datos = list(documentos)

    # Crear un DataFrame de pandas con los datos
    df = pd.DataFrame(datos)

    # Si necesitas eliminar la columna '_id' generada por MongoDB, puedes hacerlo así:
    if '_id' in df:
        del df['_id']

    # Definir el nombre del archivo Excel
    nombre_archivo = 'reporte_asistencia.xlsx'

    # Crear un escritor de Pandas Excel usando XlsxWriter como motor
    writer = pd.ExcelWriter(nombre_archivo, engine='xlsxwriter')

    # Convertir el DataFrame a un archivo Excel
    df.to_excel(writer, sheet_name='Reporte Asistencia')

    # Guardar el archivo
    writer.save()

    return nombre_archivo
