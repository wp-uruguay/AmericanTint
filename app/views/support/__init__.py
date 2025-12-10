from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.extensions import db
from app.models import User, Ticket, TicketMessage, AuditLog
from datetime import datetime

support_bp = Blueprint('support', __name__)

# 1. LISTA DE TICKETS (Bandeja de Entrada)
@support_bp.route('/')
@login_required
def index():
    # Si es Admin/Superadmin: Ve TODOS los tickets
    if current_user.role in ['admin', 'superadmin']:
        tickets = Ticket.query.order_by(Ticket.fecha_actualizacion.desc()).all()
    # Si es Instalador: Ve SOLO sus tickets
    else:
        tickets = Ticket.query.filter_by(user_id=current_user.id).order_by(Ticket.fecha_actualizacion.desc()).all()

    return render_template('support/index.html', tickets=tickets)

# 2. CREAR NUEVO TICKET
@support_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        asunto = request.form.get('asunto')
        mensaje_inicial = request.form.get('mensaje')
        prioridad = request.form.get('prioridad')

        try:
            # Crear el Ticket Padre
            nuevo_ticket = Ticket(
                asunto=asunto,
                prioridad=prioridad,
                estado='ABIERTO',
                user_id=current_user.id
            )
            db.session.add(nuevo_ticket)
            db.session.flush() # Para obtener el ID

            # Crear el primer mensaje
            primer_mensaje = TicketMessage(
                contenido=mensaje_inicial,
                ticket_id=nuevo_ticket.id,
                sender_id=current_user.id
            )
            db.session.add(primer_mensaje)
            
            # Auditoría
            db.session.add(AuditLog(user_id=current_user.id, accion='NUEVO_TICKET', detalle=f"Ticket #{nuevo_ticket.id}: {asunto}"))
            
            db.session.commit()
            flash('Ticket creado exitosamente.', 'success')
            return redirect(url_for('support.detail', ticket_id=nuevo_ticket.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear ticket: {str(e)}', 'danger')

    return render_template('support/create.html')

# 3. VER Y RESPONDER TICKET (Chat)
@support_bp.route('/<int:ticket_id>', methods=['GET', 'POST'])
@login_required
def detail(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)

    # Seguridad: Solo el dueño o un admin pueden ver esto
    if current_user.role not in ['admin', 'superadmin'] and ticket.user_id != current_user.id:
        flash('No tienes permiso para ver este ticket.', 'danger')
        return redirect(url_for('support.index'))

    # Lógica para RESPONDER
    if request.method == 'POST':
        respuesta = request.form.get('respuesta')
        nuevo_estado = request.form.get('estado') # Solo admin puede cambiar estado

        if respuesta:
            msg = TicketMessage(
                contenido=respuesta,
                ticket_id=ticket.id,
                sender_id=current_user.id
            )
            db.session.add(msg)
            
            # Actualizar fecha del ticket para que suba arriba
            ticket.fecha_actualizacion = datetime.utcnow()
            
            # Si responde el admin, pasamos a RESPONDIDO. Si responde el usuario, a ABIERTO.
            if current_user.role in ['admin', 'superadmin']:
                if nuevo_estado: ticket.estado = nuevo_estado
                else: ticket.estado = 'RESPONDIDO'
            else:
                ticket.estado = 'ABIERTO' # El usuario volvió a preguntar

            db.session.commit()
            flash('Respuesta enviada.', 'success')
            return redirect(url_for('support.detail', ticket_id=ticket.id))

    return render_template('support/detail.html', ticket=ticket)