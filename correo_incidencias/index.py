from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import database as dbase
import configparser
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from functools import wraps

# Configuración de la base de datos
db = dbase.dbConnection()

app = Flask(__name__)
app.secret_key = '0adj289j3d82j39k9e28dm3ue82fn98eu3e2g2r3nun9238je923je2398289298ej2jjjijaliottttttthhhaliothaud9u28u92893du2839u23u89'  # Clave secreta para la sesión

# Configuración del logging
logging.basicConfig(level=logging.INFO)
handler = logging.FileHandler('index.log')
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
app.logger.addHandler(handler)
logger = logging.getLogger(__name__)

# Decorador para requerir inicio de sesión
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/incidenciacorreo')
@login_required
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

# Ruta para enviar correo
@app.route('/ruta_para_enviar_correo', methods=['POST'])
@login_required
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

# Ruta para mostrar usuarios
@app.route('/usuarios', methods=['GET'])
@login_required
def mostrar_usuarios():
    # Obtener todos los RFC y contraseñas de la colección 'puestos_jefes'
    usuarios = db.puestos_jefes.find()
    usuarios_list = list(usuarios)
    # Obtener todos los RFC de la colección 'datos_generales'
    empleados = db.datos_generales.find()
    empleados_list = list(empleados)
    return render_template('gestion_usuarios.html', usuarios=usuarios_list, empleados=empleados_list)

# Ruta para el inicio de sesión
@app.route('/login', methods=['POST'])
def login():
    rfc = request.form['rfc']
    contrasena = request.form['contrasena']
    user_collection = db['login_jefes']
    user = user_collection.find_one({"rfc": rfc, "contrasena": contrasena})
    
    if user:
        session['logged_in'] = True
        return jsonify({'redirect': url_for('principal'), 'token': '4LI0THT0K3N', 'rfc': rfc}), 200
    else:
        return jsonify({'error': 'Credenciales incorrectas'}), 401

# Ruta para verificar sesión
@app.route('/verificacion', methods=['POST'])
def verificacion():
    rfc = request.form['rfc']    # Accede al valor del campo 'rfc'
    token = request.form['token']  # Accede al valor del campo 'token'
    if session.get('logged_in') and db['login_jefes'].find_one({"rfc": rfc}):
        return jsonify({'authorized': True}), 200
    else:
        return jsonify({'authorized': False, 'error': 'Verificación fallida-403'}), 403

# Ruta para la página de inicio
@app.route('/')
def index():
    if 'logged_in' in session:
        return redirect(url_for('principal'))
    else:
        return render_template('login.html')

# Ruta para cerrar sesión
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

# Ruta para la página principal después de iniciar sesión
@app.route('/principal')
@login_required
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

# Ruta para agregar usuario
@app.route('/agregarusuario', methods=['PUT'])
@login_required
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

# Ruta para eliminar usuario
@app.route('/eliminarusuario', methods=['DELETE'])
@login_required
def eliminarusuario():
    rfc = request.args.get('rfc')
    result = db.puestos_jefes.delete_one({'rfc': rfc})
    
    if result.deleted_count > 0:
        return jsonify(message="Usuario eliminado correctamente."), 200
    else:
        return jsonify(message="No se encontró el usuario."), 404

# Ruta de página no encontrada
@app.errorhandler(404)
def notFound(error=None):
    message = {
        'message': 'No encontrado',
        'status': '404 Not Found'
    }
    response = jsonify(message)
    response.status_code = 404
    return response

# Ruta para el manejo de errores 405
@app.errorhandler(405)
def method_not_allowed(error):
    # Leer la IP y el puerto desde variables.ini
    config = configparser.ConfigParser()
    config.read('variables.ini')
    ip = config.get('variables', 'ip')
    port = config.getint('variables', 'port')

    # Crear el mensaje de error personalizado
    message = {
        'error': 'Metodo no permitido',
        'status': '405 Method Not Allowed',
        'message': f'El metodo utilizado no es permitido en esta ruta. Por favor, verifique si inicio sesion y autenticado. Acceda a la direccion {ip}:{port}/'
    }
    response = jsonify(message)
    response.status_code = 405
    return response



if __name__ == '__main__':
    # Obtener la IP y el puerto desde el archivo de configuración
    config = configparser.ConfigParser()
    config.read('variables.ini')
    ip = config.get('variables', 'ip')
    port = config.getint('variables', 'port')

    # Iniciar el servidor Flask
    app.run(debug=True, host=ip, port=port)

print("Iniciando el servidor envío de incidencias (correo) ... cierre esta ventana para terminar el proceso.")
