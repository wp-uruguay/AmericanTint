from app.extensions import db
from datetime import datetime

class Subcodigo(db.Model):
    __tablename__ = 'subcodigos'

    id = db.Column(db.Integer, primary_key=True)
    
    # El código final: "AR-AT15-0001-617"
    codigo_hijo = db.Column(db.String(60), unique=True, nullable=False)
    pin_seguridad = db.Column(db.String(3), nullable=False)
    
    # Estados: 'INACTIVO', 'DISPONIBLE', 'PENDIENTE', 'ACTIVADO'
    estado = db.Column(db.String(20), default='INACTIVO')
    
    rollo_id = db.Column(db.Integer, db.ForeignKey('rollos.id'), nullable=False)
    
    # Datos del cliente
    cliente_nombre = db.Column(db.String(100), nullable=True)
    cliente_email = db.Column(db.String(100), nullable=True)
    cliente_telefono = db.Column(db.String(50), nullable=True)
    cliente_patente = db.Column(db.String(20), nullable=True)
    
    fecha_activacion = db.Column(db.DateTime, nullable=True)
    fecha_vencimiento = db.Column(db.DateTime, nullable=True)

    # --- CAMPOS DE RESEÑA ---
    instalador_correcto = db.Column(db.Boolean, default=True) # ¿Era el instalador correcto?
    review_texto = db.Column(db.Text, nullable=True)          # Comentario
    review_stars = db.Column(db.Integer, default=0)           # 1 a 5 estrellas

    def __repr__(self):
        return f'<Subcodigo {self.codigo_hijo}>'