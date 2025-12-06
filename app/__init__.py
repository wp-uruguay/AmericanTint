from flask import Flask
from app.config import Config
from app.extensions import db, login_manager, migrate

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Inicializar extensiones
    db.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message = "Debes iniciar sesión para ver esta página."
    login_manager.login_message_category = "warning"
    
    # 1. Pasamos 'db' a migrate para que sepa dónde buscar
    migrate.init_app(app, db)

    # 2. IMPORTANTE: Importamos los modelos aquí para que Alembic los detecte
    # Sin esta línea, dice "No changes detected"
    from app import models 

    # --- REGISTRO DE BLUEPRINTS (ESTRATEGIA: CARPETAS) ---
    
    # 1. Admin -> http://127.0.0.1:5000/admin
    from app.views.admin import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # 2. Instalador -> http://127.0.0.1:5000/instalador
    from app.views.installer import installer_bp
    app.register_blueprint(installer_bp, url_prefix='/instalador')

    # 3. Garantía -> http://127.0.0.1:5000/garantia
    from app.views.public import public_bp
    app.register_blueprint(public_bp, url_prefix='/garantia')

    # 4. Home Principal -> http://127.0.0.1:5000/
    from app.views.main import main_bp
    app.register_blueprint(main_bp)

    # 5. Autenticación (Login/Logout)
    from app.views.auth import auth_bp
    app.register_blueprint(auth_bp) # Sin prefijo, para que sea /login
    
    return app