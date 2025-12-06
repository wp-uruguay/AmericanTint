"""
Blueprint de Productos
Rutas: listar, crear, editar productos
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required

product_bp = Blueprint('product', __name__)


@product_bp.route('/')
@login_required
def index():
    """Listar todos los productos"""
    # TODO: Obtener productos del catálogo
    return render_template('product/index.html')


@product_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """Agregar nuevo producto"""
    if request.method == 'POST':
        # TODO: Crear nuevo producto
        pass
    
    return render_template('product/add.html')


@product_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Editar producto existente"""
    if request.method == 'POST':
        # TODO: Actualizar producto
        pass
    
    return render_template('product/edit.html')
