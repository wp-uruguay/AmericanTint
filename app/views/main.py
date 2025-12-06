from flask import Blueprint

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    # FÍJATE EN LOS HREF: Ahora apuntan a la carpeta, no al subdominio
    return """
    <div style="text-align:center; font-family: sans-serif; padding:50px;">
        <h1>🏢 Centro de Control American Tint</h1>
        <p>Sistema ERP v1.0 (Modo Carpetas Local)</p>
        <hr>
        <div style="display: flex; justify-content: center; gap: 20px;">
            <a href="/admin" style="padding: 20px; background: #d9534f; color: white; text-decoration: none; border-radius: 8px;">
                🔴 Ir a ADMIN
            </a>
            
            <a href="/instalador" style="padding: 20px; background: #0275d8; color: white; text-decoration: none; border-radius: 8px;">
                🔵 Ir a INSTALADORES
            </a>
            
            <a href="/garantia" style="padding: 20px; background: #5cb85c; color: white; text-decoration: none; border-radius: 8px;">
                🟢 Ir a CLIENTES
            </a>
        </div>
    </div>
    """