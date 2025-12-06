from flask import Flask
from app.config import Config
from app.extensions import db, login_manager, migrate
from app.services.email_service import mail 

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Inicializar extensiones
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    # CONFIGURACIÓN DE LOGIN (ESTO FALTABA)
    # Le decimos a Flask: "Si alguien no tiene permiso, mándalo a 'auth.login'"
    login_manager.login_view = 'auth.login'
    login_manager.login_message = "Por favor inicia sesión para acceder."
    login_manager.login_message_category = "warning"

    # Importar modelos para migraciones
    from app import models 

    # --- REGISTRO DE BLUEPRINTS ---
    
    # 1. Admin
    from app.views.admin import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # 2. Instalador
    from app.views.installer import installer_bp
    app.register_blueprint(installer_bp, url_prefix='/instalador')

    # 3. Garantía (Público)
    from app.views.public import public_bp
    app.register_blueprint(public_bp, url_prefix='/garantia')

    # 4. Home Principal
    from app.views.main import main_bp
    app.register_blueprint(main_bp)

    # 5. AUTENTICACIÓN (LOGIN/LOGOUT) - ¡ESTO FALTABA!
    from app.views.auth import auth_bp
    app.register_blueprint(auth_bp)

    return app