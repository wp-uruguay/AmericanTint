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
    
    # --- COLUMNA NUEVA (La que faltaba) ---
    fecha_asignacion = db.Column(db.DateTime, nullable=True)
    
    # Relaciones (Foreign Keys)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id')) 
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)

    # Relación inversa para ver info del producto fácilmente
    producto_info = db.relationship('Producto', backref='rollos_asociados', lazy=True)

    # Relación con los hijos (Garantías)
    subcodigos = db.relationship('Subcodigo', backref='rollo_padre', lazy=True)

    def __repr__(self):
        return f'<Rollo {self.codigo_padre}>'