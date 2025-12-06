from app import create_app
from app.extensions import db
from app.models import User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    print("--- 🕵️‍♂️ DIAGNÓSTICO DE USUARIOS ---")
    users = User.query.all()
    for u in users:
        print(f"ID: {u.id} | User: {u.username} | Email: {u.email} | Rol: {u.role}")
    
    print("\n--- 🛠️ RESTABLECIENDO CONTRASEÑA ---")
    email_taller = 'taller@test.com' # El email que usaste
    taller = User.query.filter_by(email=email_taller).first()
    
    if taller:
        taller.password_hash = generate_password_hash('1234')
        db.session.commit()
        print(f"✅ Contraseña de {taller.username} cambiada a: 1234")
    else:
        print(f"❌ Error: No encontré al usuario {email_taller}")