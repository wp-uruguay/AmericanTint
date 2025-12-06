import smtplib
import os
from dotenv import load_dotenv

# Cargar configuración
load_dotenv()

USER = os.getenv('MAIL_USERNAME')
PASSWORD = os.getenv('MAIL_PASSWORD')
SERVER = os.getenv('MAIL_SERVER')
PORT = 587

print(f"--- 📧 PROBANDO CONEXIÓN A GMAIL ---")
print(f"Servidor: {SERVER}:{PORT}")
print(f"Usuario: {USER}")
print("Intentando conectar...")

try:
    # 1. Conectar al servidor
    server = smtplib.SMTP(SERVER, PORT)
    server.set_debuglevel(1) # Esto imprimirá los detalles técnicos
    
    # 2. Iniciar TLS (Encriptación)
    print("Conexión establecida. Iniciando TLS...")
    server.starttls()
    
    # 3. Loguearse
    print("Intentando Login...")
    server.login(USER, PASSWORD)
    
    print("\n✅ ¡ÉXITO! Tu computadora SÍ tiene acceso a Gmail.")
    print("El problema no es la red, es algo en Flask.")
    server.quit()

except Exception as e:
    print(f"\n❌ ERROR DE CONEXIÓN: {e}")
    print("Tu Firewall o Proveedor de Internet está bloqueando la salida.")