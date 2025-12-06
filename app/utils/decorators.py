"""
Decorators - Decoradores personalizados
"""
from functools import wraps
from flask import redirect, url_for, flash, abort
from flask_login import current_user


def admin_required(f):
    """
    Decorador para rutas que requieren rol de administrador
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Debes iniciar sesión para acceder a esta página.', 'warning')
            return redirect(url_for('auth.login'))
        
        if not current_user.is_admin():
            flash('No tienes permisos para acceder a esta página.', 'danger')
            abort(403)
        
        return f(*args, **kwargs)
    return decorated_function


def manager_required(f):
    """
    Decorador para rutas que requieren rol de manager o superior
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Debes iniciar sesión para acceder a esta página.', 'warning')
            return redirect(url_for('auth.login'))
        
        if current_user.role not in ['admin', 'manager']:
            flash('No tienes permisos para acceder a esta página.', 'danger')
            abort(403)
        
        return f(*args, **kwargs)
    return decorated_function


def check_confirmed(f):
    """
    Decorador para verificar si el usuario ha confirmado su email
    (Útil si se implementa confirmación por email)
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        
        # TODO: Implementar lógica de confirmación si se requiere
        # if not current_user.confirmed:
        #     flash('Por favor confirma tu cuenta de email.', 'warning')
        #     return redirect(url_for('auth.unconfirmed'))
        
        return f(*args, **kwargs)
    return decorated_function
