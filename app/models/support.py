from app.extensions import db
from datetime import datetime

class Ticket(db.Model):
    __tablename__ = 'tickets'

    id = db.Column(db.Integer, primary_key=True)
    asunto = db.Column(db.String(200), nullable=False)
    estado = db.Column(db.String(20), default='ABIERTO') # ABIERTO, RESPONDIDO, CERRADO
    prioridad = db.Column(db.String(20), default='NORMAL') # BAJA, NORMAL, ALTA, URGENTE
    
    # Quién creó el ticket (El Instalador)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relación con los mensajes del chat
    mensajes = db.relationship('TicketMessage', backref='ticket_padre', lazy=True, cascade="all, delete-orphan")

class TicketMessage(db.Model):
    __tablename__ = 'ticket_messages'

    id = db.Column(db.Integer, primary_key=True)
    contenido = db.Column(db.Text, nullable=False)
    
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'), nullable=False)
    
    # Quién escribió ESTE mensaje (Puede ser el Instalador o el Admin)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    fecha_envio = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Para saber quién lo escribió fácilmente
    sender = db.relationship('User', foreign_keys=[sender_id])