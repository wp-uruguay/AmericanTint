import os
from dotenv import load_dotenv

# Cargar las variables del archivo .env explícitamente
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '../.env'))

class Config:
    # Clave secreta (usa un valor por defecto si falla la lectura)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave-dev-por-defecto'
    
    # Base de datos
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or 'sqlite:///erp.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # --- LA CLAVE DE LOS SUBDOMINIOS ---
    # Si esto es None, los subdominios NO funcionarán.
    #SERVER_NAME = os.environ.get('SERVER_NAME')
    SERVER_NAME = 'americantint.local:5000'
# Bloque de depuración (Míralo en la terminal al arrancar)
print(f"--- DEBUG CONFIG ---")
print(f"SERVER_NAME detectado: {Config.SERVER_NAME}")
print(f"--------------------")