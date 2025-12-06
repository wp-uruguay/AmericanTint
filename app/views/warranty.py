"""
Blueprint de Garantías
Rutas: listar, activar, buscar, detalles
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required

warranty_bp = Blueprint('warranty', __name__)


@warranty_bp.route('/')
@login_required
def index():
    """Listar todas las garantías"""
    # TODO: Obtener garantías con filtros
    return render_template('warranty/index.html')


@warranty_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Crear/Activar nueva garantía"""
    if request.method == 'POST':
        # TODO: Llamar a warranty_service para activar
        pass
    
    return render_template('warranty/create.html')


@warranty_bp.route('/<int:id>')
@login_required
def detail(id):
    """Ver detalles de una garantía"""
    # TODO: Obtener garantía por ID
    return render_template('warranty/detail.html')


@warranty_bp.route('/search')
@login_required
def search():
    """Buscar garantía por código"""
    code = request.args.get('code', '')
    # TODO: Buscar en warranty_service
    return render_template('warranty/search.html')


@warranty_bp.route('/activate', methods=['POST'])
@login_required
def activate():
    """Endpoint para activar garantía (puede ser AJAX)"""
    # TODO: Procesar activación
    return jsonify({'success': True, 'message': 'Garantía activada'})
