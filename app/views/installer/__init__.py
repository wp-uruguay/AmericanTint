from flask import Blueprint, render_template_string, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Rollo, Subcodigo, AuditLog
from datetime import datetime

installer_bp = Blueprint('installer', __name__)

@installer_bp.route('/')
@login_required
def index():
    # Seguridad: Solo instaladores
    if current_user.role != 'instalador':
        return "<h1>⛔ ACCESO DENEGADO: Área exclusiva para Talleres</h1>", 403

    # Obtener mis rollos (Solo los que ya me asignaron)
    mis_rollos = Rollo.query.filter_by(user_id=current_user.id, estado='ASIGNADO').all()

    # Pre-calcular datos para la vista (cuántos cupos quedan)
    rollos_data = []
    for rollo in mis_rollos:
        total = len(rollo.subcodigos) # Deberían ser 15
        usados = len([s for s in rollo.subcodigos if s.estado != 'INACTIVO'])
        disponibles = total - usados
        
        # Si se acabaron los cupos, marcamos el rollo como AGOTADO
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

    html = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    </head>
    <body class="bg-light p-4">
    <div class="container" style="max_width: 900px;">
        
        <div class="d-flex justify-content-between align-items-center mb-4 bg-white p-3 rounded shadow-sm">
            <h2 class="text-primary m-0">
                <i class="fa fa-wrench"></i> Taller: {{ current_user.username }}
            </h2>
            <div>
                <span class="badge bg-secondary me-2">{{ current_user.pais }}</span>
                <a href="/logout" class="btn btn-outline-dark btn-sm">Salir</a>
            </div>
        </div>

        {% with messages = get_flashed_messages(with_categories=true) %}
          {% if messages %}
            {% for category, message in messages %}
              <div class="alert alert-{{ category }} alert-dismissible fade show">
                {{ message }} <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
              </div>
            {% endfor %}
          {% endif %}
        {% endwith %}

        <h4 class="mb-3">📦 Mis Rollos Disponibles</h4>
        
        <div class="row">
            {% for item in rollos %}
            <div class="col-md-6 mb-4">
                <div class="card h-100 border-{{ 'secondary' if item.disponibles == 0 else 'primary' }} shadow-sm">
                    <div class="card-header d-flex justify-content-between align-items-center {{ 'bg-secondary text-white' if item.disponibles == 0 else 'bg-primary text-white' }}">
                        <strong>{{ item.obj.codigo_padre }}</strong>
                        <span class="badge bg-light text-dark">Quedan: {{ item.disponibles }}</span>
                    </div>
                    <div class="card-body">
                        <h5 class="card-title">Rollo American Tint</h5>
                        <p class="card-text text-muted small">
                            ID Interno: {{ item.obj.id }} <br>
                            Recibido: {{ item.obj.fecha_asignacion.strftime('%d/%m/%Y') if item.obj.fecha_asignacion else 'Reciente' }}
                        </p>
                        
                        <div class="progress mb-3" style="height: 20px;">
                            <div class="progress-bar bg-warning" role="progressbar" style="width: {{ item.porcentaje }}%;">
                                {{ item.usados }} Usados
                            </div>
                        </div>

                        {% if item.disponibles > 0 %}
                            <button class="btn btn-success w-100" data-bs-toggle="modal" data-bs-target="#modalGarantia{{ item.obj.id }}">
                                <i class="fa fa-certificate"></i> Generar Nueva Garantía
                            </button>
                        {% else %}
                            <button class="btn btn-secondary w-100" disabled>Rollo Agotado</button>
                        {% endif %}
                    </div>
                </div>

                <div class="modal fade" id="modalGarantia{{ item.obj.id }}" tabindex="-1">
                    <div class="modal-dialog">
                        <div class="modal-content">
                            <form action="{{ url_for('installer.create_warranty') }}" method="POST">
                                <div class="modal-header bg-success text-white">
                                    <h5 class="modal-title">Registrar Instalación</h5>
                                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                                </div>
                                <div class="modal-body">
                                    <input type="hidden" name="rollo_id" value="{{ item.obj.id }}">
                                    <p>Estás usando un cupo del rollo: <strong>{{ item.obj.codigo_padre }}</strong></p>
                                    
                                    <div class="mb-3">
                                        <label class="form-label">Patente del Vehículo</label>
                                        <input type="text" name="patente" class="form-control" required placeholder="Ej: AA123BB" style="text-transform: uppercase;">
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label">Email del Cliente</label>
                                        <input type="email" name="email" class="form-control" required placeholder="cliente@email.com">
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label">Nombre del Cliente</label>
                                        <input type="text" name="nombre" class="form-control" required>
                                    </div>
                                </div>
                                <div class="modal-footer">
                                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                                    <button type="submit" class="btn btn-success">Generar y Enviar</button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>

            </div>
            {% else %}
            <div class="col-12">
                <div class="alert alert-warning text-center">
                    <h4>😕 No tienes rollos asignados.</h4>
                    <p>Contacta al administrador para que te envíe stock.</p>
                </div>
            </div>
            {% endfor %}
        </div>

        <h4 class="mt-4">📋 Historial Reciente</h4>
        <div class="table-responsive">
            <table class="table table-striped table-sm">
                <thead><tr><th>Código Garantía</th><th>Patente</th><th>Cliente</th><th>Estado</th></tr></thead>
                <tbody>
                    <tr><td colspan="4" class="text-center text-muted">Aún no hay instalaciones registradas.</td></tr>
                </tbody>
            </table>
        </div>

    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """
    return render_template_string(html, rollos=rollos_data)

@installer_bp.route('/create_warranty', methods=['POST'])
@login_required
def create_warranty():
    if current_user.role != 'instalador':
        flash('Acceso denegado', 'danger')
        return redirect('/')

    rollo_id = request.form.get('rollo_id')
    patente = request.form.get('patente').upper()
    email = request.form.get('email')
    nombre_cliente = request.form.get('nombre')

    # 1. Buscar el rollo y verificar que sea mío
    rollo = Rollo.query.get_or_404(rollo_id)
    if rollo.user_id != current_user.id:
        flash('Error de seguridad: Ese rollo no es tuyo.', 'danger')
        return redirect(url_for('installer.index'))

    # 2. Buscar un subcódigo libre (INACTIVO)
    subcodigo_libre = Subcodigo.query.filter_by(rollo_id=rollo.id, estado='INACTIVO').first()

    if not subcodigo_libre:
        flash('¡Este rollo ya no tiene cupos disponibles!', 'danger')
        return redirect(url_for('installer.index'))

    try:
        # 3. Asignar (Consumir cupo)
        # Aquí marcamos como ACTIVADO directamente para el MVP, 
        # o PENDIENTE si requieres que el cliente haga clic en un email.
        subcodigo_libre.estado = 'ACTIVADO' 
        subcodigo_libre.cliente_patente = patente
        subcodigo_libre.cliente_email = email
        subcodigo_libre.cliente_nombre = nombre_cliente
        subcodigo_libre.fecha_activacion = datetime.utcnow()
        
        # Calcular vencimiento (Lógica simple: hoy + años del producto)
        # Necesitamos acceder al producto a través del rollo
        # (Esto requeriría un join o relationship, asumimos 6 años por defecto si falla)
        anios_garantia = 6 # Default
        # TODO: Implementar lógica de fecha real basada en producto.garantia_anios
        
        db.session.commit()

        # 4. Auditoría
        db.session.add(AuditLog(
            user_id=current_user.id, 
            accion='NUEVA_GARANTIA', 
            detalle=f"Garantía {subcodigo_libre.codigo_hijo} para patente {patente}"
        ))
        db.session.commit()

        # 5. Feedback (Simulación de Email)
        mensaje_exito = f"""
        ✅ ¡Garantía Generada! <br>
        <strong>Código:</strong> {subcodigo_libre.codigo_hijo} <br>
        <strong>Cliente:</strong> {nombre_cliente} <br>
        (En un sistema real, aquí se enviaría el email).
        """
        flash(mensaje_exito, 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error al procesar: {str(e)}', 'danger')

    return redirect(url_for('installer.index'))