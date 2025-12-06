from flask_mail import Mail, Message
from flask import current_app
from threading import Thread

mail = Mail()

def send_async_email(app, msg, link_debug):
    with app.app_context():
        try:
            # Intentamos enviar el correo real
            mail.send(msg)
            print(f"✅ EMAIL ENVIADO EXITOSAMENTE a: {msg.recipients}")
        except Exception as e:
            print(f"⚠️ EL EMAIL FALLÓ (Probablemente configuración .env): {e}")
            print(f"🔗 PERO AQUÍ TIENES EL LINK PARA PROBAR: {link_debug}")

class EmailService:
    @staticmethod
    def enviar_activacion(destinatario, codigo, link_activacion):
        app = current_app._get_current_object()
        
        # IMPRIMIR EN TERMINAL SIEMPRE (Para que puedas probar sin Gmail)
        print("\n" + "="*50)
        print(f"📧 SIMULACIÓN DE CORREO PARA: {destinatario}")
        print(f"🔗 LINK DE ACTIVACIÓN: {link_activacion}")
        print("="*50 + "\n")

        msg = Message(
            subject="🌟 Activa tu Garantía - American Tint",
            recipients=[destinatario]
        )
        
        msg.html = f"""
        <div style="font-family: Arial, sans-serif; padding: 20px; border: 1px solid #ddd;">
            <h2 style="color: #d9534f;">American Tint Premium Films</h2>
            <p>Hola,</p>
            <p>Su instalador ha iniciado el proceso de garantía. Haga clic abajo para activar:</p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{link_activacion}" style="background-color: #0275d8; color: white; padding: 15px 25px; text-decoration: none; border-radius: 5px;">
                    ACTIVAR GARANTÍA AHORA
                </a>
            </div>
            <p>Código manual: <strong>{codigo}</strong></p>
        </div>
        """
        
        Thread(target=send_async_email, args=(app, msg, link_activacion)).start()