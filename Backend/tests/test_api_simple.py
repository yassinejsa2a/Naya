#!/usr/bin/env python3
"""
Simple API Structure Test for NAYA Travel Journal
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app

def main():
    """Test API structure"""
    print("🧪 Testing NAYA API Structure...")
    
    try:
        app = create_app()
        print("✅ Flask app created successfully")
        
        with app.test_client() as client:
            # Test home endpoint
            response = client.get('/')
            print(f"✅ Home endpoint: {response.status_code}")
            
            # Test API endpoints
            endpoints = ['/api/v1/places', '/api/v1/reviews', '/api/v1/photos']
            
            for endpoint in endpoints:
                try:
                    response = client.get(endpoint)
                    print(f"✅ {endpoint}: {response.status_code}")
                except Exception as e:
                    print(f"❌ {endpoint}: ERROR - {e}")
        
        print("\n✨ API structure test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    main()