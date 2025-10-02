#!/usr/bin/env python3
"""
Test NAYA Travel Journal API - Comprehensive Backend Testing
"""

import sys
import os

import requests
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app

def test_api_structure():
    """Test API structure and routes"""
    print("🧪 Testing NAYA API Structure...")
    
    app = create_app()
    
    with app.test_client() as client:
        # Test home endpoint
        response = client.get('/')
        print(f"✅ Home endpoint: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.get_json()}")
        
        # Check all registered routes
        with app.app_context():
            routes = []
            for rule in app.url_map.iter_rules():
                methods = rule.methods or set()
                routes.append(f"{sorted(list(methods))} {rule.rule}")
            
            print("\n📍 All registered routes:")
            for route in sorted(routes):
                print(f"  {route}")
            
            # Filter API v1 routes
            api_routes = [route for route in routes if '/api/v1' in route]
            print(f"\n📡 API v1 routes found: {len(api_routes)}")
        
        # Test GET endpoints (should work without auth)
        print("\n🔍 Testing GET endpoints:")
        
        endpoints = [
            '/api/v1/places',
            '/api/v1/reviews', 
            '/api/v1/photos'
        ]
        
        for endpoint in endpoints:
            try:
                response = client.get(endpoint)
                print(f"  {endpoint}: {response.status_code}")
                if response.status_code == 200:
                    data = response.get_json()
                    if data and 'success' in data:
                        print(f"    Success: {data['success']}")
            except Exception as e:
                print(f"  {endpoint}: ERROR - {e}")
    
    print("\n✨ API structure test completed!")
    return True

def test_auth_endpoints():
    """Test authentication endpoints"""
    print("\n🔐 Testing Authentication Endpoints...")
    
    # Test registration
    try:
        register_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123",
            "first_name": "Test",
            "last_name": "User"
        }
        
        response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        print(f"   Register: {response.status_code}")
        
        if response.status_code == 201:
            print("   ✅ Registration successful")
            
            # Test login
            login_data = {
                "email": "test@example.com",
                "password": "testpassword123"
            }
            
            login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
            print(f"   Login: {login_response.status_code}")
            
            if login_response.status_code == 200:
                token = login_response.json().get('access_token')
                print("   ✅ Login successful")
                
                # Test profile endpoint
                headers = {"Authorization": f"Bearer {token}"}
                profile_response = requests.get(f"{BASE_URL}/auth/profile", headers=headers)
                print(f"   Profile: {profile_response.status_code}")
                
                if profile_response.status_code == 200:
                    print("   ✅ Profile access successful")
                    return token
                else:
                    print("   ❌ Profile access failed")
            else:
                print("   ❌ Login failed")
        else:
            print(f"   ❌ Registration failed: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Auth test failed: {e}")
    
    return None

def test_placeholder_endpoints(token):
    """Test placeholder endpoints for places, reviews, photos"""
    print("\n📍 Testing Placeholder Endpoints...")
    
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    endpoints = [
        ("GET", "/places", "Places list"),
        ("GET", "/reviews", "Reviews list"), 
        ("GET", "/photos", "Photos list")
    ]
    
    for method, endpoint, description in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
            
            print(f"   {description}: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ {description} endpoint working")
            else:
                print(f"   ⚠️  {description} returned {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ {description} failed: {e}")

def main():
    """Run all API tests"""
    print("Testing NAYA Travel Journal API")
    print("=" * 50)
    
    # Test health check
    if not test_health_check():
        print("❌ Server not running. Start with: python run.py")
        return
    
    # Test authentication
    token = test_auth_endpoints()
    
    # Test other endpoints
    test_placeholder_endpoints(token)
    
    print("\n" + "=" * 50)
    print("✨ API Test Complete!")
    print("📝 Note: Some endpoints are placeholders and will be implemented with full services")

if __name__ == "__main__":
    main()