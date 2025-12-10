from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from app.extensions import db
from app.models import Producto, User, Rollo, AuditLog, Subcodigo
from app.services.stock_service import StockService
from datetime import datetime
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__)

# --- RUTA PRINCIPAL (DASHBOARD) ---
@admin_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if current_user.role not in ['admin', 'superadmin']:
        return "<h1>⛔ ACCESO DENEGADO</h1>", 403

    if request.method == 'POST' and 'importar_stock' in request.form:
        producto_id = int(request.form.get('producto_id'))
        cantidad = int(request.form.get('cantidad'))
        
        pais_destino = request.form.get('pais_destino') if current_user.role == 'superadmin' else current_user.pais
            
        exito, mensaje = StockService.importar_stock(producto_id, cantidad, current_user, pais_destino)
        if exito: flash(mensaje, 'success')
        else: flash(f"Error: {mensaje}", 'danger')
        return redirect(url_for('admin.index'))

    # Métricas Dashboard
    hoy = datetime.utcnow()
    inicio_mes = datetime(hoy.year, hoy.month, 1)
    
    filtro_pais = [] if current_user.role == 'superadmin' else [Rollo.codigo_padre.like(f"{current_user.pais}%")]

    query_ventas = Rollo.query.filter(Rollo.estado == 'ASIGNADO', Rollo.fecha_asignacion >= inicio_mes)
    if filtro_pais: query_ventas = query_ventas.filter(*filtro_pais)
    ventas_mes = query_ventas.count()

    query_top = db.session.query(User.username, func.count(Rollo.id)).join(Rollo, User.id == Rollo.user_id).filter(Rollo.estado.in_(['ASIGNADO', 'AGOTADO']))
    if current_user.role != 'superadmin': query_top = query_top.filter(User.pais == current_user.pais)
    top_chart_data = query_top.group_by(User.username).order_by(func.count(Rollo.id).desc()).limit(5).all()
    
    chart_labels = [row[0] for row in top_chart_data]
    chart_values = [row[1] for row in top_chart_data]

    productos = Producto.query.all()
    stock_por_producto = []
    for p in productos:
        q = Rollo.query.filter_by(producto_id=p.id, estado='EN_DEPOSITO')
        if current_user.role != 'superadmin': q = q.filter(Rollo.codigo_padre.like(f"{current_user.pais}%"))
        stock_por_producto.append({'nombre': p.nombre, 'cantidad': q.count()})

    q_inst = User.query.filter_by(role='instalador').order_by(User.created_at.desc())
    if current_user.role != 'superadmin': q_inst = q_inst.filter_by(pais=current_user.pais)
    instaladores = q_inst.limit(10).all()

    return render_template('admin/dashboard_v2.html',
                           ventas_mes=ventas_mes, chart_labels=chart_labels, chart_values=chart_values,
                           stock_productos=stock_por_producto, instaladores=instaladores)

# --- PERFIL CRM UNIFICADO (INSTALADOR + ACCIONES) ---
@admin_bp.route('/instalador/<int:user_id>', methods=['GET', 'POST'])
@login_required
def ver_instalador(user_id):
    instalador = User.query.get_or_404(user_id)
    
    if current_user.role != 'superadmin' and instalador.pais != current_user.pais:
        flash('No tienes permiso para ver este perfil.', 'danger')
        return redirect(url_for('admin.gestionar_instaladores'))

    # --- MANEJO DE ACCIONES (POST) ---
    if request.method == 'POST':
        accion = request.form.get('accion')

        # 1. ENVIAR STOCK
        if accion == 'transferir':
            rollos_ids = request.form.getlist('rollos_seleccionados')
            if not rollos_ids:
                flash('❌ Debes seleccionar al menos un rollo.', 'warning')
            else:
                count = 0
                for rid in rollos_ids:
                    rollo = Rollo.query.get(rid)
                    if rollo and rollo.user_id == current_user.id and rollo.estado == 'EN_DEPOSITO':
                        rollo.user_id = instalador.id
                        rollo.estado = 'ASIGNADO'
                        rollo.fecha_asignacion = datetime.utcnow()
                        count += 1
                
                db.session.add(AuditLog(user_id=current_user.id, accion='TRANSFERENCIA', detalle=f"Enviados {count} a {instalador.username}"))
                db.session.commit()
                flash(f'✅ Enviados {count} rollos exitosamente.', 'success')
                return redirect(url_for('admin.ver_instalador', user_id=instalador.id, tab='stock'))

        # 2. ENVIAR EMAIL
        elif accion == 'email':
            from app.services.email_service import EmailService
            asunto = request.form.get('asunto')
            mensaje = request.form.get('mensaje')
            
            try:
                EmailService.enviar_mensaje_personalizado(instalador.email, asunto, mensaje)
                flash('✅ Correo enviado correctamente.', 'success')
            except Exception as e:
                flash(f'❌ Error enviando correo: {e}', 'danger')
            return redirect(url_for('admin.ver_instalador', user_id=instalador.id, tab='email'))

    # --- DATOS PARA LA VISTA (GET) ---
    total_rollos = Rollo.query.filter_by(user_id=instalador.id).count()
    rollos_activos = Rollo.query.filter_by(user_id=instalador.id, estado='ASIGNADO').count()
    garantias_generadas = db.session.query(func.count(Subcodigo.id))\
        .join(Rollo, Subcodigo.rollo_id == Rollo.id)\
        .filter(Rollo.user_id == instalador.id, Subcodigo.estado == 'ACTIVADO').scalar() or 0

    historial_stock = Rollo.query.filter_by(user_id=instalador.id).order_by(Rollo.fecha_asignacion.desc()).limit(10).all()
    
    # Stock disponible del Admin para enviar
    stock_para_enviar = Rollo.query.filter_by(user_id=current_user.id, estado='EN_DEPOSITO').all()

    # Prefijos WhatsApp
    prefijos = {'AR': '549', 'UY': '598', 'CL': '569', 'PY': '595', 'PE': '51', 'CO': '57', 'MX': '52'}
    prefijo_pais = prefijos.get(instalador.pais, '')

    active_tab = request.args.get('tab', 'perfil')

    return render_template('admin/perfil_instalador.html', 
                           inst=instalador, 
                           total_rollos=total_rollos,
                           activos=rollos_activos,
                           garantias=garantias_generadas,
                           historial=historial_stock,
                           stock_disponible=stock_para_enviar,
                           prefijo_pais=prefijo_pais,
                           active_tab=active_tab)

# --- OTRAS RUTAS OPERATIVAS ---
@admin_bp.route('/instaladores', methods=['GET', 'POST'])
@login_required
def gestionar_instaladores():
    query = User.query.filter_by(role='instalador')
    if current_user.role != 'superadmin':
        query = query.filter_by(pais=current_user.pais)

    busqueda = request.args.get('q')
    if busqueda:
        query = query.filter((User.username.ilike(f"%{busqueda}%")) | (User.email.ilike(f"%{busqueda}%")))

    users = query.order_by(User.created_at.desc()).all()
    return render_template('admin/instaladores.html', instaladores=users)

@admin_bp.route('/stock', methods=['GET', 'POST'])
@login_required
def gestionar_stock():
    active_tab = request.args.get('tab', 'stock')
    if request.method == 'POST' and 'importar_stock' in request.form:
        producto_id = int(request.form.get('producto_id'))
        cantidad = int(request.form.get('cantidad'))
        pais_destino = request.form.get('pais_destino') if current_user.role == 'superadmin' else current_user.pais
        
        exito, mensaje = StockService.importar_stock(producto_id, cantidad, current_user, pais_destino)
        if exito: flash(mensaje, 'success')
        else: flash(f"Error: {mensaje}", 'danger')
        return redirect(url_for('admin.gestionar_stock', tab='stock'))

    lineas_existentes = db.session.query(Producto.linea).distinct().all()
    lineas = [l[0] for l in lineas_existentes]
    productos = Producto.query.order_by(Producto.nombre.asc()).all()
    
    query = Rollo.query
    if current_user.role != 'superadmin':
        query = query.filter(Rollo.codigo_padre.like(f"{current_user.pais}%"))
    rollos = query.order_by(Rollo.id.desc()).limit(100).all()
        
    return render_template('admin/stock.html', productos=productos, rollos=rollos, lineas=lineas, active_tab=active_tab)

@admin_bp.route('/create_product', methods=['POST'])
@login_required
def create_product():
    if current_user.role not in ['admin', 'superadmin']: return redirect(url_for('admin.index'))
    
    linea_final = request.form.get('linea_nueva').strip() if request.form.get('linea_nueva') else request.form.get('linea_select')
    nombre_final = f"AT {linea_final} {request.form.get('variedad')}"
    
    if Producto.query.filter_by(nombre=nombre_final).first():
        flash('Producto existente.', 'warning')
    else:
        nuevo = Producto(
            nombre=nombre_final, linea=linea_final, variedad=request.form.get('variedad'),
            garantia_anios=int(request.form.get('garantia')), precio=float(request.form.get('precio'))
        )
        db.session.add(nuevo)
        db.session.commit()
        flash(f'Producto creado: {nombre_final}', 'success')
    return redirect(url_for('admin.gestionar_stock', tab='precios'))

@admin_bp.route('/update_price', methods=['POST'])
@login_required
def update_price():
    if current_user.role not in ['admin', 'superadmin']: return redirect(url_for('admin.index'))
    prod = Producto.query.get(request.form.get('producto_id'))
    if prod:
        prod.precio = float(request.form.get('precio'))
        db.session.commit()
        flash('Precio actualizado.', 'success')
    return redirect(url_for('admin.gestionar_stock', tab='precios'))

@admin_bp.route('/vender')
@login_required
def vender():
    q = User.query.filter_by(role='instalador')
    if current_user.role != 'superadmin': q = q.filter_by(pais=current_user.pais)
    return render_template('admin/vender.html', instaladores=q.all())

# Mantenemos esta ruta para retrocompatibilidad, aunque ahora la lógica principal está en ver_instalador
@admin_bp.route('/assign_stock/<int:user_id>', methods=['GET', 'POST'])
@login_required
def assign_stock(user_id):
    # Redirigimos al nuevo perfil en la pestaña de stock
    return redirect(url_for('admin.ver_instalador', user_id=user_id, tab='stock'))

@admin_bp.route('/create_installer', methods=['POST'])
@login_required
def create_installer():
    try:
        pais = request.form.get('pais') if current_user.role == 'superadmin' else current_user.pais
        user = User(
            username=request.form['username'], email=request.form['email'],
            password_hash=generate_password_hash(request.form['password']), role='instalador', pais=pais,
            nombre_responsable=request.form.get('responsable'), telefono_negocio=request.form.get('telefono'),
            direccion_negocio=request.form.get('direccion'), logo_url=request.form.get('logo_url')
        )
        db.session.add(user)
        db.session.commit()
        flash('Instalador creado.', 'success')
    except Exception as e: flash(f'Error: {e}', 'danger')
    return redirect(url_for('admin.gestionar_instaladores'))

@admin_bp.route('/delete_user/<int:user_id>')
@login_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('Usuario eliminado.', 'info')
    return redirect(request.referrer or url_for('admin.index'))

@admin_bp.route('/create_admin', methods=['POST'])
@login_required
def create_country_admin():
    if current_user.role != 'superadmin': return redirect(url_for('admin.index'))
    try:
        user = User(username=request.form['username'], email=request.form['email'],
                    password_hash=generate_password_hash(request.form['password']), role='admin', pais=request.form['pais'])
        db.session.add(user)
        db.session.commit()
        flash('Admin creado.', 'success')
    except Exception as e: flash(f'Error: {e}', 'danger')
    return redirect(url_for('admin.index'))