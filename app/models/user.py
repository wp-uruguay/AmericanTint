from app.extensions import db, login_manager
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    username = db.Column(db.String(100), nullable=False, index=True)
    
    # Roles: 'admin', 'instalador', 'cliente'
    role = db.Column(db.String(20), nullable=False, default='cliente')
    
    # País (Opcional por ahora, lo dejamos nullable para evitar errores)
    pais = db.Column(db.String(3), nullable=True) 
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones
    # Nota: Usamos strings en relationship para evitar errores de importación circular
    rollos = db.relationship('Rollo', backref='propietario', lazy=True)
    logs = db.relationship('AuditLog', backref='actor', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'

# --- ESTA ES LA PARTE QUE FALTABA (EL USER LOADER) ---
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))