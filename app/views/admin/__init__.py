from flask import Blueprint, render_template_string, request, flash, redirect, url_for
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
    if current_user.role not in ['admin', 'superadmin']:
        return "<h1>⛔ ACCESO DENEGADO</h1>", 403

    # Lógica de Importación de Stock
    if request.method == 'POST' and 'importar_stock' in request.form:
        producto_id = int(request.form.get('producto_id'))
        cantidad = int(request.form.get('cantidad'))
        
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

    # --- CONSULTAS DB ---
    productos = Producto.query.all()
    
    # 1. Traer Instaladores
    if current_user.role == 'superadmin':
        instaladores = User.query.filter_by(role='instalador').all()
        admins_pais = User.query.filter_by(role='admin').all()
        rollos = Rollo.query.order_by(Rollo.id.desc()).limit(50).all()
    else:
        instaladores = User.query.filter_by(role='instalador', pais=current_user.pais).all()
        admins_pais = [] 
        rollos = Rollo.query.filter(Rollo.codigo_padre.like(f"{current_user.pais}%")).order_by(Rollo.id.desc()).limit(50).all()

    # --- HTML ---
    html = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    </head>
    <body class="bg-light p-4">
    <div class="container bg-white p-4 shadow rounded">
        
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h1 class="text-danger">
                🔴 Panel {{ 'GLOBAL (CEO)' if current_user.role == 'superadmin' else 'PAÍS: ' + current_user.pais }}
            </h1>
            <div>
                <span class="me-3">Hola, <strong>{{ current_user.username }}</strong></span>
                <a href="/logout" class="btn btn-outline-danger btn-sm">Salir</a>
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

        {% if current_user.role == 'superadmin' %}
        <div class="card mb-4 border-primary">
            <div class="card-header bg-primary text-white">🌎 Gestión de Gerentes de País</div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-4">
                        <form action="{{ url_for('admin.create_country_admin') }}" method="POST">
                            <input type="text" name="username" class="form-control mb-2" placeholder="Nombre Gerente" required>
                            <input type="email" name="email" class="form-control mb-2" placeholder="Email" required>
                            <input type="password" name="password" class="form-control mb-2" placeholder="Contraseña" required>
                            <select name="pais" class="form-select mb-2" required>
                                <option value="" disabled selected>País...</option>
                                <option value="AR">🇦🇷 Argentina</option>
                                <option value="UY">🇺🇾 Uruguay</option>
                                <option value="CL">🇨🇱 Chile</option>
                                <option value="PY">🇵🇾 Paraguay</option>
                            </select>
                            <button type="submit" class="btn btn-sm btn-primary w-100">Crear Admin</button>
                        </form>
                    </div>
                    <div class="col-md-8">
                        <table class="table table-sm">
                            <thead><tr><th>País</th><th>Nombre</th><th>Email</th><th></th></tr></thead>
                            <tbody>
                                {% for adm in admins_pais %}
                                <tr>
                                    <td>{{ adm.pais }}</td><td>{{ adm.username }}</td><td>{{ adm.email }}</td>
                                    <td><a href="{{ url_for('admin.delete_user', user_id=adm.id) }}" class="text-danger"><i class="fa fa-trash"></i></a></td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
        {% endif %}

        <div class="card mb-4 border-info">
            <div class="card-header bg-info text-white">🛠️ Gestión de Talleres / Instaladores</div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-4 border-end">
                        <h5 class="mb-3">➕ Nuevo Taller</h5>
                        <form action="{{ url_for('admin.create_installer') }}" method="POST">
                            <div class="mb-2"><input type="text" name="username" class="form-control" required placeholder="Ej: Parabrisas Juan"></div>
                            <div class="mb-2"><input type="email" name="email" class="form-control" required placeholder="Email"></div>
                            <div class="mb-2"><input type="password" name="password" class="form-control" required placeholder="Contraseña"></div>
                            {% if current_user.role == 'superadmin' %}
                            <div class="mb-2">
                                <select name="pais" class="form-select" required>
                                    <option value="AR">🇦🇷 Argentina</option>
                                    <option value="UY">🇺🇾 Uruguay</option>
                                    <option value="CL">🇨🇱 Chile</option>
                                </select>
                            </div>
                            {% endif %}
                            <button type="submit" class="btn btn-info text-white w-100 mt-2">Dar de Alta Taller</button>
                        </form>
                    </div>

                    <div class="col-md-8">
                        <h5 class="mb-3">📋 Cartera de Clientes ({{ instaladores|length }})</h5>
                        <div class="table-responsive" style="max_height: 300px; overflow-y: auto;">
                            <table class="table table-hover table-sm">
                                <thead class="table-light">
                                    <tr>
                                        <th>Nombre</th>
                                        <th>Email</th>
                                        <th>Stock</th>
                                        <th>Acción</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for inst in instaladores %}
                                    <tr>
                                        <td>{{ inst.username }}</td>
                                        <td>{{ inst.email }}</td>
                                        <td>
                                            {% set stock_inst = inst.rollos|selectattr("estado", "equalto", "ASIGNADO")|list|length %}
                                            <span class="badge bg-secondary">{{ stock_inst }} Rollos</span>
                                        </td>
                                        <td>
                                            <a href="{{ url_for('admin.assign_stock', user_id=inst.id) }}" class="btn btn-success btn-sm py-0" title="Enviar Stock">
                                                <i class="fa fa-box"></i> Enviar
                                            </a>
                                            <a href="{{ url_for('admin.delete_user', user_id=inst.id) }}" class="btn btn-danger btn-sm py-0" onclick="return confirm('¿Borrar taller?')"><i class="fa fa-trash"></i></a>
                                        </td>
                                    </tr>
                                    {% else %}
                                    <tr><td colspan="4" class="text-center text-muted">No hay instaladores registrados.</td></tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="card mb-4 border-danger">
            <div class="card-header bg-danger text-white">📦 Importar Stock al Depósito</div>
            <div class="card-body">
                <form method="POST">
                    <input type="hidden" name="importar_stock" value="1">
                    <div class="row g-3">
                        <div class="col-md-4">
                            <select name="producto_id" class="form-select" required>
                                {% for p in productos %}
                                    <option value="{{ p.id }}">{{ p.nombre }}</option>
                                {% endfor %}
                            </select>
                        </div>
                        <div class="col-md-2">
                            <input type="number" name="cantidad" class="form-control" value="1" min="1" placeholder="Cant." required>
                        </div>
                        {% if current_user.role == 'superadmin' %}
                        <div class="col-md-3">
                            <select name="pais_destino" class="form-select" required>
                                <option value="AR">🇦🇷 Argentina</option>
                                <option value="UY">🇺🇾 Uruguay</option>
                                <option value="CL">🇨🇱 Chile</option>
                                <option value="PY">🇵🇾 Paraguay</option>
                            </select>
                        </div>
                        {% endif %}
                        <div class="col-md-3">
                            <button type="submit" class="btn btn-success w-100">Generar</button>
                        </div>
                    </div>
                </form>
            </div>
        </div>

        <h3 class="mt-5">📜 Stock en Depósito Central ({{ rollos|length }})</h3>
        <div class="table-responsive">
            <table class="table table-striped table-bordered">
                <thead class="table-dark">
                    <tr>
                        <th>ID</th>
                        <th>Código Rollo</th>
                        <th>Estado</th>
                        <th>Ubicación</th>
                        <th>Fecha Ingreso</th>
                    </tr>
                </thead>
                <tbody>
                    {% for rollo in rollos %}
                    <tr>
                        <td>{{ rollo.id }}</td>
                        <td>
                            <span class="badge bg-warning text-dark" style="font-size: 1em;">{{ rollo.codigo_padre }}</span>
                        </td>
                        <td>
                            {% if rollo.estado == 'EN_DEPOSITO' %}
                                <span class="badge bg-success">En Depósito</span>
                            {% elif rollo.estado == 'ASIGNADO' %}
                                <span class="badge bg-info text-dark">En Taller</span>
                            {% else %}
                                <span class="badge bg-secondary">{{ rollo.estado }}</span>
                            {% endif %}
                        </td>
                        <td>
                            {% if rollo.propietario.id == current_user.id %}
                                <span class="text-success fw-bold">Mí Stock</span>
                            {% else %}
                                {{ rollo.propietario.username }}
                            {% endif %}
                        </td>
                        <td>{{ rollo.fecha_creacion.strftime('%d-%m-%Y') }}</td>
                    </tr>
                    {% else %}
                    <tr><td colspan="5" class="text-center p-3">No hay stock cargado aún.</td></tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """
    return render_template_string(html, productos=productos, rollos=rollos, admins_pais=admins_pais, instaladores=instaladores)

# --- NUEVA RUTA: ASIGNAR STOCK (REMITO DIGITAL) ---
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
    # Solo mostramos rollos que sean propiedad del admin actual y estén EN_DEPOSITO
    stock_disponible = Rollo.query.filter_by(user_id=current_user.id, estado='EN_DEPOSITO').all()

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
                            <td>AT Rollo (ID: {{ rollo.producto_id }})</td> </tr>
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

# --- RUTAS EXISTENTES (CREAR/BORRAR) ---
@admin_bp.route('/create_admin', methods=['POST'])
@login_required
def create_country_admin():
    # ... (Mismo código de antes)
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
    # ... (Mismo código de antes)
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
    # ... (Mismo código de antes)
    user = User.query.get_or_404(user_id)
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