import os
from dotenv import load_dotenv

# Cargar las variables del archivo .env explícitamente
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '../.env'))

class Config:
    # 1. Configuración General
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave-dev-por-defecto'
    
    # 2. Base de Datos
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or 'sqlite:///erp.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 3. Configuración de EMAIL (¡ESTO ES LO QUE FALTABA!)
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    # El puerto debe convertirse a entero (int)
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    # La variable viene como string 'True', hay que convertirla a booleano
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') == 'True'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')

# Diagnóstico al arrancar (Para ver si lee bien)
print(f"--- 📧 CONFIGURACIÓN DETECTADA ---")
print(f"Servidor: {Config.MAIL_SERVER}")
print(f"Puerto: {Config.MAIL_PORT}")
print(f"Usuario: {Config.MAIL_USERNAME}")
print(f"----------------------------------")