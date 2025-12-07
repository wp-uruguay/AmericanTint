from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from app.extensions import db
from app.models import Producto, User, Rollo, AuditLog
from app.services.stock_service import StockService
from datetime import datetime, timedelta
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/')
@login_required
def index():
    if current_user.role not in ['admin', 'superadmin']:
        return "<h1>⛔ ACCESO DENEGADO</h1>", 403

    # MÉTRICAS DEL DASHBOARD
    hoy = datetime.utcnow()
    inicio_mes = datetime(hoy.year, hoy.month, 1)
    
    if current_user.role == 'superadmin':
        filtro_pais = [] 
    else:
        filtro_pais = [Rollo.codigo_padre.like(f"{current_user.pais}%")]

    query_ventas = Rollo.query.filter(Rollo.estado == 'ASIGNADO', Rollo.fecha_asignacion >= inicio_mes)
    if filtro_pais:
        query_ventas = query_ventas.filter(*filtro_pais)
    
    ventas_mes = query_ventas.count()

    query_top = db.session.query(
        User.username, func.count(Rollo.id)
    ).join(Rollo, User.id == Rollo.user_id)\
     .filter(Rollo.estado.in_(['ASIGNADO', 'AGOTADO']))
    
    if current_user.role != 'superadmin':
        query_top = query_top.filter(User.pais == current_user.pais)
        
    top_chart_data = query_top.group_by(User.username).order_by(func.count(Rollo.id).desc()).limit(5).all()
    
    chart_labels = [row[0] for row in top_chart_data]
    chart_values = [row[1] for row in top_chart_data]

    productos = Producto.query.all()
    stock_por_producto = []
    
    for p in productos:
        q = Rollo.query.filter_by(producto_id=p.id, estado='EN_DEPOSITO')
        if current_user.role != 'superadmin':
            q = q.filter(Rollo.codigo_padre.like(f"{current_user.pais}%"))
        
        cantidad = q.count()
        stock_por_producto.append({'nombre': p.nombre, 'cantidad': cantidad})

    if current_user.role == 'superadmin':
        instaladores = User.query.filter_by(role='instalador').order_by(User.created_at.desc()).limit(10).all()
    else:
        instaladores = User.query.filter_by(role='instalador', pais=current_user.pais).order_by(User.created_at.desc()).limit(10).all()

    return render_template('admin/dashboard_v2.html',
                           ventas_mes=ventas_mes,
                           chart_labels=chart_labels,
                           chart_values=chart_values,
                           stock_productos=stock_por_producto,
                           instaladores=instaladores)

# RUTA 1: VENDER
@admin_bp.route('/vender')
@login_required
def vender():
    if current_user.role == 'superadmin':
        instaladores = User.query.filter_by(role='instalador').all()
    else:
        instaladores = User.query.filter_by(role='instalador', pais=current_user.pais).all()
    return render_template('admin/vender.html', instaladores=instaladores)

# RUTA 2: GESTIONAR STOCK
@admin_bp.route('/stock', methods=['GET', 'POST'])
@login_required
def gestionar_stock():
    if request.method == 'POST':
        producto_id = int(request.form.get('producto_id'))
        cantidad = int(request.form.get('cantidad'))
        pais_destino = request.form.get('pais_destino') if current_user.role == 'superadmin' else current_user.pais
        
        exito, mensaje = StockService.importar_stock(producto_id, cantidad, current_user, pais_destino)
        if exito: flash(mensaje, 'success')
        else: flash(f"Error: {mensaje}", 'danger')
        return redirect(url_for('admin.gestionar_stock'))

    productos = Producto.query.all()
    if current_user.role == 'superadmin':
        rollos = Rollo.query.order_by(Rollo.id.desc()).limit(100).all()
    else:
        rollos = Rollo.query.filter(Rollo.codigo_padre.like(f"{current_user.pais}%")).order_by(Rollo.id.desc()).limit(100).all()
        
    return render_template('admin/stock.html', productos=productos, rollos=rollos)

# RUTA 3: INSTALADORES
@admin_bp.route('/instaladores')
@login_required
def gestionar_instaladores():
    if current_user.role == 'superadmin':
        users = User.query.filter_by(role='instalador').all()
    else:
        users = User.query.filter_by(role='instalador', pais=current_user.pais).all()
    return render_template('admin/instaladores.html', instaladores=users)

# ASIGNAR STOCK (REMITO)
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
    
    # AQUI ESTÁ LA CORRECCIÓN: Renderizamos el nuevo archivo .html
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
            logo_url=request.form.get('logo_url') # <-- GUARDAMOS EL LOGO
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