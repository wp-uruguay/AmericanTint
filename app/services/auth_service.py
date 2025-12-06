"""
Auth Service - Lógica de autenticación
"""
from app.extensions import db
from app.models.user import User
from flask_login import login_user
from datetime import datetime


class AuthService:
    
    @staticmethod
    def authenticate_user(username, password, remember=False):
        """
        Autenticar usuario
        
        Returns:
            tuple: (success: bool, message: str, user: User)
        """
        user = User.query.filter_by(username=username).first()
        
        if not user:
            return False, 'Usuario no encontrado', None
        
        if not user.is_active:
            return False, 'Usuario desactivado', None
        
        if not user.check_password(password):
            return False, 'Contraseña incorrecta', None
        
        # Actualizar último login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Login con Flask-Login
        login_user(user, remember=remember)
        
        return True, 'Login exitoso', user
    
    @staticmethod
    def create_user(username, email, password, first_name='', last_name='', role='user'):
        """
        Crear nuevo usuario
        
        Returns:
            tuple: (success: bool, message: str, user: User)
        """
        # Validar si ya existe
        if User.query.filter_by(username=username).first():
            return False, 'El nombre de usuario ya existe', None
        
        if User.query.filter_by(email=email).first():
            return False, 'El email ya está registrado', None
        
        # Crear usuario
        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            role=role
        )
        user.set_password(password)
        
        try:
            db.session.add(user)
            db.session.commit()
            return True, 'Usuario creado exitosamente', user
        except Exception as e:
            db.session.rollback()
            return False, f'Error al crear usuario: {str(e)}', None
    
    @staticmethod
    def change_password(user, old_password, new_password):
        """
        Cambiar contraseña de usuario
        
        Returns:
            tuple: (success: bool, message: str)
        """
        if not user.check_password(old_password):
            return False, 'Contraseña actual incorrecta'
        
        user.set_password(new_password)
        
        try:
            db.session.commit()
            return True, 'Contraseña actualizada exitosamente'
        except Exception as e:
            db.session.rollback()
            return False, f'Error al actualizar contraseña: {str(e)}'
