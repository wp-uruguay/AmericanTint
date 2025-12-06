"""
Helpers - Funciones auxiliares generales
"""
from datetime import datetime, timedelta
import os
from werkzeug.utils import secure_filename
from flask import current_app


def format_date(date, format='%d/%m/%Y'):
    """
    Formatear fecha para mostrar
    
    Args:
        date: Objeto datetime
        format: Formato de salida
    
    Returns:
        str: Fecha formateada
    """
    if not date:
        return ''
    
    if isinstance(date, str):
        try:
            date = datetime.fromisoformat(date)
        except ValueError:
            return date
    
    return date.strftime(format)


def format_datetime(dt, format='%d/%m/%Y %H:%M'):
    """
    Formatear fecha y hora
    
    Returns:
        str: Fecha y hora formateada
    """
    return format_date(dt, format)


def calculate_percentage(value, total):
    """
    Calcular porcentaje
    
    Returns:
        float: Porcentaje (0-100)
    """
    if total == 0:
        return 0
    return round((value / total) * 100, 2)


def time_ago(dt):
    """
    Convertir fecha a formato "hace X tiempo"
    
    Returns:
        str: Tiempo relativo
    """
    if not dt:
        return ''
    
    now = datetime.utcnow()
    diff = now - dt
    
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return 'hace un momento'
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f'hace {minutes} minuto{"s" if minutes > 1 else ""}'
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f'hace {hours} hora{"s" if hours > 1 else ""}'
    elif seconds < 2592000:
        days = int(seconds / 86400)
        return f'hace {days} día{"s" if days > 1 else ""}'
    elif seconds < 31536000:
        months = int(seconds / 2592000)
        return f'hace {months} mes{"es" if months > 1 else ""}'
    else:
        years = int(seconds / 31536000)
        return f'hace {years} año{"s" if years > 1 else ""}'


def save_uploaded_file(file, folder='uploads'):
    """
    Guardar archivo subido de forma segura
    
    Args:
        file: Archivo de FileStorage
        folder: Subcarpeta dentro de uploads
    
    Returns:
        str: Path relativo del archivo guardado
    """
    if not file:
        return None
    
    filename = secure_filename(file.filename)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_filename = f"{timestamp}_{filename}"
    
    upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], folder)
    os.makedirs(upload_folder, exist_ok=True)
    
    filepath = os.path.join(upload_folder, unique_filename)
    file.save(filepath)
    
    return os.path.join(folder, unique_filename)


def format_currency(amount, currency='$'):
    """
    Formatear cantidad monetaria
    
    Returns:
        str: Cantidad formateada
    """
    if amount is None:
        return f'{currency}0.00'
    
    return f'{currency}{amount:,.2f}'


def paginate_query(query, page=1, per_page=20):
    """
    Paginar query de SQLAlchemy
    
    Args:
        query: Query de SQLAlchemy
        page: Número de página
        per_page: Items por página
    
    Returns:
        dict: Datos de paginación
    """
    pagination = query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    return {
        'items': pagination.items,
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages,
        'has_prev': pagination.has_prev,
        'has_next': pagination.has_next,
        'prev_num': pagination.prev_num,
        'next_num': pagination.next_num
    }


def generate_random_string(length=8, uppercase=True, digits=True):
    """
    Generar string aleatorio
    
    Returns:
        str: String aleatorio
    """
    import random
    import string
    
    chars = string.ascii_lowercase
    if uppercase:
        chars += string.ascii_uppercase
    if digits:
        chars += string.digits
    
    return ''.join(random.choices(chars, k=length))
