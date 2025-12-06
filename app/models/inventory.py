"""
Modelos de Inventario - Productos y Rollos
"""
from app.extensions import db
from datetime import datetime


class Producto(db.Model):
    """Modelo para productos de polarizado"""
    __tablename__ = 'productos'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    linea = db.Column(db.String(50), nullable=False)  # Premium, Nanocarbon, Nanoceramic
    garantia_anios = db.Column(db.Integer, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    rollos = db.relationship('Rollo', backref='producto', lazy='dynamic')
    
    def __repr__(self):
        return f'<Producto {self.nombre} - {self.linea}>'


class Rollo(db.Model):
    """Modelo para rollos de polarizado (Código Padre)"""
    __tablename__ = 'rollos'
    
    id = db.Column(db.Integer, primary_key=True)
    codigo_padre = db.Column(db.String(50), unique=True, nullable=False, index=True)
    estado = db.Column(db.String(20), default='EN_DEPOSITO')  # EN_DEPOSITO, ASIGNADO, AGOTADO
    
    # Relación con producto
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    
    # Relación con usuario (instalador asignado)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    subcodigos = db.relationship('Subcodigo', backref='rollo', lazy='dynamic')
    
    def __repr__(self):
        return f'<Rollo {self.codigo_padre} - {self.estado}>'
