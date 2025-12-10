from app.extensions import db

class Producto(db.Model):
    __tablename__ = 'productos'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False) # Ej: AT Premium 15
    linea = db.Column(db.String(50), nullable=False)   # Premium, Nanocarbon, Nanoceramic
    variedad = db.Column(db.String(10), nullable=False)# 05, 15, 35, 50...
    garantia_anios = db.Column(db.Integer, nullable=False) # 6 o 10
    
    # NUEVO: PRECIO LISTA (Por Rollo)
    precio = db.Column(db.Float, default=0.0) 
    
    # Relación inversa
    # rollos_asociados = db.relationship('Rollo', backref='producto_info', lazy=True)

    def __repr__(self):
        return f'<Producto {self.nombre}>'