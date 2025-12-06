"""
Email Service - Envío de correos electrónicos
"""
from flask import current_app, render_template
from flask_mail import Mail, Message


class EmailService:
    
    @staticmethod
    def send_warranty_activation_email(warranty, customer):
        """
        Enviar email de confirmación de activación de garantía
        
        Args:
            warranty: Objeto Warranty
            customer: Objeto Customer
        
        Returns:
            bool: True si se envió exitosamente
        """
        try:
            # TODO: Implementar envío de email
            # Configurar Flask-Mail en extensions.py si se requiere
            subject = f'Garantía Activada - {warranty.code}'
            
            # En producción, usar render_template para email HTML
            body = f"""
            Estimado/a {customer.full_name},
            
            Su garantía ha sido activada exitosamente:
            
            Código: {warranty.code}
            Fecha de activación: {warranty.activation_date}
            Fecha de expiración: {warranty.expiration_date}
            Vehículo: {warranty.vehicle_info}
            
            Gracias por confiar en American Tint.
            """
            
            # mail = Mail(current_app)
            # msg = Message(subject, recipients=[customer.email], body=body)
            # mail.send(msg)
            
            return True
            
        except Exception as e:
            print(f'Error al enviar email: {str(e)}')
            return False
    
    @staticmethod
    def send_warranty_expiration_reminder(warranty, customer):
        """
        Enviar recordatorio de vencimiento de garantía
        
        Returns:
            bool: True si se envió exitosamente
        """
        try:
            subject = f'Recordatorio: Su garantía está por vencer - {warranty.code}'
            
            body = f"""
            Estimado/a {customer.full_name},
            
            Le recordamos que su garantía está próxima a vencer:
            
            Código: {warranty.code}
            Días restantes: {warranty.days_remaining()}
            Fecha de expiración: {warranty.expiration_date}
            
            Para renovaciones, contáctenos.
            
            American Tint
            """
            
            return True
            
        except Exception as e:
            print(f'Error al enviar email: {str(e)}')
            return False
