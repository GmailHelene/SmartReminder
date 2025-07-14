#!/usr/bin/env python3
"""Test forgot password functionality"""

import requests
import json

def test_forgot_password():
    """Test forgot password endpoint"""
    
    base_url = "http://localhost:5000"
    
    print("🔍 Testing forgot password functionality...")
    
    # Test forgot password endpoint
    test_email = "test@example.com"
    
    # Test with JSON payload
    print(f"Testing forgot password with email: {test_email}")
    
    try:
        response = requests.post(
            f"{base_url}/forgot-password",
            json={'email': test_email},
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Forgot password functionality works")
                return True
            else:
                print(f"❌ Forgot password failed: {data.get('message')}")
                return False
        else:
            print(f"❌ HTTP error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing forgot password: {e}")
        return False

if __name__ == "__main__":
    test_forgot_password()
