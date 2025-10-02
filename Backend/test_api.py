#!/usr/bin/env python3
"""
Test NAYA Travel Journal API
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5000/api/v1"

def test_health_check():
    """Test health check"""
    try:
        response = requests.get("http://127.0.0.1:5000/")
        print(f"✅ Health Check: {response.status_code}")
        print(f"   Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Health Check failed: {e}")
        return False

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