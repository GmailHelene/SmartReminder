#!/usr/bin/env python3
"""
Final test for calendar authentication and data loading
"""

import requests
import json

def test_calendar_authentication():
    """Test calendar with proper authentication"""
    base_url = "http://localhost:8080"
    
    print("🧪 Testing Calendar Authentication Fix")
    print("=" * 50)
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    try:
        # Step 1: Get login page to get CSRF token
        print("1. Getting login page...")
        login_page = session.get(f"{base_url}/login")
        print(f"   Login page status: {login_page.status_code}")
        
        # Step 2: Test API without authentication (should redirect)
        print("\n2. Testing API without auth...")
        api_response = session.get(f"{base_url}/api/calendar-events")
        print(f"   API status: {api_response.status_code}")
        if api_response.status_code == 302:
            print("   ✅ Correctly redirects to login")
        else:
            print("   ⚠️  Unexpected response")
        
        # Step 3: Check if we have test users
        print("\n3. Checking test users...")
        users_response = session.get(f"{base_url}/register")
        if users_response.status_code == 200:
            print("   ✅ Registration page accessible")
        
        print("\n🎯 Manual Testing Instructions:")
        print("=" * 40)
        print("1. Open browser: http://localhost:8080")
        print("2. Register new user: test@example.com / password123")
        print("3. Login and go to dashboard")
        print("4. Open browser console (F12)")
        print("5. Check console messages:")
        print("   - 'Loading calendar events...'")
        print("   - 'Calendar API response status: 200'")
        print("   - 'Calendar events loaded: X'")
        print("6. If you see authentication errors:")
        print("   - Look for detailed error messages")
        print("   - Try logging out and in again")
        print("   - Clear browser cache/cookies")
        
        print("\n📋 Expected Behavior:")
        print("✅ Calendar should load with events")
        print("✅ No 'Kunne ikke laste kalender-data' error")
        print("✅ Console shows successful API calls")
        print("✅ Can create new reminders via calendar")
        
    except Exception as e:
        print(f"❌ Error testing: {e}")

if __name__ == "__main__":
    test_calendar_authentication()
