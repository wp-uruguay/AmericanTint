from flask_mail import Mail, Message
from flask import current_app
from threading import Thread

mail = Mail()

def send_async_email(app, msg, link_debug):
    with app.app_context():
        try:
            mail.send(msg)
            print(f"✅ EMAIL ENVIADO EXITOSAMENTE a: {msg.recipients}")
        except Exception as e:
            print(f"⚠️ EL EMAIL FALLÓ: {e}")
            if link_debug:
                print(f"🔗 LINK DE ACTIVACIÓN: {link_debug}")

class EmailService:
    
    @staticmethod
    def enviar_activacion(destinatario, codigo, link_activacion):
        app = current_app._get_current_object()
        
        # LOG PARA DEBUG
        print("\n" + "="*50)
        print(f"📧 EMAIL ACTIVACIÓN PARA: {destinatario}")
        print(f"🔗 LINK: {link_activacion}")
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

    @staticmethod
    def enviar_mensaje_personalizado(destinatario, asunto, cuerpo):
        app = current_app._get_current_object()
        
        msg = Message(
            subject=f"📢 {asunto} - American Tint",
            recipients=[destinatario]
        )
        
        # Convertimos saltos de línea a <br>
        cuerpo_html = cuerpo.replace('\n', '<br>')
        
        msg.html = f"""
        <div style="font-family: Arial, sans-serif; padding: 20px; border: 1px solid #eee;">
            <h3 style="color: #333;">Hola,</h3>
            <p style="font-size: 16px; color: #555;">{cuerpo_html}</p>
            <hr>
            <small style="color: #999;">Enviado desde el Centro de Soporte American Tint</small>
        </div>
        """
        
        Thread(target=send_async_email, args=(app, msg, None)).start()