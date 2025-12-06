from flask import Flask
from app.config import Config
from app.extensions import db, login_manager, migrate

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Inicializar extensiones
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app)

    # --- REGISTRO DE BLUEPRINTS ---
    
    # 1. Admin (Solo responde a admin.americantint.local)
    from app.views.admin import admin_bp
    app.register_blueprint(admin_bp, subdomain='admin')

    # 2. Instalador (Solo responde a instaladores.americantint.local)
    from app.views.installer import installer_bp
    app.register_blueprint(installer_bp, subdomain='instaladores')

    # 3. Garantía (Solo responde a garantia.americantint.local)
    from app.views.public import public_bp
    app.register_blueprint(public_bp, subdomain='garantia')

    # 4. Home Principal (Responde al dominio raíz americantint.local)
    # IMPORTANTE: No le ponemos subdomain.
    from app.views.main import main_bp
    app.register_blueprint(main_bp)

    return app