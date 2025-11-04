#!/usr/bin/env python3
"""
Integration tests for places endpoints.
"""


def _create_place(client, headers, **overrides):
    payload = {
        'name': 'Test Landmark',
        'description': 'A bucket-list destination.',
        'city': 'Sample City',
        'country': 'Sample Country',
        'latitude': 12.34,
        'longitude': 56.78,
    }
    payload.update(overrides)
    response = client.post('/api/v1/places', json=payload, headers=headers)
    assert response.status_code == 201, response.get_json()
    return response.get_json()['data'], payload


def _create_review(client, headers, place_id, **overrides):
    payload = {
        'title': 'Glowing review',
        'content': 'Loved every second spent at this spot.',
        'rating': 5,
        'place_id': place_id,
    }
    payload.update(overrides)
    response = client.post('/api/v1/reviews', json=payload, headers=headers)
    assert response.status_code == 201, response.get_json()
    return response.get_json()['data']


def test_place_filters_and_nearby_search(api_client, user_factory):
    """List, filter, search, and geolocate places."""
    author = user_factory(email='mapper@example.com', username='mapper')
    eiffel, eiffel_payload = _create_place(
        api_client,
        author['headers'],
        name='Eiffel Tower',
        city='Paris',
        country='France',
        latitude=48.8584,
        longitude=2.2945
    )
    opera, _ = _create_place(
        api_client,
        author['headers'],
        name='Sydney Opera House',
        city='Sydney',
        country='Australia',
        latitude=-33.8568,
        longitude=151.2153
    )

    list_resp = api_client.get('/api/v1/places')
    assert list_resp.status_code == 200
    assert list_resp.get_json()['count'] == 2

    city_resp = api_client.get('/api/v1/places', query_string={'city': 'Paris'})
    assert city_resp.status_code == 200
    assert city_resp.get_json()['count'] == 1
    assert city_resp.get_json()['places'][0]['name'] == 'Eiffel Tower'

    search_resp = api_client.get('/api/v1/places/search', query_string={'q': 'Opera'})
    assert search_resp.status_code == 200
    assert search_resp.get_json()['count'] == 1
    assert search_resp.get_json()['places'][0]['name'] == 'Sydney Opera House'

    nearby_resp = api_client.get(
        '/api/v1/places/nearby',
        query_string={'lat': 48.8584, 'lon': 2.2945, 'radius': 5}
    )
    assert nearby_resp.status_code == 200
    nearby = nearby_resp.get_json()['places']
    assert len(nearby) == 1
    assert nearby[0]['id'] == eiffel['id']
    assert abs(nearby[0]['distance_km']) < 0.1

    missing_geo = api_client.get('/api/v1/places/nearby')
    assert missing_geo.status_code == 400


def test_place_validation_and_reviews_listing(api_client, user_factory):
    """Validate place creation rules and embedded review listing."""
    author = user_factory(email='host@example.com', username='host')
    place, payload = _create_place(
        api_client,
        author['headers'],
        name='Old Port Market',
        city='Marseille',
        country='France'
    )

    duplicate_resp = api_client.post('/api/v1/places', json=payload, headers=author['headers'])
    assert duplicate_resp.status_code == 400
    assert 'already exists' in duplicate_resp.get_json()['error']

    missing_fields_resp = api_client.post(
        '/api/v1/places',
        json={'name': 'Incomplete'},
        headers=author['headers']
    )
    assert missing_fields_resp.status_code == 400
    assert 'Missing required field' in missing_fields_resp.get_json()['error']

    _create_review(
        api_client,
        author['headers'],
        place_id=place['id'],
        title='Fresh seafood',
        content='The bouillabaisse alone is worth the detour.',
        rating=4
    )

    place_detail = api_client.get(f"/api/v1/places/{place['id']}")
    assert place_detail.status_code == 200
    place_payload = place_detail.get_json()['place']
    assert place_payload['statistics']['total_reviews'] == 1
    assert place_payload['statistics']['average_rating'] == 4.0

    reviews_resp = api_client.get(f"/api/v1/places/{place['id']}/reviews")
    assert reviews_resp.status_code == 200
    reviews_payload = reviews_resp.get_json()
    assert reviews_payload['count'] == 1
    assert reviews_payload['reviews'][0]['title'] == 'Fresh seafood'

    missing_place_detail = api_client.get('/api/v1/places/bad-id')
    assert missing_place_detail.status_code == 404

    missing_place_reviews = api_client.get('/api/v1/places/bad-id/reviews')
    assert missing_place_reviews.status_code == 404
