from flask import Blueprint, render_template_string, request, flash, redirect, url_for
from app.extensions import db
from app.models import Subcodigo, AuditLog # Asegúrate de tener TicketSoporte en models
from datetime import datetime

public_bp = Blueprint('public', __name__)

@public_bp.route('/', methods=['GET', 'POST'])
def index():
    garantia_encontrada = None
    
    # LÓGICA DE BÚSQUEDA
    if request.method == 'POST' and 'buscar_patente' in request.form:
        patente = request.form.get('patente').upper().strip()
        # Buscamos la garantía activa más reciente para esa patente
        garantia_encontrada = Subcodigo.query.filter_by(cliente_patente=patente, estado='ACTIVADO').first()
        
        if not garantia_encontrada:
            flash('No encontramos una garantía activa para esa patente.', 'warning')
        else:
            flash('✅ ¡Garantía encontrada!', 'success')

    # LÓGICA DE RECLAMO (SOPORTE)
    if request.method == 'POST' and 'crear_reclamo' in request.form:
        patente = request.form.get('patente_reclamo')
        email = request.form.get('email')
        mensaje = request.form.get('mensaje')
        
        # Guardar ticket (Necesitas asegurarte de tener este modelo o usar AuditLog por ahora)
        # Para simplificar este MVP, guardaremos un AuditLog marcado como RECLAMO
        # (O idealmente descomentar el modelo TicketSoporte si lo creaste en models.py)
        
        # Simulación de guardado de ticket
        try:
            # Aquí podrías guardar en una tabla 'tickets' real
            log = AuditLog(
                user_id=None, # Es anónimo/público
                accion='NUEVO_RECLAMO',
                detalle=f"Reclamo de {patente} ({email}): {mensaje}"
            )
            db.session.add(log)
            db.session.commit()
            flash('Tu reclamo ha sido enviado. Nos contactaremos pronto.', 'info')
        except Exception as e:
            flash('Error al enviar reclamo.', 'danger')
            
        return redirect(url_for('public.index'))

    html = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Garantía American Tint</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
            body { background-color: #f8f9fa; }
            .hero-section { background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); color: white; padding: 60px 0; border-radius: 0 0 20px 20px; }
            .certificate-card { border: 2px solid #daa520; background: #fff; position: relative; overflow: hidden; }
            .watermark { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%) rotate(-30deg); font-size: 5rem; color: rgba(0,0,0,0.05); font-weight: bold; pointer-events: none; }
        </style>
    </head>
    <body>

    <div class="hero-section text-center mb-5">
        <div class="container">
            <h1 class="fw-bold"><i class="fa fa-shield-alt"></i> American Tint</h1>
            <p class="lead">Consulta de Garantía Oficial & Soporte</p>
        </div>
    </div>

    <div class="container" style="max_width: 800px;">
        
        {% with messages = get_flashed_messages(with_categories=true) %}
          {% if messages %}
            {% for category, message in messages %}
              <div class="alert alert-{{ category }} alert-dismissible fade show text-center">
                {{ message }} <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
              </div>
            {% endfor %}
          {% endif %}
        {% endwith %}

        <div class="card shadow-sm mb-5">
            <div class="card-body p-4 text-center">
                <h3 class="mb-3">🔍 Consultar mi Garantía</h3>
                <form method="POST" class="d-flex justify-content-center gap-2">
                    <input type="text" name="patente" class="form-control form-control-lg w-50" placeholder="Ingresa tu Patente (Ej: AA123BB)" required style="text-transform: uppercase;">
                    <button type="submit" name="buscar_patente" value="1" class="btn btn-primary btn-lg">Buscar</button>
                </form>
            </div>
        </div>

        {% if garantia %}
        <div class="card certificate-card shadow-lg mb-5 animate__animated animate__fadeInUp">
            <div class="watermark">ORIGINAL</div>
            <div class="card-body p-5">
                <div class="text-center mb-4">
                    <h2 class="text-uppercase" style="color: #1e3c72; letter-spacing: 2px;">Certificado de Garantía</h2>
                    <p class="text-muted">American Tint Premium Films</p>
                    <hr class="w-25 mx-auto" style="border-color: #daa520; border-width: 3px;">
                </div>

                <div class="row">
                    <div class="col-md-6 mb-3">
                        <h6 class="text-muted text-uppercase small">Vehículo</h6>
                        <h4>{{ garantia.cliente_patente }}</h4>
                    </div>
                    <div class="col-md-6 mb-3 text-md-end">
                        <h6 class="text-muted text-uppercase small">Código Único</h6>
                        <h4 class="text-primary">{{ garantia.codigo_hijo }}</h4>
                    </div>
                </div>

                <div class="row mt-3 p-3 bg-light rounded">
                    <div class="col-md-6">
                        <p class="mb-1"><strong>Producto Instalado:</strong></p>
                        <span class="fs-5">{{ garantia.rollo_padre.producto_info.nombre }}</span>
                    </div>
                    <div class="col-md-6 text-md-end">
                        <p class="mb-1"><strong>Fecha Instalación:</strong></p>
                        <span class="fs-5">{{ garantia.fecha_activacion.strftime('%d/%m/%Y') }}</span>
                    </div>
                </div>

                <div class="mt-4 text-center">
                    <p class="mb-1 text-muted">Instalado Por:</p>
                    <h5>{{ garantia.rollo_padre.propietario.username }}</h5>
                    <p class="small text-muted">{{ garantia.rollo_padre.propietario.email }}</p>
                </div>

                <div class="mt-4 alert alert-success text-center border-0">
                    <i class="fa fa-check-circle"></i> Garantía Vigente hasta <strong>2030</strong> 
                    </div>
            </div>
        </div>
        {% endif %}

        <div class="accordion mb-5" id="accordionSoporte">
            <div class="accordion-item border-0 shadow-sm">
                <h2 class="accordion-header">
                    <button class="accordion-button collapsed bg-light" type="button" data-bs-toggle="collapse" data-bs-target="#collapseOne">
                        🛠️ ¿Tienes un problema? Abrir un Reclamo
                    </button>
                </h2>
                <div id="collapseOne" class="accordion-collapse collapse" data-bs-parent="#accordionSoporte">
                    <div class="accordion-body">
                        <form method="POST">
                            <input type="hidden" name="crear_reclamo" value="1">
                            <div class="mb-3">
                                <label>Patente Afectada</label>
                                <input type="text" name="patente_reclamo" class="form-control" required>
                            </div>
                            <div class="mb-3">
                                <label>Tu Email de Contacto</label>
                                <input type="email" name="email" class="form-control" required>
                            </div>
                            <div class="mb-3">
                                <label>Descripción del Problema</label>
                                <textarea name="mensaje" class="form-control" rows="3" required placeholder="Ej: Burbujas en ventana trasera..."></textarea>
                            </div>
                            <button type="submit" class="btn btn-danger w-100">Enviar Reclamo</button>
                        </form>
                    </div>
                </div>
            </div>
        </div>

    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """
    return render_template_string(html, garantia=garantia_encontrada)