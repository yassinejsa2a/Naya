#!/usr/bin/env python3
"""
Unit tests for NAYA Travel Journal authentication
"""
import os
import pytest
from app import create_app, db
from app.models.user import User


@pytest.fixture
def app(monkeypatch):
    """Create test app"""
    monkeypatch.delenv('ADMIN_DEFAULT_EMAIL', raising=False)
    monkeypatch.delenv('ADMIN_DEFAULT_PASSWORD', raising=False)
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['ADMIN_EMAILS'] = ['admin@example.com']
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def sample_user(app):
    """Create a sample user for testing"""
    with app.app_context():
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        return user

def test_register_success(client):
    """Test successful user registration"""
    data = {
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'password123'
    }

    response = client.post('/api/v1/auth/register', json=data)
    
    assert response.status_code == 201
    result = response.get_json()
    assert result['message'] == 'User registered successfully'
    assert 'user' in result
    assert result['user']['email'] == 'newuser@example.com'
    assert result['user']['is_admin'] is False

def test_register_missing_fields(client):
    """Test registration with missing fields"""
    data = {
        'username': 'newuser',
        'email': 'newuser@example.com'
        # password missing
    }
    
    response = client.post('/api/v1/auth/register', json=data)
    
    assert response.status_code == 400
    result = response.get_json()
    assert 'error' in result

def test_register_duplicate_email(client, sample_user):
    """Test registration with existing email"""
    data = {
        'username': 'newuser',
        'email': 'test@example.com',  # Same as sample_user
        'password': 'password123'
    }
    
    response = client.post('/api/v1/auth/register', json=data)
    
    assert response.status_code == 400
    result = response.get_json()
    assert 'already registered' in result['error'].lower()

def test_login_success(client, sample_user):
    """Test successful login"""
    data = {
        'login': 'test@example.com',
        'password': 'password123'
    }
    
    response = client.post('/api/v1/auth/login', json=data)
    
    assert response.status_code == 200
    result = response.get_json()
    assert 'access_token' in result
    assert result['user']['username'] == 'testuser'
    assert result['user']['is_admin'] is False


def test_refresh_token(client, sample_user):
    """Test refresh token returns a new access token."""
    login_resp = client.post('/api/v1/auth/login', json={'login': 'test@example.com', 'password': 'password123'})
    tokens = login_resp.get_json()
    refresh = tokens['refresh_token']

    response = client.post('/api/v1/auth/refresh', headers={'Authorization': f'Bearer {refresh}'})

    assert response.status_code == 200
    payload = response.get_json()
    assert 'access_token' in payload
    assert isinstance(payload['access_token'], str)


def test_refresh_rejects_access_tokens(client, sample_user):
    """Refreshing with an access token should fail with an error from JWT."""
    login_resp = client.post('/api/v1/auth/login', json={'login': 'test@example.com', 'password': 'password123'})
    access_token = login_resp.get_json()['access_token']

    response = client.post('/api/v1/auth/refresh', headers={'Authorization': f'Bearer {access_token}'})
    assert response.status_code in (401, 422)
    payload = response.get_json()
    assert any(key in payload for key in ('msg', 'error'))


def test_register_admin_user(client):
    """Admin emails should receive admin privileges."""
    data = {
        'username': 'adminuser',
        'email': 'admin@example.com',
        'password': 'password123'
    }

    response = client.post('/api/v1/auth/register', json=data)
    assert response.status_code == 201
    result = response.get_json()
    assert result['user']['is_admin'] is True

def test_login_invalid_credentials(client, sample_user):
    """Test login with invalid credentials"""
    data = {
        'login': 'test@example.com',
        'password': 'wrongpassword'
    }
    
    response = client.post('/api/v1/auth/login', json=data)
    
    assert response.status_code == 401
    result = response.get_json()
    assert 'Invalid email or password' in result['error']

def test_get_profile(client, sample_user):
    """Test getting user profile"""
    # First login to get token
    login_data = {
        'login': 'test@example.com',
        'password': 'password123'
    }

    login_response = client.post('/api/v1/auth/login', json=login_data)
    
    token = login_response.get_json()['access_token']
    
    # Get profile with token
    response = client.get('/api/v1/auth/profile',
                         headers={'Authorization': f'Bearer {token}'})
    
    assert response.status_code == 200
    result = response.get_json()
    assert result['username'] == 'testuser'
    assert result['email'] == 'test@example.com'

def test_get_profile_no_token(client):
    """Test getting profile without token"""
    response = client.get('/api/v1/auth/profile')
    
    assert response.status_code == 401


def test_default_admin_provisioning(monkeypatch):
    """Default admin should be created when config variables are provided."""
    monkeypatch.setenv('ADMIN_EMAILS', 'bootstrap@example.com')
    monkeypatch.setenv('ADMIN_DEFAULT_EMAIL', 'bootstrap@example.com')
    monkeypatch.setenv('ADMIN_DEFAULT_PASSWORD', 'Bootstrap123')
    monkeypatch.setenv('DEV_DATABASE_URL', 'sqlite:///:memory:')

    bootstrap_app = create_app()
    bootstrap_app.config['TESTING'] = True
    assert bootstrap_app.config['ADMIN_DEFAULT_EMAIL'] == 'bootstrap@example.com'
    assert 'bootstrap@example.com' in bootstrap_app.config['ADMIN_EMAILS']

    with bootstrap_app.app_context():
        admin = User.query.filter_by(email='bootstrap@example.com').first()
        assert admin is not None
        assert admin.is_admin is True
        assert admin.check_password('Bootstrap123')
        db.drop_all()
