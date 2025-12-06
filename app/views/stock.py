"""
Blueprint de Stock
Rutas: listar, crear, editar, detalles de rollos
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required

stock_bp = Blueprint('stock', __name__)


@stock_bp.route('/')
@login_required
def index():
    """Listar todos los rollos de stock"""
    # TODO: Obtener stock desde stock_service
    return render_template('stock/index.html')


@stock_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """Agregar nuevo rollo al stock"""
    if request.method == 'POST':
        # TODO: Llamar a stock_service.importar_stock()
        pass
    
    return render_template('stock/add.html')


@stock_bp.route('/<int:id>')
@login_required
def detail(id):
    """Ver detalles de un rollo específico"""
    # TODO: Obtener rollo y sus subcódigos
    return render_template('stock/detail.html')


@stock_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Editar información de un rollo"""
    if request.method == 'POST':
        # TODO: Actualizar rollo
        pass
    
    return render_template('stock/edit.html')
