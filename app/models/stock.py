from app.extensions import db
from datetime import datetime

class Rollo(db.Model):
    __tablename__ = 'rollos'

    id = db.Column(db.Integer, primary_key=True)
    
    # El código único: Ej "AR-AT15-0001"
    codigo_padre = db.Column(db.String(50), unique=True, nullable=False)
    
    # Estados: 'EN_DEPOSITO', 'ASIGNADO', 'AGOTADO'
    estado = db.Column(db.String(20), default='EN_DEPOSITO')
    
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones (Foreign Keys)
    # Quién tiene el rollo (Admin o Instalador)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id')) 
    
    # Qué producto es
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)

    # Relación con los hijos (Garantías)
    # Nota: Usamos el string 'Subcodigo' para evitar problemas de importación si la clase no se leyó aun
    subcodigos = db.relationship('Subcodigo', backref='rollo_padre', lazy=True)

    # Agregar esto dentro de la clase Rollo (al final)
    producto_info = db.relationship('Producto', backref='rollos_asociados', lazy=True)

    def __repr__(self):
        return f'<Rollo {self.codigo_padre}>'