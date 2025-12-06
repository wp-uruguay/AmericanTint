"""
Tests para modelos
"""
import pytest
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.stock import Stock
from app.models.warranty import Warranty
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


@pytest.fixture
def client(app):
    """Cliente de prueba"""
    return app.test_client()


def test_user_password_hashing(app):
    """Test de hash de contraseñas"""
    with app.app_context():
        user = User(username='test', email='test@test.com')
        user.set_password('password123')
        
        assert user.password_hash is not None
        assert user.check_password('password123')
        assert not user.check_password('wrongpassword')


def test_stock_code_generation(app):
    """Test de generación de códigos de stock"""
    with app.app_context():
        code1 = Stock.generate_code()
        code2 = Stock.generate_code()
        
        assert code1.startswith('AT-')
        assert code2.startswith('AT-')
        assert code1 != code2
        assert len(code1) == 11  # AT-XXXXXXXX


def test_warranty_code_generation(app):
    """Test de generación de códigos de garantía"""
    with app.app_context():
        stock_code = 'AT-ABC12345'
        warranty_code = Warranty.generate_code(stock_code, 1)
        
        assert warranty_code == 'AT-ABC12345-001'
        assert warranty_code.startswith(stock_code)


def test_stock_availability_update(app):
    """Test de actualización de disponibilidad"""
    with app.app_context():
        product = Product(code='TEST01', name='Test Product', category='Premium')
        db.session.add(product)
        db.session.flush()
        
        stock = Stock(
            code='AT-TEST001',
            product_id=product.id,
            total_quantity=15,
            used_quantity=0
        )
        db.session.add(stock)
        
        stock.update_availability()
        assert stock.status == 'available'
        assert stock.available_quantity == 15
        
        stock.used_quantity = 5
        stock.update_availability()
        assert stock.status == 'partial'
        assert stock.available_quantity == 10
        
        stock.used_quantity = 15
        stock.update_availability()
        assert stock.status == 'depleted'
        assert stock.available_quantity == 0
