import subprocess
import webbrowser
import configparser

# Leer las variables de variables.ini
config = configparser.ConfigParser()
config.read('variables.ini')
ip = config.get('variables', 'ip')
port = config.get('variables', 'port')

# Construir la URL de la página principal
url = f'http://{ip}:{port}/'

# Abrir el navegador con la URL del proyecto de Flask
webbrowser.open(url)

# Comando para ejecutar el script index.py
comando = ['python', 'index.py']

# Ejecutar el script index.py
subprocess.run(comando)
