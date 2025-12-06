"""
Tests para services
"""
import pytest
from app import create_app
from app.extensions import db
from app.services.stock_service import StockService
from app.services.warranty_service import WarrantyService
from app.services.auth_service import AuthService
from app.models.product import Product


@pytest.fixture
def app():
    """Crear aplicación de prueba"""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


def test_import_stock(app):
    """Test de importación de stock"""
    with app.app_context():
        # Crear producto de prueba
        product = Product(code='PREMIUM01', name='Premium Line', category='Premium')
        db.session.add(product)
        db.session.commit()
        
        # Importar stock
        success, message, stocks = StockService.importar_stock(
            product_id=product.id,
            quantity=2,
            roll_number='R001',
            batch_number='B001'
        )
        
        assert success is True
        assert len(stocks) == 2
        assert '2 rollo(s) importado(s)' in message
        assert '30 códigos de garantía' in message


def test_create_user(app):
    """Test de creación de usuario"""
    with app.app_context():
        success, message, user = AuthService.create_user(
            username='testuser',
            email='test@example.com',
            password='password123',
            first_name='Test',
            last_name='User'
        )
        
        assert success is True
        assert user is not None
        assert user.username == 'testuser'
        assert user.check_password('password123')


def test_duplicate_user(app):
    """Test de usuario duplicado"""
    with app.app_context():
        # Crear primer usuario
        AuthService.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        
        # Intentar crear usuario duplicado
        success, message, user = AuthService.create_user(
            username='testuser',
            email='another@example.com',
            password='password123'
        )
        
        assert success is False
        assert 'ya existe' in message
        assert user is None


def test_warranty_activation(app):
    """Test de activación de garantía"""
    with app.app_context():
        # Preparar datos
        product = Product(code='TEST01', name='Test', category='Premium')
        db.session.add(product)
        db.session.commit()
        
        success, message, stocks = StockService.importar_stock(
            product_id=product.id,
            quantity=1
        )
        
        # Obtener primera garantía
        from app.models.warranty import Warranty
        warranty = Warranty.query.first()
        
        # Activar garantía
        customer_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'phone': '1234567890'
        }
        
        success, message, activated_warranty = WarrantyService.activate_warranty(
            warranty_code=warranty.code,
            customer_data=customer_data,
            vehicle_info='Toyota Camry 2020'
        )
        
        assert success is True
        assert activated_warranty.status == 'active'
        assert activated_warranty.customer is not None
