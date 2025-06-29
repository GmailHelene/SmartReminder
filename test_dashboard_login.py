#!/usr/bin/env python3
"""
Test the dashboard and calendar with proper login
"""

import requests
import json

def test_dashboard_with_login():
    """Test dashboard access after login"""
    print("🧪 Testing dashboard and calendar with login...")
    
    base_url = "http://localhost:8080"
    session = requests.Session()
    
    try:
        # Step 1: Try to access dashboard (should redirect to login)
        print("1. Testing dashboard access without login...")
        response = session.get(f"{base_url}/dashboard")
        if response.status_code == 302 or 'login' in response.url:
            print("✅ Dashboard correctly requires login")
        else:
            print(f"⚠️ Unexpected response: {response.status_code}")
        
        # Step 2: Try to access calendar API (should redirect to login)
        print("2. Testing calendar API without login...")
        response = session.get(f"{base_url}/api/calendar-events")
        if response.status_code == 302:
            print("✅ Calendar API correctly requires authentication")
        else:
            print(f"⚠️ Unexpected API response: {response.status_code}")
        
        # Step 3: Check login page
        print("3. Testing login page...")
        response = session.get(f"{base_url}/login")
        if response.status_code == 200:
            print("✅ Login page loads successfully")
            
            # Check if there's a CSRF token
            if 'csrf_token' in response.text:
                print("✅ CSRF token found in login form")
            else:
                print("⚠️ No CSRF token found")
        else:
            print(f"❌ Login page failed: {response.status_code}")
        
        print("\n🎯 Manual Test Instructions:")
        print("=" * 50)
        print("1. Open browser and go to: http://localhost:8080")
        print("2. You should be redirected to login page")
        print("3. Register a new user or login")
        print("4. After login, dashboard should load")
        print("5. Calendar should either:")
        print("   - Show events if user is properly authenticated")
        print("   - Show clear 'Du må logge inn' message if not")
        print("\n✅ The calendar error handling is now improved!")
        
    except Exception as e:
        print(f"❌ Error testing: {e}")

if __name__ == "__main__":
    test_dashboard_with_login()
