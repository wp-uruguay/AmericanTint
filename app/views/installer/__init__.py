from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Rollo, Subcodigo, AuditLog
from app.services.email_service import EmailService
from datetime import datetime

installer_bp = Blueprint('installer', __name__)

@installer_bp.route('/')
@login_required
def index():
    # Seguridad: Solo instaladores
    if current_user.role != 'instalador':
        return "<h1>⛔ ACCESO DENEGADO: Área exclusiva para Talleres</h1>", 403

    # Obtener mis rollos
    mis_rollos = Rollo.query.filter_by(user_id=current_user.id, estado='ASIGNADO').all()

    # Pre-calcular datos para la vista
    rollos_data = []
    for rollo in mis_rollos:
        total = len(rollo.subcodigos)
        usados = len([s for s in rollo.subcodigos if s.estado != 'INACTIVO'])
        disponibles = total - usados
        
        # Actualizar estado si se agotó
        if disponibles == 0 and rollo.estado != 'AGOTADO':
            rollo.estado = 'AGOTADO'
            db.session.commit()

        rollos_data.append({
            'obj': rollo,
            'total': total,
            'usados': usados,
            'disponibles': disponibles,
            'porcentaje': (usados / total) * 100 if total > 0 else 100
        })

    # CAMBIO CLAVE: Usamos el template HTML nuevo
    return render_template('installer/index.html', rollos=rollos_data)


@installer_bp.route('/create_warranty', methods=['POST'])
@login_required
def create_warranty():
    if current_user.role != 'instalador':
        return redirect('/')

    rollo_id = request.form.get('rollo_id')
    email_cliente = request.form.get('email')
    patente_ref = request.form.get('patente', '').upper().strip()
    
    if not patente_ref:
        flash('❌ Error: Debes ingresar la patente.', 'danger')
        return redirect(url_for('installer.index'))

    # 1. Buscar y validar
    rollo = Rollo.query.get_or_404(rollo_id)
    if rollo.user_id != current_user.id:
        flash('Error: Ese rollo no es tuyo.', 'danger')
        return redirect(url_for('installer.index'))

    # 2. Buscar cupo
    subcodigo = Subcodigo.query.filter_by(rollo_id=rollo.id, estado='INACTIVO').first()
    if not subcodigo:
        flash('Sin cupos disponibles.', 'danger')
        return redirect(url_for('installer.index'))

    try:
        # 3. Reservar
        subcodigo.estado = 'PENDIENTE'
        subcodigo.cliente_email = email_cliente
        subcodigo.cliente_patente = patente_ref
        db.session.commit()

        # 4. Email
        link = url_for('public.activar_garantia', codigo=subcodigo.codigo_hijo, _external=True)
        EmailService.enviar_activacion(email_cliente, subcodigo.codigo_hijo, link)

        flash(f'📧 Invitación enviada a {email_cliente}.', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'danger')

    return redirect(url_for('installer.index'))