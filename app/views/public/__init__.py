from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.extensions import db
from app.models import Subcodigo, AuditLog
from datetime import datetime

public_bp = Blueprint('public', __name__)

@public_bp.route('/activar/<codigo>', methods=['GET', 'POST'])
def activar_garantia(codigo):
    garantia_previa = Subcodigo.query.filter_by(codigo_hijo=codigo).first()
    
    # Precargar datos
    patente_sugerida = garantia_previa.cliente_patente if garantia_previa else ''
    nombre_taller = "Taller Autorizado"
    if garantia_previa and garantia_previa.rollo_padre.propietario:
        nombre_taller = garantia_previa.rollo_padre.propietario.username

    if request.method == 'POST':
        codigo_final = request.form.get('codigo_manual', '').strip()
        garantia = Subcodigo.query.filter_by(codigo_hijo=codigo_final).first()

        if not garantia:
            flash('❌ Código incorrecto.', 'danger')
            return render_template('public/activar.html', codigo=codigo_final, patente_ref='', taller='')

        if garantia.estado == 'ACTIVADO':
            return redirect(url_for('public.ver_certificado', codigo=garantia.codigo_hijo))

        try:
            garantia.cliente_nombre = request.form['nombre']
            garantia.cliente_telefono = request.form['telefono']
            garantia.cliente_patente = request.form['patente'].upper().strip()
            
            # Guardar reseña
            garantia.instalador_correcto = (request.form.get('instalador_ok') == 'si')
            garantia.review_texto = request.form.get('review_texto')
            garantia.review_stars = int(request.form.get('rating', 0))

            garantia.fecha_activacion = datetime.utcnow()
            garantia.estado = 'ACTIVADO'
            db.session.commit()
            
            return redirect(url_for('public.ver_certificado', codigo=garantia.codigo_hijo))
            
        except Exception as e:
            db.session.rollback()
            flash(f"Error: {str(e)}", 'danger')

    return render_template('public/activar.html', 
                           codigo=codigo, 
                           patente_ref=patente_sugerida,
                           taller=nombre_taller)


@public_bp.route('/certificado/<codigo>')
def ver_certificado(codigo):
    garantia = Subcodigo.query.filter_by(codigo_hijo=codigo, estado='ACTIVADO').first_or_404()
    
    nombre_producto = "Producto American Tint"
    if garantia.rollo_padre and garantia.rollo_padre.producto_info:
        nombre_producto = garantia.rollo_padre.producto_info.nombre

    nombre_instalador = "Taller Autorizado"
    email_instalador = ""
    if garantia.rollo_padre and garantia.rollo_padre.propietario:
        nombre_instalador = garantia.rollo_padre.propietario.username
        email_instalador = garantia.rollo_padre.propietario.email

    return render_template('public/certificado.html', 
                           g=garantia, 
                           producto=nombre_producto, 
                           instalador=nombre_instalador,
                           email_inst=email_instalador)


@public_bp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        dato = request.form.get('busqueda', '').strip().upper()
        
        garantia = Subcodigo.query.filter_by(codigo_hijo=dato, estado='ACTIVADO').first()
        if not garantia:
            garantia = Subcodigo.query.filter_by(cliente_patente=dato, estado='ACTIVADO').order_by(Subcodigo.fecha_activacion.desc()).first()
            
        if garantia:
            return redirect(url_for('public.ver_certificado', codigo=garantia.codigo_hijo))
        else:
            flash('No encontramos una garantía activa.', 'warning')

    return render_template('public/index.html')