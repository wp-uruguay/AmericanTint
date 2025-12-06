"""
Modelo Cliente
Gestión de clientes que activan garantías
"""
from app.extensions import db
from datetime import datetime


class Customer(db.Model):
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Información personal
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, index=True)
    phone = db.Column(db.String(20))
    
    # Información adicional
    address = db.Column(db.String(200))
    city = db.Column(db.String(50))
    state = db.Column(db.String(50))
    zip_code = db.Column(db.String(10))
    
    # Notas
    notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    warranties = db.relationship('Warranty', backref='customer', lazy='dynamic')
    
    @property
    def full_name(self):
        """Nombre completo"""
        return f"{self.first_name} {self.last_name}"
    
    def active_warranties_count(self):
        """Contar garantías activas"""
        return self.warranties.filter_by(status='active').count()
    
    def __repr__(self):
        return f'<Customer {self.full_name}>'
