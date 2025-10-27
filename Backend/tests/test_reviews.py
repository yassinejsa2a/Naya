#!/usr/bin/env python3
"""
Integration tests for the reviews API.
"""

import pytest


def _create_place(client, headers, **overrides):
    payload = {
        'name': 'Sample Place',
        'description': 'A scenic destination used in tests.',
        'city': 'Sample City',
        'country': 'Sample Country',
        'latitude': 10.0,
        'longitude': 20.0,
    }
    payload.update(overrides)
    response = client.post('/api/v1/places', json=payload, headers=headers)
    assert response.status_code == 201, response.get_json()
    return response.get_json()['data']


def _create_review(client, headers, place_id, **overrides):
    payload = {
        'title': 'Great Experience',
        'content': 'Had an amazing time exploring the area.',
        'rating': 5,
        'summary': 'A memorable trip.',
        'place_id': place_id,
    }
    payload.update(overrides)
    response = client.post('/api/v1/reviews', json=payload, headers=headers)
    assert response.status_code == 201, response.get_json()
    return response.get_json()['data']


def test_review_lifecycle_and_statistics(api_client, user_factory):
    """Full lifecycle: create, update, search, stats, delete."""
    author = user_factory(email='writer@example.com', username='writer')
    place = _create_place(
        api_client,
        author['headers'],
        name='Sunken Garden',
        city='Iloilo',
        country='Philippines',
        latitude=10.705,
        longitude=122.546
    )

    creation = _create_review(
        api_client,
        author['headers'],
        place_id=place['id'],
        title='Sunset memories',
        content='Watching the sunset over Sunken Garden was breathtaking!',
        rating=4,
        visit_date='2023-08-15'
    )
    review_id = creation['review']['id']

    update_resp = api_client.put(
        f'/api/v1/reviews/{review_id}',
        json={
            'title': 'Updated sunset memories',
            'content': 'Updated: the evening breeze made it perfect.',
            'rating': 5
        },
        headers=author['headers']
    )
    assert update_resp.status_code == 200

    detail_resp = api_client.get(f'/api/v1/reviews/{review_id}')
    assert detail_resp.status_code == 200
    detail = detail_resp.get_json()['data']
    assert detail['title'] == 'Updated sunset memories'
    assert detail['rating'] == 5

    search_resp = api_client.get('/api/v1/reviews', query_string={'search': 'sunset'})
    assert search_resp.status_code == 200
    search_payload = search_resp.get_json()
    assert search_payload['count'] == 1
    assert search_payload['reviews'][0]['title'] == 'Updated sunset memories'

    stats_resp = api_client.get(f'/api/v1/reviews/statistics/{place["id"]}')
    assert stats_resp.status_code == 200
    stats = stats_resp.get_json()['data']
    assert stats['total_reviews'] == 1
    assert pytest.approx(stats['average_rating']) == 5
    rating_distribution = {int(key): value for key, value in stats['rating_distribution'].items()}
    assert rating_distribution[5] == 1

    delete_resp = api_client.delete(f'/api/v1/reviews/{review_id}', headers=author['headers'])
    assert delete_resp.status_code == 200

    stats_after = api_client.get(f'/api/v1/reviews/statistics/{place["id"]}')
    assert stats_after.status_code == 200
    stats_after_data = stats_after.get_json()['data']
    assert stats_after_data['total_reviews'] == 0
    assert stats_after_data['average_rating'] is None

    missing_resp = api_client.get(f'/api/v1/reviews/{review_id}')
    assert missing_resp.status_code == 404

    invalid_stats = api_client.get('/api/v1/reviews/statistics/non-existent-id')
    assert invalid_stats.status_code == 400


def test_review_permissions_and_error_paths(api_client, user_factory):
    """Only authors or admins may mutate reviews; missing resources raise errors."""
    owner = user_factory(email='owner@example.com', username='owner')
    stranger = user_factory(email='stranger@example.com', username='stranger')
    admin = user_factory(email='admin@example.com', username='adminuser')
    assert admin['user']['is_admin'] is True

    place = _create_place(api_client, owner['headers'], name='Hidden Beach', city='El Nido', country='Philippines')
    review = _create_review(
        api_client,
        owner['headers'],
        place_id=place['id'],
        title='Secret lagoon',
        content='This lagoon felt untouched and serene.',
        rating=5
    )
    review_id = review['review']['id']

    unauthorized_update = api_client.put(
        f'/api/v1/reviews/{review_id}',
        json={'content': 'Trying to hijack this review', 'rating': 3},
        headers=stranger['headers']
    )
    assert unauthorized_update.status_code == 400
    assert 'own reviews' in unauthorized_update.get_json()['error']

    unauthorized_delete = api_client.delete(
        f'/api/v1/reviews/{review_id}',
        headers=stranger['headers']
    )
    assert unauthorized_delete.status_code == 400

    admin_delete = api_client.delete(f'/api/v1/reviews/{review_id}', headers=admin['headers'])
    assert admin_delete.status_code == 200

    missing_user_reviews = api_client.get('/api/v1/reviews', query_string={'user_id': 'does-not-exist'})
    assert missing_user_reviews.status_code == 400
    assert 'User not found' in missing_user_reviews.get_json()['error']

    missing_place_reviews = api_client.get('/api/v1/reviews', query_string={'place_id': 'missing-place'})
    assert missing_place_reviews.status_code == 400
    assert 'Place not found' in missing_place_reviews.get_json()['error']


def test_review_creation_requires_place_context(api_client, user_factory):
    """Creating a review without place info fails, but inline place payloads succeed."""
    author = user_factory(email='context@example.com', username='context')

    missing_place_resp = api_client.post(
        '/api/v1/reviews',
        json={
            'title': 'Nowhere trip',
            'content': 'Forgot to mention the place entirely.',
            'rating': 4,
        },
        headers=author['headers']
    )
    assert missing_place_resp.status_code == 400
    assert 'Place information is required' in missing_place_resp.get_json()['error']

    inline_place_payload = {
        'title': 'Hidden rooftops',
        'content': 'These rooftops had the best view over the old town.',
        'rating': 5,
        'place': {
            'name': 'Old Town Rooftop',
            'city': 'Nice',
            'country': 'France',
            'description': 'Overlooks the Mediterranean.',
            'latitude': '43.6977',
            'longitude': '7.2718'
        }
    }
    inline_resp = api_client.post('/api/v1/reviews', json=inline_place_payload, headers=author['headers'])
    assert inline_resp.status_code == 201
    created_review = inline_resp.get_json()['data']['review']
    assert created_review['place_id']

    place_detail = api_client.get(f"/api/v1/places/{created_review['place_id']}")
    assert place_detail.status_code == 200
    assert place_detail.get_json()['place']['name'] == 'Old Town Rooftop'

    duplicate_review = api_client.post(
        '/api/v1/reviews',
        json={
            'title': 'Second take',
            'content': 'Trying to review the same place twice.',
            'rating': 4,
            'place_id': created_review['place_id']
        },
        headers=author['headers']
    )
    assert duplicate_review.status_code == 400
    assert 'already reviewed' in duplicate_review.get_json()['error']
