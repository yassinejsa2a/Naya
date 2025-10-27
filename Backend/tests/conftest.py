#!/usr/bin/env python3
"""
Shared pytest fixtures for API-level tests.
"""

import pytest

from app import create_app, db


@pytest.fixture
def api_app(monkeypatch, tmp_path):
    """Create a fresh Flask app configured for API integration tests."""
    monkeypatch.setenv('FLASK_ENV', 'testing')
    monkeypatch.setenv('ADMIN_EMAILS', 'admin@example.com')
    monkeypatch.delenv('ADMIN_DEFAULT_EMAIL', raising=False)
    monkeypatch.delenv('ADMIN_DEFAULT_PASSWORD', raising=False)

    app = create_app()
    upload_dir = tmp_path / 'uploads'
    upload_dir.mkdir(parents=True, exist_ok=True)
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI='sqlite:///:memory:',
        UPLOAD_FOLDER=str(upload_dir),
        WTF_CSRF_ENABLED=False,
    )

    with app.app_context():
        db.create_all()

    yield app

    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def api_client(api_app):
    """Return a test client bound to the API app."""
    with api_app.test_client() as client:
        yield client


@pytest.fixture
def user_factory(api_client):
    """
    Register and authenticate users on demand.
    Returns dict with headers, user payload, and tokens.
    """
    def _create_user(email='user@example.com', username=None, password='Password123!'):
        username = username or email.split('@')[0]
        register_payload = {
            'username': username,
            'email': email,
            'password': password
        }
        response = api_client.post('/api/v1/auth/register', json=register_payload)
        assert response.status_code == 201, response.get_json()

        login_resp = api_client.post(
            '/api/v1/auth/login',
            json={'login': email, 'password': password}
        )
        assert login_resp.status_code == 200, login_resp.get_json()
        tokens = login_resp.get_json()

        return {
            'headers': {'Authorization': f"Bearer {tokens['access_token']}"},
            'user': tokens['user'],
            'tokens': tokens,
            'password': password,
            'email': email,
        }

    return _create_user
