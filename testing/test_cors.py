#!/usr/bin/env python3
"""
Test CORS configuration
"""

import requests

def test_cors():
    """Test CORS headers are present."""
    print("Testing CORS configuration...")
    
    # Test preflight request
    headers = {
        'Origin': 'http://localhost:5173',
        'Access-Control-Request-Method': 'GET',
        'Access-Control-Request-Headers': 'Content-Type'
    }
    
    try:
        response = requests.options('http://localhost:8000/api/v1/jobs', headers=headers)
        print(f"OPTIONS request status: {response.status_code}")
        print(f"CORS headers: {dict(response.headers)}")
        
        if 'Access-Control-Allow-Origin' in response.headers:
            print("✅ CORS is properly configured!")
        else:
            print("❌ CORS headers missing")
            
    except Exception as e:
        print(f"❌ Error testing CORS: {e}")

if __name__ == "__main__":
    test_cors() 