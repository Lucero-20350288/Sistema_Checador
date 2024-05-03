from flask import Flask, render_template, request, Response, jsonify, redirect, url_for
import database as dbase
import configparser
import logging
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
db = dbase.dbConnection()
app = Flask(__name__)

import logging
from logging.handlers import RotatingFileHandler

# Configuración del logging
logging.basicConfig(level=logging.INFO)  # Puedes cambiar a DEBUG, ERROR, etc., según lo que necesites
handler = RotatingFileHandler('index.log', maxBytes=1000000, backupCount=2)
handler.setLevel(logging.INFO)  # O cualquier otro nivel según necesites
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.addHandler(handler)


@app.route('/incidenciacorreo')
def incidenciacorreo():
    config = configparser.ConfigParser()
    correo_electronico = ''
    password = ''
    try:
        config.read('variables.ini')
        correo_electronico = config.get('config_Correo', 'correo_electronico', fallback='')
        password = config.get('config_Correo', 'password', fallback='')
    except configparser.Error as e:
        logger.error(f"Error al cargar el archivo de configuración: {e}")

    empleados = db['datos_generales']
    empleadosReceived = empleados.find()

    return render_template('horarioincidenciacorreo.html', empleados=empleadosReceived, correo_electronico=correo_electronico, password=password)

#---------------------------------------#


@app.route('/ruta_para_enviar_correo', methods=['POST'])
def enviar_correo():
    try:
        config = configparser.ConfigParser()
        with open('variables.ini', encoding='utf-8') as f:
            config.read_file(f)
        descripcion_correo_introduccion = config.get('Textos', 'descripcion_correo_introduccion', fallback='')

        # Obtener los datos del formulario enviado mediante FormData
        correo_empleado = request.form.get('correoElectronicoEmpleado')
        asunto = request.form.get('asunto')
        nombre_empleado = request.form.get('nombreEmpleado')
        
        # Obtener los datos de remitente y contraseña enviados mediante FormData
        remitente = request.form.get('correoElectronico')
        password = request.form.get('password')

        # Adjuntar el PDF enviado mediante FormData
        pdf = request.files['pdf']

        # Configurar el correo electrónico
        msg = MIMEMultipart()
        msg['From'] = remitente  # Remitente
        msg['To'] = correo_empleado  # Destinatario
        msg['Subject'] = asunto  # Asunto

        # Agregar el cuerpo del correo (texto)
        cuerpo_correo = f"""<h1>{nombre_empleado}</h1><br><br>
        {descripcion_correo_introduccion}<br><br>
        <h2>ESTIMADO: {correo_empleado}</h2><br><br>
        ESTE CORREO HA SIDO GENERADO AUTOMATICAMENTE, CUALQUIER DUDA AL RESPECTO CONSULTAR CON EL DEPARTAMENTO DE RH."""
        msg.attach(MIMEText(cuerpo_correo, 'html', _charset='utf-8'))

        # Adjuntar el PDF al correo
        pdf_adjunto = pdf.read()
        adjunto_pdf = MIMEBase('application', 'octet-stream')
        adjunto_pdf.set_payload(pdf_adjunto)
        encoders.encode_base64(adjunto_pdf)
        adjunto_pdf.add_header('Content-Disposition', 'attachment', filename='Notificacion_de_Incidencias.pdf')
        msg.attach(adjunto_pdf)

        # Establecer la conexión SMTP con el servidor de Office 365
        servidor_smtp = smtplib.SMTP('smtp.office365.com', 587)
        servidor_smtp.starttls()

        # Autenticarse con el servidor SMTP de Office 365
        servidor_smtp.login(remitente, password)

        # Enviar el correo electrónico
        servidor_smtp.sendmail(remitente, correo_empleado, msg.as_string())

        return jsonify({'message': 'Correo enviado con éxito'}), 200
    except Exception as e:
        error_message = f'Error al enviar el correo: {str(e)}'
        logger.error(error_message)  # Registrar el error en el archivo de log
        return jsonify({'error': error_message}), 500
    finally:
        try:
            # Cerrar la conexión SMTP en el bloque finally
            servidor_smtp.quit()
        except:
            pass  # Si hay algún error al cerrar la conexión, simplemente pasa


#investigue y en : https://support.microsoft.com/es-es/office/configuraci%C3%B3n-pop-imap-y-smtp-para-outlook-com-d088b986-291d-42b8-9564-9c414e2aa040
# te dice que para correos que no son @outlook (en nuestro caso actual es @tuxtepec) se deshabilita por default el smtp del correo, entonces solo se recomienda usar POP.


@app.route('/usuarios', methods=['GET'])
def mostrar_usuarios():
    # Obtener todos los RFC y contraseñas de la colección 'puestos_jefes'
    usuarios = db.puestos_jefes.find()
    usuarios_list = list(usuarios)
    # Obtener todos los RFC de la colección 'datos_generales'
    empleados = db.datos_generales.find()
    empleados_list = list(empleados)
    return render_template('gestion_usuarios.html', usuarios=usuarios_list, empleados=empleados_list)

@app.route('/login', methods=['POST'])
def login():
    rfc = request.form['rfc']
    contrasena = request.form['contrasena']
    user_collection = db['login_jefes']
    user = user_collection.find_one({"rfc": rfc, "contrasena": contrasena})
    
    if user:
        # Renderizar directamente el template con variables
        usuario = Usuario(id =5, nombre ="Pedro" )
        login_user(usuario)
        return jsonify({'redirect': url_for('principal'), 'token': '4LI0THT0K3N', 'rfc': rfc}), 200
    else:
        return jsonify({'error': 'Credenciales incorrectas'}), 401
    
@app.route('/verificacion', methods=['POST'])
def verificacion():
    rfc = request.form['rfc']    # Accede al valor del campo 'rfc'
    token = request.form['token']  # Accede al valor del campo 'token'
    print(rfc)
    print(token)
    if token == "4LI0THT0K3N" and db['login_jefes'].find_one({"rfc": rfc}):
        return jsonify({'authorized': True}), 200
    else:
        return jsonify({'authorized': False, 'error': 'Verificación fallida-403'}), 403


@app.route('/agregarusuario', methods=['PUT'])
def agregarusuario():
    rfc = request.form['rfc']
    contrasena = request.form['contrasena']
    
    # Verificar si el RFC existe en la colección 'datos_generales'
    if db.puestos_jefes.find_one({"rfc": rfc}):
        # Si el RFC ya existe, actualizar la contraseña en la colección 'login'
        db.puestos_jefes.update_one({'rfc': rfc}, {'$set': {'contrasena': contrasena}})
        return jsonify(success="Contraseña actualizada correctamente.")
    else:
        # Si el RFC no existe, agregar el usuario a la colección 'login'
        db.puestos_jefes.insert_one({'rfc': rfc, 'contrasena': contrasena})
        return jsonify(success="Usuario agregado correctamente.")


#FINALIZA ROUTES ALIOTH


@app.route('/')
def index():
    return render_template('login.html')

@app.route('/principal')
def principal():
  config = configparser.ConfigParser()
  correo_electronico = ''
  password = ''
  try:
        config.read('variables.ini')
        correo_electronico = config.get('config_Correo', 'correo_electronico', fallback='')
        password = config.get('config_Correo', 'password', fallback='')
  except configparser.Error as e:
        logger.error(f"Error al cargar el archivo de configuración: {e}")

  empleados = db['datos_generales']
  empleadosReceived = empleados.find()

  return render_template('principal.html', empleados=empleadosReceived, correo_electronico=correo_electronico, password=password)

@app.route('/eliminarusuario', methods=['DELETE'])
def eliminarusuario():
    rfc = request.args.get('rfc')
    result = db.puestos_jefes.delete_one({'rfc': rfc})
    
    if result.deleted_count > 0:
        return jsonify(message="Usuario eliminado correctamente."), 200
    else:
        return jsonify(message="No se encontró el usuario."), 404

  
@app.errorhandler(404)
def notFound(error=None):
  message ={
    'message': 'No encontrado',
    'status': '404 Not Found'
  }
  response= jsonify(message)
  response.status_code = 404
  return response


if __name__ == '__main__':
    # Mensaje personalizado para mostrar en la consola

    # Obtener la IP y el puerto desde el archivo de configuración
    config = configparser.ConfigParser()
    config.read('variables.ini')
    ip = config.get('variables', 'ip')
    port = config.getint('variables', 'port')

    # Iniciar el servidor Flask
    app.run(debug=True, host=ip, port=port)
    

print("Iniciando el servidor envio de incidencias(correo) ... cierre esta ventana para terminar el proceso. ")