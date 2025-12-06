"""
Extensions - Inicialización de extensiones Flask
Evita importaciones circulares al centralizar las extensiones
"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

# Inicializar extensiones sin vincular a la app
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

# Configuración del Login Manager
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
login_manager.login_message_category = 'info'
