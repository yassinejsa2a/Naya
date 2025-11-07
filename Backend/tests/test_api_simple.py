#!/usr/bin/env python3
"""
Basic smoke tests for the NAYA API to ensure public routes stay reachable.
"""

import pytest

from app import create_app


@pytest.fixture(scope="module")
def client():
    """Provide a Flask test client with the default configuration."""
    app = create_app()
    app.config.update(TESTING=True)
    with app.test_client() as test_client:
        yield test_client


def test_home_endpoint(client):
    """Home route returns a JSON payload describing the API state."""
    response = client.get('/')
    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "NAYA Travel Journal API"
    assert data["status"] == "running"


@pytest.mark.parametrize(
    "endpoint",
    [
        "/api/v1/places",
        "/api/v1/reviews",
        "/api/v1/photos",
    ],
)
def test_public_collections_are_accessible(client, endpoint):
    """Ensure read-only collection endpoints respond with HTTP 200."""
    response = client.get(endpoint)
    assert response.status_code == 200
    data = response.get_json()
    assert data.get("success") is True
