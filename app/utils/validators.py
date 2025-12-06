"""
Validators - Funciones de validación
"""
import re
from datetime import datetime


def validate_email(email):
    """
    Validar formato de email
    
    Returns:
        bool: True si es válido
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone):
    """
    Validar formato de teléfono
    
    Returns:
        bool: True si es válido
    """
    # Acepta formatos: (123) 456-7890, 123-456-7890, 1234567890
    pattern = r'^[\d\s\-\(\)]+$'
    return re.match(pattern, phone) is not None and len(phone) >= 10


def validate_code_format(code, prefix='AT'):
    """
    Validar formato de código de stock o garantía
    
    Args:
        code: Código a validar
        prefix: Prefijo esperado
    
    Returns:
        bool: True si es válido
    """
    if not code:
        return False
    
    return code.startswith(f'{prefix}-')


def validate_warranty_years(years):
    """
    Validar años de garantía
    
    Returns:
        bool: True si es válido (1-10 años)
    """
    try:
        years = int(years)
        return 1 <= years <= 10
    except (ValueError, TypeError):
        return False


def sanitize_filename(filename):
    """
    Sanitizar nombre de archivo para evitar problemas de seguridad
    
    Returns:
        str: Nombre de archivo sanitizado
    """
    # Eliminar caracteres peligrosos
    filename = re.sub(r'[^\w\s\-\.]', '', filename)
    # Reemplazar espacios con guiones bajos
    filename = filename.replace(' ', '_')
    return filename


def validate_date_range(start_date, end_date):
    """
    Validar que el rango de fechas sea válido
    
    Returns:
        bool: True si es válido
    """
    if not start_date or not end_date:
        return False
    
    try:
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date)
        if isinstance(end_date, str):
            end_date = datetime.fromisoformat(end_date)
        
        return start_date <= end_date
    except (ValueError, TypeError):
        return False


def allowed_file(filename, allowed_extensions=None):
    """
    Verificar si la extensión del archivo está permitida
    
    Args:
        filename: Nombre del archivo
        allowed_extensions: Set de extensiones permitidas
    
    Returns:
        bool: True si está permitida
    """
    if allowed_extensions is None:
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}
    
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions
