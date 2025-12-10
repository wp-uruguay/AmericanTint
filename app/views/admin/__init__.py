from flask import Blueprint, render_template, render_template_string, request, flash, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from app.extensions import db
from app.models import Producto, User, Rollo, AuditLog
from app.services.stock_service import StockService
from datetime import datetime, timedelta
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__)

# --- RUTA PRINCIPAL (DASHBOARD) ---
@admin_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if current_user.role not in ['admin', 'superadmin']:
        return "<h1>⛔ ACCESO DENEGADO</h1>", 403

    # Lógica de Importación de Stock (POST)
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

    # --- MÉTRICAS Y CONSULTAS (GET) ---
    hoy = datetime.utcnow()
    inicio_mes = datetime(hoy.year, hoy.month, 1)
    
    if current_user.role == 'superadmin':
        filtro_pais = [] 
    else:
        filtro_pais = [Rollo.codigo_padre.like(f"{current_user.pais}%")]

    # 1. Ventas del Mes
    query_ventas = Rollo.query.filter(Rollo.estado == 'ASIGNADO', Rollo.fecha_asignacion >= inicio_mes)
    if filtro_pais:
        query_ventas = query_ventas.filter(*filtro_pais)
    ventas_mes = query_ventas.count()

    # 2. Gráfico Top Instaladores
    query_top = db.session.query(
        User.username, func.count(Rollo.id)
    ).join(Rollo, User.id == Rollo.user_id)\
     .filter(Rollo.estado.in_(['ASIGNADO', 'AGOTADO']))
    
    if current_user.role != 'superadmin':
        query_top = query_top.filter(User.pais == current_user.pais)
        
    top_chart_data = query_top.group_by(User.username).order_by(func.count(Rollo.id).desc()).limit(5).all()
    
    chart_labels = [row[0] for row in top_chart_data]
    chart_values = [row[1] for row in top_chart_data]

    # 3. Stock Resumido
    productos = Producto.query.all()
    stock_por_producto = []
    
    for p in productos:
        q = Rollo.query.filter_by(producto_id=p.id, estado='EN_DEPOSITO')
        if current_user.role != 'superadmin':
            q = q.filter(Rollo.codigo_padre.like(f"{current_user.pais}%"))
        
        cantidad = q.count()
        stock_por_producto.append({'nombre': p.nombre, 'cantidad': cantidad})

    # 4. Instaladores Recientes
    if current_user.role == 'superadmin':
        instaladores = User.query.filter_by(role='instalador').order_by(User.created_at.desc()).limit(10).all()
        admins_pais = User.query.filter_by(role='admin').all()
        rollos = Rollo.query.order_by(Rollo.id.desc()).limit(50).all()
    else:
        instaladores = User.query.filter_by(role='instalador', pais=current_user.pais).order_by(User.created_at.desc()).limit(10).all()
        admins_pais = [] 
        rollos = Rollo.query.filter(Rollo.codigo_padre.like(f"{current_user.pais}%")).order_by(Rollo.id.desc()).limit(50).all()

    return render_template('admin/dashboard_v2.html',
                           ventas_mes=ventas_mes,
                           chart_labels=chart_labels,
                           chart_values=chart_values,
                           stock_productos=stock_por_producto,
                           instaladores=instaladores)

# --- GESTIÓN DE STOCK Y CATÁLOGO ---
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

    # Filtros y datos
    lineas_existentes = db.session.query(Producto.linea).distinct().all()
    lineas = [l[0] for l in lineas_existentes]

    productos = Producto.query.order_by(Producto.nombre.asc()).all()
    
    query = Rollo.query
    if current_user.role != 'superadmin':
        query = query.filter(Rollo.codigo_padre.like(f"{current_user.pais}%"))
    
    rollos = query.order_by(Rollo.id.desc()).limit(100).all()
        
    return render_template('admin/stock.html', 
                           productos=productos, 
                           rollos=rollos, 
                           lineas=lineas, 
                           active_tab=active_tab)

# --- CREAR PRODUCTO (Variante) ---
@admin_bp.route('/create_product', methods=['POST'])
@login_required
def create_product():
    if current_user.role not in ['admin', 'superadmin']:
        return redirect(url_for('admin.index'))
    
    linea_select = request.form.get('linea_select')
    linea_nueva = request.form.get('linea_nueva')
    linea_final = linea_nueva.strip() if linea_nueva else linea_select
    
    variedad = request.form.get('variedad')
    garantia = int(request.form.get('garantia'))
    precio = float(request.form.get('precio'))
    
    nombre_final = f"AT {linea_final} {variedad}"
    
    if Producto.query.filter_by(nombre=nombre_final).first():
        flash('Ese producto ya existe.', 'warning')
    else:
        nuevo_prod = Producto(
            nombre=nombre_final,
            linea=linea_final,
            variedad=variedad,
            garantia_anios=garantia,
            precio=precio
        )
        db.session.add(nuevo_prod)
        db.session.commit()
        flash(f'Producto creado: {nombre_final}', 'success')
    
    return redirect(url_for('admin.gestionar_stock', tab='precios'))

# --- ACTUALIZAR PRECIO ---
@admin_bp.route('/update_price', methods=['POST'])
@login_required
def update_price():
    if current_user.role not in ['admin', 'superadmin']:
        return redirect(url_for('admin.index'))
    
    prod_id = request.form.get('producto_id')
    nuevo_precio = request.form.get('precio')
    
    producto = Producto.query.get(prod_id)
    if producto:
        producto.precio = float(nuevo_precio)
        db.session.commit()
        flash(f'Precio de {producto.nombre} actualizado.', 'success')
    
    return redirect(url_for('admin.gestionar_stock', tab='precios'))

# --- RUTAS RESTANTES (Vender, Instaladores, etc) ---

@admin_bp.route('/vender')
@login_required
def vender():
    if current_user.role == 'superadmin':
        instaladores = User.query.filter_by(role='instalador').all()
    else:
        instaladores = User.query.filter_by(role='instalador', pais=current_user.pais).all()
    return render_template('admin/vender.html', instaladores=instaladores)

@admin_bp.route('/instaladores')
@login_required
def gestionar_instaladores():
    if current_user.role == 'superadmin':
        users = User.query.filter_by(role='instalador').all()
    else:
        users = User.query.filter_by(role='instalador', pais=current_user.pais).all()
    return render_template('admin/instaladores.html', instaladores=users)

@admin_bp.route('/assign_stock/<int:user_id>', methods=['GET', 'POST'])
@login_required
def assign_stock(user_id):
    instalador = User.query.get_or_404(user_id)
    if request.method == 'POST':
        rollos_ids = request.form.getlist('rollos_seleccionados')
        if not rollos_ids:
            flash('Selecciona al menos un rollo.', 'warning')
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
            flash(f'✅ Enviados {count} rollos a {instalador.username}.', 'success')
            return redirect(url_for('admin.vender'))

    stock_disponible = Rollo.query.filter_by(user_id=current_user.id, estado='EN_DEPOSITO').all()
    return render_template('admin/assign_stock.html', instalador=instalador, stock=stock_disponible)

@admin_bp.route('/create_installer', methods=['POST'])
@login_required
def create_installer():
    try:
        pais = request.form.get('pais') if current_user.role == 'superadmin' else current_user.pais
        new_user = User(
            username=request.form['username'],
            email=request.form['email'],
            password_hash=generate_password_hash(request.form['password']),
            role='instalador',
            pais=pais,
            nombre_responsable=request.form.get('responsable'),
            telefono_negocio=request.form.get('telefono'),
            direccion_negocio=request.form.get('direccion'),
            logo_url=request.form.get('logo_url')
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Instalador creado.', 'success')
    except Exception as e:
        flash(f'Error: {e}', 'danger')
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