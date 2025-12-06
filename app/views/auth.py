from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from app.models.user import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Si ya está logueado, lo mandamos a su panel correspondiente
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect('/admin')
        elif current_user.role == 'instalador':
            return redirect('/instalador')
        else:
            return redirect('/')

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        # Verificamos si el usuario existe y la contraseña es correcta
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            
            # Redirección inteligente según el rol
            if user.role == 'admin':
                return redirect('/admin')
            elif user.role == 'instalador':   # <--- ¿TIENES ESTO?
                return redirect('/instalador')
            elif user.role == 'superadmin':   # <--- Y ESTO
                return redirect('/admin')
            else:
                return redirect('/garantia')
        else:
            flash('Email o contraseña incorrectos', 'danger')

    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión correctamente.', 'info')
    return redirect(url_for('auth.login'))