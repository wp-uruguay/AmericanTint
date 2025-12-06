from flask import Blueprint, render_template, render_template_string, request, flash, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from app.extensions import db
from app.models import Producto, User, Rollo, AuditLog
from app.services.stock_service import StockService
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

# --- RUTA PRINCIPAL (DASHBOARD) ---
@admin_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    # Seguridad: Solo Admins y Superadmins
    if current_user.role not in ['admin', 'superadmin']:
        return "<h1>⛔ ACCESO DENEGADO</h1>", 403

    # 1. Lógica de Importación de Stock (POST)
    if request.method == 'POST' and 'importar_stock' in request.form:
        producto_id = int(request.form.get('producto_id'))
        cantidad = int(request.form.get('cantidad'))
        
        # Si es superadmin elige país, si es admin local usa el suyo
        if current_user.role == 'superadmin':
            pais_destino = request.form.get('pais_destino')
        else:
            pais_destino = current_user.pais
            
        exito, mensaje = StockService.importar_stock(producto_id, cantidad, current_user, pais_destino)
        
        if exito:
            flash(mensaje, 'success')
        else:
            flash(f"Error: {mensaje}", 'danger')
        
        return redirect(url_for('admin.index'))

    # 2. Consultas a Base de Datos (GET)
    productos = Producto.query.all()
    
    if current_user.role == 'superadmin':
        # SuperAdmin ve todo
        instaladores = User.query.filter_by(role='instalador').all()
        admins_pais = User.query.filter_by(role='admin').all()
        rollos = Rollo.query.order_by(Rollo.id.desc()).limit(50).all()
    else:
        # Admin Local ve solo su país
        instaladores = User.query.filter_by(role='instalador', pais=current_user.pais).all()
        admins_pais = [] 
        rollos = Rollo.query.filter(Rollo.codigo_padre.like(f"{current_user.pais}%")).order_by(Rollo.id.desc()).limit(50).all()

    # 3. Renderizado (AHORA USAMOS EL ARCHIVO HTML)
    return render_template('admin/index.html', 
                           productos=productos, 
                           rollos=rollos, 
                           admins_pais=admins_pais, 
                           instaladores=instaladores)


# --- RUTA: ASIGNAR STOCK (REMITO DIGITAL) ---
@admin_bp.route('/assign_stock/<int:user_id>', methods=['GET', 'POST'])
@login_required
def assign_stock(user_id):
    instalador = User.query.get_or_404(user_id)
    
    # Procesar la transferencia
    if request.method == 'POST':
        rollos_ids = request.form.getlist('rollos_seleccionados')
        if not rollos_ids:
            flash('Debes seleccionar al menos un rollo.', 'warning')
        else:
            count = 0
            for rid in rollos_ids:
                rollo = Rollo.query.get(rid)
                # Verificar que el rollo sea mío y esté disponible
                if rollo and rollo.user_id == current_user.id and rollo.estado == 'EN_DEPOSITO':
                    rollo.user_id = instalador.id  # Cambio de dueño
                    rollo.estado = 'ASIGNADO'      # Cambio de estado
                    rollo.fecha_asignacion = datetime.utcnow()
                    count += 1
            
            # Auditoría
            log = AuditLog(
                user_id=current_user.id,
                accion='TRANSFERENCIA_STOCK',
                detalle=f"Enviados {count} rollos a {instalador.username}"
            )
            db.session.add(log)
            db.session.commit()
            flash(f'✅ ¡Éxito! Se transfirieron {count} rollos a {instalador.username}.', 'success')
            return redirect(url_for('admin.index'))

    # Mostrar stock disponible para enviar
    stock_disponible = Rollo.query.filter_by(user_id=current_user.id, estado='EN_DEPOSITO').all()

    # Mantenemos este HTML aquí por ahora para no complicar la migración
    # (Luego podemos moverlo a templates/admin/assign_stock.html)
    html_assign = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body class="bg-light p-5">
    <div class="container bg-white p-5 shadow rounded" style="max_width: 800px;">
        <h2 class="mb-4">📦 Enviar Mercadería a: <span class="text-primary">{{ instalador.username }}</span></h2>
        
        <div class="alert alert-info">
            Selecciona los rollos físicos que estás entregando. Estos pasarán al stock del instalador inmediatamente.
        </div>

        <form method="POST">
            <div class="table-responsive mb-4" style="max_height: 400px; overflow-y: auto;">
                <table class="table table-bordered table-hover">
                    <thead class="table-dark sticky-top">
                        <tr>
                            <th width="50" class="text-center">✔</th>
                            <th>Código de Rollo</th>
                            <th>Producto</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for rollo in stock %}
                        <tr>
                            <td class="text-center">
                                <input type="checkbox" name="rollos_seleccionados" value="{{ rollo.id }}" class="form-check-input" style="transform: scale(1.3);">
                            </td>
                            <td class="fw-bold">{{ rollo.codigo_padre }}</td>
                            <td>
                                {% if rollo.producto_info %}
                                    {{ rollo.producto_info.nombre }}
                                {% else %}
                                    Producto ID {{ rollo.producto_id }}
                                {% endif %}
                            </td>
                        </tr>
                        {% else %}
                        <tr><td colspan="3" class="text-center text-danger">No tienes rollos disponibles en tu depósito. ¡Importa primero!</td></tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>

            <div class="d-flex justify-content-between">
                <a href="{{ url_for('admin.index') }}" class="btn btn-secondary">Cancelar</a>
                <button type="submit" class="btn btn-success btn-lg">🚀 Confirmar Transferencia</button>
            </div>
        </form>
    </div>
    </body>
    </html>
    """
    return render_template_string(html_assign, instalador=instalador, stock=stock_disponible)


# --- RUTAS DE GESTIÓN (CREAR/BORRAR) ---

@admin_bp.route('/create_admin', methods=['POST'])
@login_required
def create_country_admin():
    if current_user.role != 'superadmin':
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('admin.index'))
    
    try:
        new_user = User(
            username=request.form['username'],
            email=request.form['email'],
            password_hash=generate_password_hash(request.form['password']),
            role='admin',
            pais=request.form['pais']
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Admin de país creado.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'danger')
        
    return redirect(url_for('admin.index'))

@admin_bp.route('/create_installer', methods=['POST'])
@login_required
def create_installer():
    if current_user.role not in ['admin', 'superadmin']:
        flash('No tienes permisos.', 'danger')
        return redirect(url_for('admin.index'))
    
    try:
        pais = request.form.get('pais') if current_user.role == 'superadmin' else current_user.pais
        
        new_installer = User(
            username=request.form['username'],
            email=request.form['email'],
            password_hash=generate_password_hash(request.form['password']),
            role='instalador',
            pais=pais
        )
        db.session.add(new_installer)
        db.session.commit()
        flash(f'Taller {new_installer.username} creado exitosamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al crear taller: {str(e)}', 'danger')
        
    return redirect(url_for('admin.index'))

@admin_bp.route('/delete_user/<int:user_id>')
@login_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    # Seguridad: Un Admin AR no puede borrar a un Instalador de CL
    if current_user.role != 'superadmin' and user.pais != current_user.pais:
        flash('No puedes borrar usuarios de otro país.', 'danger')
        return redirect(url_for('admin.index'))

    if user.role == 'superadmin':
        flash('No puedes borrar al Jefe.', 'warning')
    else:
        db.session.delete(user)
        db.session.commit()
        flash('Usuario eliminado.', 'info')
        
    return redirect(url_for('admin.index'))