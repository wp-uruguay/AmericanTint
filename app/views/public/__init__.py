from flask import Blueprint, render_template_string, request, flash, redirect, url_for
from app.extensions import db
from app.models import Subcodigo, AuditLog
from datetime import datetime

public_bp = Blueprint('public', __name__)

# --- VISTA 1: ACTIVACIÓN DE GARANTÍA ---
@public_bp.route('/activar/<codigo>', methods=['GET', 'POST'])
def activar_garantia(codigo):
    garantia_previa = Subcodigo.query.filter_by(codigo_hijo=codigo).first()
    
    # Precargar datos
    patente_sugerida = garantia_previa.cliente_patente if garantia_previa else ''
    nombre_taller = "el Taller Autorizado"
    if garantia_previa and garantia_previa.rollo_padre.propietario:
        nombre_taller = garantia_previa.rollo_padre.propietario.username

    if request.method == 'POST':
        codigo_final = request.form.get('codigo_manual', '').strip()
        garantia = Subcodigo.query.filter_by(codigo_hijo=codigo_final).first()

        # Validaciones básicas
        if not garantia:
            flash('❌ Error: Código inválido.', 'danger')
            return render_template_string(html_activacion, codigo=codigo_final, patente_ref='', taller='')

        if garantia.estado == 'ACTIVADO':
            flash('ℹ️ Esta garantía ya fue activada.', 'info')
            return redirect(url_for('public.ver_certificado', codigo=garantia.codigo_hijo))

        try:
            # Guardar Datos Personales
            garantia.cliente_nombre = request.form['nombre']
            garantia.cliente_telefono = request.form['telefono']
            garantia.cliente_patente = request.form['patente'].upper().strip()
            
            # Guardar Reseña (NUEVO)
            garantia.instalador_correcto = (request.form.get('instalador_ok') == 'si')
            garantia.review_texto = request.form.get('review_texto')
            garantia.review_stars = int(request.form.get('rating', 0))

            # Activar
            garantia.fecha_activacion = datetime.utcnow()
            garantia.estado = 'ACTIVADO'
            
            db.session.commit()
            
            flash('✅ ¡Garantía activada y reseña guardada!', 'success')
            return redirect(url_for('public.ver_certificado', codigo=garantia.codigo_hijo))
            
        except Exception as e:
            db.session.rollback()
            flash(f"Error técnico: {str(e)}", 'danger')

    return render_template_string(html_activacion, 
                                  codigo=codigo, 
                                  patente_ref=patente_sugerida,
                                  taller=nombre_taller)


# --- VISTA 2: VER CERTIFICADO ---
@public_bp.route('/certificado/<codigo>')
def ver_certificado(codigo):
    garantia = Subcodigo.query.filter_by(codigo_hijo=codigo, estado='ACTIVADO').first_or_404()
    
    nombre_producto = "Producto American Tint"
    if garantia.rollo_padre and garantia.rollo_padre.producto_info:
        nombre_producto = garantia.rollo_padre.producto_info.nombre

    nombre_instalador = "Taller Autorizado"
    if garantia.rollo_padre and garantia.rollo_padre.propietario:
        nombre_instalador = garantia.rollo_padre.propietario.username

    return render_template_string(html_certificado, 
                                  g=garantia, 
                                  producto=nombre_producto, 
                                  instalador=nombre_instalador)

# --- VISTA 3: HOME ---
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

    return render_template_string(html_home)


# ==============================================================================
# HTML TEMPLATES (Con Estrellas CSS)
# ==============================================================================

html_activacion = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Activar Garantía</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        /* Estilos para las Estrellas */
        .rate { float: left; height: 46px; padding: 0 10px; }
        .rate:not(:checked) > input { position:absolute; top:-9999px; }
        .rate:not(:checked) > label { float:right; width:1em; overflow:hidden; white-space:nowrap; cursor:pointer; font-size:30px; color:#ccc; }
        .rate:not(:checked) > label:before { content: '★ '; }
        .rate > input:checked ~ label { color: #ffc700; }
        .rate:not(:checked) > label:hover, .rate:not(:checked) > label:hover ~ label { color: #deb217; }
        .rate > input:checked + label:hover, .rate > input:checked + label:hover ~ label,
        .rate > input:checked ~ label:hover, .rate > input:checked ~ label:hover ~ label,
        .rate > label:hover ~ input:checked ~ label { color: #c59b08; }
    </style>
</head>
<body class="bg-light py-5">
    <div class="container" style="max_width: 600px;">
        
        {% with messages = get_flashed_messages(with_categories=true) %}
          {% if messages %}
            {% for category, message in messages %}
              <div class="alert alert-{{ category }}">{{ message }}</div>
            {% endfor %}
          {% endif %}
        {% endwith %}

        <div class="card shadow border-0">
            <div class="card-header bg-primary text-white text-center py-3">
                <h4 class="mb-0">🛡️ Activar Garantía Oficial</h4>
            </div>
            <div class="card-body p-4">
                <form method="POST">
                    
                    <h5 class="text-muted mb-3">1. Datos del Vehículo</h5>
                    <div class="mb-3">
                        <label class="form-label small fw-bold">CÓDIGO DE GARANTÍA</label>
                        <input type="text" name="codigo_manual" class="form-control fw-bold text-primary" value="{{ codigo }}" required>
                    </div>
                    <div class="mb-3">
                        <label>Patente</label>
                        <input type="text" name="patente" class="form-control text-uppercase" value="{{ patente_ref }}" required>
                    </div>

                    <h5 class="text-muted mt-4 mb-3">2. Tus Datos</h5>
                    <div class="row">
                        <div class="col-6">
                            <label>Nombre</label>
                            <input type="text" name="nombre" class="form-control" required>
                        </div>
                        <div class="col-6">
                            <label>Teléfono</label>
                            <input type="text" name="telefono" class="form-control" required>
                        </div>
                    </div>

                    <hr class="my-4">
                    
                    <h5 class="text-muted mb-3">3. Tu Experiencia</h5>
                    
                    <div class="mb-3 p-3 bg-light rounded border">
                        <label class="form-label d-block mb-2">¿La instalación fue realizada por <strong>{{ taller }}</strong>?</label>
                        <div class="form-check form-check-inline">
                            <input class="form-check-input" type="radio" name="instalador_ok" value="si" id="inst_si" checked>
                            <label class="form-check-label" for="inst_si">Sí, es correcto</label>
                        </div>
                        <div class="form-check form-check-inline">
                            <input class="form-check-input" type="radio" name="instalador_ok" value="no" id="inst_no">
                            <label class="form-check-label" for="inst_no">No, fue otro</label>
                        </div>
                    </div>

                    <div class="mb-3">
                        <label class="form-label d-block">Califica el servicio:</label>
                        <div class="rate">
                            <input type="radio" id="star5" name="rating" value="5" />
                            <label for="star5" title="Excelente">5 stars</label>
                            <input type="radio" id="star4" name="rating" value="4" />
                            <label for="star4" title="Muy bueno">4 stars</label>
                            <input type="radio" id="star3" name="rating" value="3" />
                            <label for="star3" title="Normal">3 stars</label>
                            <input type="radio" id="star2" name="rating" value="2" />
                            <label for="star2" title="Malo">2 stars</label>
                            <input type="radio" id="star1" name="rating" value="1" />
                            <label for="star1" title="Muy malo">1 star</label>
                        </div>
                        <div style="clear:both;"></div>
                    </div>

                    <div class="mb-4">
                        <label class="form-label">Cuéntanos brevemente tu experiencia (Opcional)</label>
                        <textarea name="review_texto" class="form-control" rows="2" placeholder="Ej: Quedó excelente, muy rápido..."></textarea>
                    </div>

                    <button type="submit" class="btn btn-success w-100 btn-lg shadow">✅ CONFIRMAR Y ACTIVAR</button>
                </form>
            </div>
        </div>
    </div>
</body>
</html>
"""

html_certificado = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Certificado Oficial</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-dark py-5">
    <div class="container">
        <div class="card shadow-lg mx-auto p-5" style="max_width: 800px; border: 5px solid #D4AF37;">
            <div class="text-center">
                <h1 class="text-uppercase display-6 fw-bold">Certificado de Garantía</h1>
                <h3 style="color: #D4AF37;">American Tint Premium Films</h3>
                <hr>
                
                <div class="row text-start mt-5">
                    <div class="col-md-6">
                        <p class="text-muted mb-0">CLIENTE</p>
                        <h4>{{ g.cliente_nombre }}</h4>
                    </div>
                    <div class="col-md-6 text-end">
                        <p class="text-muted mb-0">CÓDIGO ÚNICO</p>
                        <h4 class="text-primary">{{ g.codigo_hijo }}</h4>
                    </div>
                </div>

                <div class="alert alert-light border mt-4">
                    <div class="row">
                        <div class="col-6 text-start">
                            <strong>Producto:</strong> {{ producto }}<br>
                            <strong>Vehículo:</strong> {{ g.cliente_patente }}
                        </div>
                        <div class="col-6 text-end">
                            <strong>Instalador:</strong> {{ instalador }}<br>
                            <strong>Fecha:</strong> {{ g.fecha_activacion.strftime('%d/%m/%Y') }}
                        </div>
                    </div>
                </div>

                <div class="mt-4">
                    <span class="badge bg-success fs-5">GARANTÍA VIGENTE</span>
                </div>
            </div>
            <div class="text-center mt-5 no-print">
                <button onclick="window.print()" class="btn btn-outline-dark">🖨️ Imprimir</button>
            </div>
        </div>
    </div>
</body>
</html>
"""

html_home = """<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"><title>Soporte</title></head><body><h1>Buscador...</h1></body></html>"""
# (Puedes usar el HTML home completo del paso anterior aquí, lo resumí por espacio)