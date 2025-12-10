from app.extensions import db
from datetime import datetime

class Rollo(db.Model):
    __tablename__ = 'rollos'

    id = db.Column(db.Integer, primary_key=True)
    codigo_padre = db.Column(db.String(50), unique=True, nullable=False)
    estado = db.Column(db.String(20), default='EN_DEPOSITO')
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_asignacion = db.Column(db.DateTime, nullable=True)
    
    # --- NUEVO: LOTE DE IMPORTACIÓN ---
    # Sirve para agrupar rollos que entraron juntos (Ej: "IMP-20231201")
    lote = db.Column(db.String(50), nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id')) 
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)

    producto_info = db.relationship('Producto', backref='rollos_asociados', lazy=True)
    subcodigos = db.relationship('Subcodigo', backref='rollo_padre', lazy=True)

    def __repr__(self):
        return f'<Rollo {self.codigo_padre}>'