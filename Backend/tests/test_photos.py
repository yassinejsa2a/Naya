#!/usr/bin/env python3
"""
Tests for photo upload workflow.
"""

import io
import os

import pytest

from app import create_app, db


@pytest.fixture
def app(tmp_path):
    """Create a fresh app with an isolated upload directory."""
    app = create_app()
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI='sqlite:///:memory:',
        ADMIN_EMAILS=['admin@example.com'],
        UPLOAD_FOLDER=str(tmp_path / 'uploads'),
    )
    with app.app_context():
        db.create_all()
    yield app
    with app.app_context():
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def _auth_headers(client):
    """Register and login a demo user, returning auth headers."""
    register_payload = {
        'username': 'demo',
        'email': 'demo@example.com',
        'password': 'demopass'
    }
    client.post('/api/v1/auth/register', json=register_payload)

    login_resp = client.post(
        '/api/v1/auth/login',
        json={'login': 'demo@example.com', 'password': 'demopass'}
    )
    token = login_resp.get_json()['access_token']
    return {'Authorization': f'Bearer {token}'}


def test_photo_upload_without_additional_metadata(client, app, tmp_path):
    """Uploading a photo with only the file should succeed and expose a file URL."""
    headers = _auth_headers(client)
    image_stream = io.BytesIO(b'GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff'
                              b'\x00\x00\x00!\xf9\x04\x00\x00\x00\x00\x00,\x00'
                              b'\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;')

    response = client.post(
        '/api/v1/photos',
        data={'photo_file': (image_stream, 'sample.gif')},
        headers=headers
    )

    assert response.status_code == 201
    payload = response.get_json()
    assert payload['success'] is True

    photo_info = payload['data']
    assert photo_info['file_url']
    saved_path = os.path.join(app.config['UPLOAD_FOLDER'], photo_info['filename'])
    assert os.path.exists(saved_path)

    # Photo should be retrievable via the public file endpoint.
    file_resp = client.get(f"/api/v1/photos/files/{photo_info['filename']}")
    assert file_resp.status_code == 200


def test_admin_can_delete_foreign_photo(client, app, tmp_path):
    """Admin users can delete photos they did not upload."""
    # Regular user uploads a photo
    user_headers = _auth_headers(client)
    image_stream = io.BytesIO(b'GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff'
                              b'\x00\x00\x00!\xf9\x04\x00\x00\x00\x00\x00,\x00'
                              b'\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;')

    upload_resp = client.post(
        '/api/v1/photos',
        data={'photo_file': (image_stream, 'user.gif')},
        headers=user_headers
    )
    photo_id = upload_resp.get_json()['data']['id']

    # Register admin account
    client.post('/api/v1/auth/register', json={
        'username': 'admin',
        'email': 'admin@example.com',
        'password': 'password123'
    })
    admin_login = client.post(
        '/api/v1/auth/login',
        json={'login': 'admin@example.com', 'password': 'password123'}
    )
    admin_headers = {'Authorization': f"Bearer {admin_login.get_json()['access_token']}"}

    # Admin deletes the photo uploaded by another user
    delete_resp = client.delete(f'/api/v1/photos/{photo_id}', headers=admin_headers)
    assert delete_resp.status_code == 200

    # Photo should no longer exist
    get_resp = client.get(f'/api/v1/photos/{photo_id}')
    assert get_resp.status_code == 404
