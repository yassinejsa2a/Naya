#!/usr/bin/env python3
"""
Pytest helpers for validating top-level API wiring.
"""

import pytest

from app import create_app, db


@pytest.fixture(scope="module")
def app():
    app = create_app()
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI='sqlite:///:memory:',
    )
    with app.app_context():
        db.create_all()
    yield app
    with app.app_context():
        db.drop_all()


@pytest.fixture(scope="module")
def client(app):
    with app.test_client() as client:
        yield client


def test_health_check(client):
    """Home endpoint should respond with API metadata."""
    response = client.get('/')
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["message"] == "NAYA Travel Journal API"


def test_api_structure(app):
    """API blueprint should register expected v1 routes."""
    with app.app_context():
        routes = {rule.rule for rule in app.url_map.iter_rules()}
    expected = {
        '/api/v1/places',
        '/api/v1/reviews',
        '/api/v1/photos',
        '/api/v1/auth/register',
        '/api/v1/auth/login',
    }
    assert expected.issubset(routes)


def test_placeholder_endpoints(client):
    """GET endpoints should return structured JSON responses even without data."""
    for endpoint in ('/api/v1/places', '/api/v1/reviews', '/api/v1/photos'):
        response = client.get(endpoint)
        assert response.status_code == 200
        payload = response.get_json()
        assert payload.get('success') is True
        assert 'count' in payload
