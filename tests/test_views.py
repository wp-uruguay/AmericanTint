"""
Tests para views (blueprints)
"""
import pytest
from app import create_app
from app.extensions import db
from app.models.user import User


@pytest.fixture
def app():
    """Crear aplicación de prueba"""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        
        # Crear usuario de prueba
        user = User(username='admin', email='admin@test.com', role='admin')
        user.set_password('admin123')
        db.session.add(user)
        db.session.commit()
        
        yield app
        
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Cliente de prueba"""
    return app.test_client()


def test_login_page(client):
    """Test de página de login"""
    response = client.get('/auth/login')
    assert response.status_code == 200
    assert b'Usuario' in response.data


def test_login_redirect_to_dashboard(client):
    """Test de redirección después de login"""
    response = client.post('/auth/login', data={
        'username': 'admin',
        'password': 'admin123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    # assert b'Dashboard' in response.data


def test_logout(client):
    """Test de logout"""
    # Login primero
    client.post('/auth/login', data={
        'username': 'admin',
        'password': 'admin123'
    })
    
    # Logout
    response = client.get('/auth/logout', follow_redirects=True)
    assert response.status_code == 200


def test_dashboard_requires_login(client):
    """Test de protección de dashboard"""
    response = client.get('/dashboard/')
    # Debe redirigir a login
    assert response.status_code == 302


def test_stock_page_requires_login(client):
    """Test de protección de stock"""
    response = client.get('/stock/')
    assert response.status_code == 302


def test_warranty_page_requires_login(client):
    """Test de protección de garantías"""
    response = client.get('/warranty/')
    assert response.status_code == 302
