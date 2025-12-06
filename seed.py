from app import create_app
from app.extensions import db
from app.models import User, Producto, Rollo, AuditLog, Subcodigo
from werkzeug.security import generate_password_hash

def seed_database():
    app = create_app()
    with app.app_context():
        print("🌱 Iniciando carga de datos...")

        # ---------------------------------------------------------
        # 1. USUARIOS (Super Admin + Admin Argentina)
        # ---------------------------------------------------------
        
        # A. SUPER ADMIN (Acceso a todo LATAM)
        if not User.query.filter_by(email='ceo@americantint.com').first():
            super_admin = User(
                email='ceo@americantint.com',
                password_hash=generate_password_hash('ceo123'),
                username='CEO Global', 
                role='superadmin',
                pais=None # None significa "Todos los países"
            )
            db.session.add(super_admin)
            print("🌎 Usuario SUPER ADMIN creado (ceo@americantint.com).")

        # B. ADMIN ARGENTINA (Solo AR)
        if not User.query.filter_by(email='admin.ar@americantint.com').first():
            admin_ar = User(
                email='admin.ar@americantint.com',
                password_hash=generate_password_hash('admin123'),
                username='Admin Argentina', 
                role='admin',
                pais='AR'
            )
            db.session.add(admin_ar)
            print("🇦🇷 Usuario Admin AR creado.")

        # ---------------------------------------------------------
        # 2. CATÁLOGO DE PRODUCTOS
        # ---------------------------------------------------------
        productos_data = [
            {'nombre': 'AT Premium 05', 'linea': 'Premium', 'variedad': '05', 'garantia': 6},
            {'nombre': 'AT Premium 15', 'linea': 'Premium', 'variedad': '15', 'garantia': 6},
            {'nombre': 'AT Premium 35', 'linea': 'Premium', 'variedad': '35', 'garantia': 6}, 
            {'nombre': 'AT Nanocarbon 05', 'linea': 'Nanocarbon', 'variedad': '05', 'garantia': 10},
            {'nombre': 'AT Nanocarbon 15', 'linea': 'Nanocarbon', 'variedad': '15', 'garantia': 10},
            {'nombre': 'AT Nanoceramic 05', 'linea': 'Nanoceramic', 'variedad': '05', 'garantia': 10},
            {'nombre': 'AT Nanoceramic 15', 'linea': 'Nanoceramic', 'variedad': '15', 'garantia': 10},
        ]

        for p_data in productos_data:
            if not Producto.query.filter_by(nombre=p_data['nombre']).first():
                prod = Producto(
                    nombre=p_data['nombre'],
                    linea=p_data['linea'],
                    variedad=p_data['variedad'],
                    garantia_anios=p_data['garantia']
                )
                db.session.add(prod)
        
        db.session.commit()
        print("✅ ¡Base de datos actualizada con Super Admin!")

if __name__ == '__main__':
    seed_database()