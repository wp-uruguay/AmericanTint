"""
Warranty Service - Lógica de gestión de garantías
"""
from app.extensions import db
from app.models.warranty import Warranty
from app.models.customer import Customer
from app.models.stock import Stock
from app.models.transaction import Transaction
from datetime import datetime


class WarrantyService:
    
    @staticmethod
    def activate_warranty(warranty_code, customer_data, vehicle_info='', warranty_years=5):
        """
        Activar una garantía vinculándola a un cliente
        
        Args:
            warranty_code: Código de la garantía
            customer_data: Dict con datos del cliente (first_name, last_name, email, phone)
            vehicle_info: Información del vehículo
            warranty_years: Años de garantía (default 5)
        
        Returns:
            tuple: (success: bool, message: str, warranty: Warranty)
        """
        try:
            # Buscar garantía
            warranty = Warranty.query.filter_by(code=warranty_code).first()
            
            if not warranty:
                return False, 'Código de garantía no encontrado', None
            
            if warranty.status != 'pending':
                return False, f'Esta garantía ya está {warranty.status}', None
            
            # Buscar o crear cliente
            customer = Customer.query.filter_by(email=customer_data['email']).first()
            
            if not customer:
                customer = Customer(
                    first_name=customer_data['first_name'],
                    last_name=customer_data['last_name'],
                    email=customer_data['email'],
                    phone=customer_data.get('phone', '')
                )
                db.session.add(customer)
                db.session.flush()
            
            # Activar garantía
            warranty.activate(
                customer_id=customer.id,
                vehicle_info=vehicle_info,
                warranty_years=warranty_years
            )
            
            # Actualizar stock
            stock = Stock.query.get(warranty.stock_id)
            if stock:
                stock.used_quantity += 1
                stock.update_availability()
            
            # Registrar transacción
            transaction = Transaction(
                transaction_type='warranty_activation',
                warranty_id=warranty.id,
                stock_id=warranty.stock_id,
                description=f'Garantía activada para {customer.full_name}'
            )
            db.session.add(transaction)
            
            db.session.commit()
            
            return True, 'Garantía activada exitosamente', warranty
            
        except Exception as e:
            db.session.rollback()
            return False, f'Error al activar garantía: {str(e)}', None
    
    @staticmethod
    def search_warranty(code):
        """
        Buscar garantía por código
        
        Returns:
            Warranty or None
        """
        return Warranty.query.filter_by(code=code).first()
    
    @staticmethod
    def get_warranty_details(warranty_id):
        """
        Obtener detalles completos de una garantía
        
        Returns:
            dict: Información completa de la garantía
        """
        warranty = Warranty.query.get(warranty_id)
        
        if not warranty:
            return None
        
        return {
            'warranty': warranty,
            'customer': warranty.customer,
            'stock': warranty.stock,
            'product': warranty.stock.product if warranty.stock else None,
            'days_remaining': warranty.days_remaining(),
            'is_expired': warranty.is_expired()
        }
    
    @staticmethod
    def get_expiring_warranties(days=30):
        """
        Obtener garantías que vencen en los próximos N días
        
        Args:
            days: Días de anticipación
        
        Returns:
            list: Lista de garantías próximas a vencer
        """
        from datetime import timedelta
        expiration_date = datetime.utcnow() + timedelta(days=days)
        
        warranties = Warranty.query.filter(
            Warranty.status == 'active',
            Warranty.expiration_date <= expiration_date,
            Warranty.expiration_date > datetime.utcnow()
        ).all()
        
        return warranties
    
    @staticmethod
    def cancel_warranty(warranty_id, reason=''):
        """
        Cancelar una garantía
        
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            warranty = Warranty.query.get(warranty_id)
            
            if not warranty:
                return False, 'Garantía no encontrada'
            
            warranty.status = 'cancelled'
            
            # Registrar transacción
            transaction = Transaction(
                transaction_type='warranty_cancellation',
                warranty_id=warranty.id,
                stock_id=warranty.stock_id,
                description=f'Garantía cancelada. Razón: {reason}'
            )
            db.session.add(transaction)
            
            db.session.commit()
            
            return True, 'Garantía cancelada exitosamente'
            
        except Exception as e:
            db.session.rollback()
            return False, f'Error al cancelar garantía: {str(e)}'
