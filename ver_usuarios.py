from app import create_app
from app.extensions import db
from app.models import User

app = create_app()

with app.app_context():
    print("\n" + "="*50)
    print("🕵️‍♂️  LISTA DE USUARIOS EN LA BASE DE DATOS")
    print("="*50)
    
    users = User.query.all()
    
    if not users:
        print("❌ No hay usuarios registrados (¿Ejecutaste python seed.py?)")
    else:
        print(f"{'ID':<5} | {'ROL':<12} | {'PAÍS':<5} | {'USUARIO':<20} | {'EMAIL'}")
        print("-" * 80)
        for u in users:
            pais = u.pais if u.pais else 'GLOBAL'
            print(f"{u.id:<5} | {u.role:<12} | {pais:<5} | {u.username:<20} | {u.email}")
    
    print("="*50 + "\n")