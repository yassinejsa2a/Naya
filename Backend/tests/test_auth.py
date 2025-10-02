#!/usr/bin/env python3
"""
Unit tests for NAYA Travel Journal authentication
"""
import pytest
import json
from app import create_app, db
from app.models.user import User

@pytest.fixture
def app():
    """Create test app"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
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
    
    response = client.post('/api/register', 
                          data=json.dumps(data),
                          content_type='application/json')
    
    assert response.status_code == 201
    result = json.loads(response.data)
    assert result['message'] == 'User created successfully'
    assert 'user_id' in result

def test_register_missing_fields(client):
    """Test registration with missing fields"""
    data = {
        'username': 'newuser',
        'email': 'newuser@example.com'
        # password missing
    }
    
    response = client.post('/api/register',
                          data=json.dumps(data),
                          content_type='application/json')
    
    assert response.status_code == 400
    result = json.loads(response.data)
    assert 'error' in result

def test_register_duplicate_email(client, sample_user):
    """Test registration with existing email"""
    data = {
        'username': 'newuser',
        'email': 'test@example.com',  # Same as sample_user
        'password': 'password123'
    }
    
    response = client.post('/api/register',
                          data=json.dumps(data),
                          content_type='application/json')
    
    assert response.status_code == 409
    result = json.loads(response.data)
    assert 'already registered' in result['error']

def test_login_success(client, sample_user):
    """Test successful login"""
    data = {
        'email': 'test@example.com',
        'password': 'password123'
    }
    
    response = client.post('/api/login',
                          data=json.dumps(data),
                          content_type='application/json')
    
    assert response.status_code == 200
    result = json.loads(response.data)
    assert 'token' in result
    assert result['username'] == 'testuser'

def test_login_invalid_credentials(client, sample_user):
    """Test login with invalid credentials"""
    data = {
        'email': 'test@example.com',
        'password': 'wrongpassword'
    }
    
    response = client.post('/api/login',
                          data=json.dumps(data),
                          content_type='application/json')
    
    assert response.status_code == 401
    result = json.loads(response.data)
    assert 'Invalid email or password' in result['error']

def test_get_profile(client, sample_user):
    """Test getting user profile"""
    # First login to get token
    login_data = {
        'email': 'test@example.com',
        'password': 'password123'
    }
    
    login_response = client.post('/api/login',
                                data=json.dumps(login_data),
                                content_type='application/json')
    
    token = json.loads(login_response.data)['token']
    
    # Get profile with token
    response = client.get('/api/profile',
                         headers={'Authorization': f'Bearer {token}'})
    
    assert response.status_code == 200
    result = json.loads(response.data)
    assert result['username'] == 'testuser'
    assert result['email'] == 'test@example.com'

def test_get_profile_no_token(client):
    """Test getting profile without token"""
    response = client.get('/api/profile')
    
    assert response.status_code == 401