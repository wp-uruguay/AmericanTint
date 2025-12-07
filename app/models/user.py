from app.extensions import db, login_manager
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    username = db.Column(db.String(100), nullable=False, index=True)
    
    # Roles: 'admin', 'instalador', 'cliente', 'superadmin'
    role = db.Column(db.String(20), nullable=False, default='cliente')
    pais = db.Column(db.String(3), nullable=True) 
    
    # --- NUEVOS CAMPOS PERFIL INSTALADOR (Admin V2) ---
    nombre_responsable = db.Column(db.String(100), nullable=True)
    telefono_personal = db.Column(db.String(50), nullable=True)
    telefono_negocio = db.Column(db.String(50), nullable=True)
    direccion_negocio = db.Column(db.String(200), nullable=True)
    horario_atencion = db.Column(db.String(100), nullable=True) # Ej: "Lun-Vie 9-18hs"
    logo_url = db.Column(db.String(255), nullable=True) # URL o path de la imagen
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones
    rollos = db.relationship('Rollo', backref='propietario', lazy=True)
    logs = db.relationship('AuditLog', backref='actor', lazy=True)
    
    # Relación Soporte (Un usuario tiene muchos tickets creados)
    tickets = db.relationship('Ticket', backref='autor', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))