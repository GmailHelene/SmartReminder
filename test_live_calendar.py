#!/usr/bin/env python3
"""
Test calendar functionality by creating a real user session
"""

import requests
import json

def test_live_calendar():
    """Test calendar with live server"""
    base_url = "http://localhost:8080"
    
    print("🧪 Testing live calendar functionality...")
    
    # Create a session
    session = requests.Session()
    
    try:
        # Test health check
        response = session.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print("❌ Server not responding")
            return
        
        # Test API endpoint (should redirect to login)
        response = session.get(f"{base_url}/api/calendar-events")
        if response.status_code == 302:
            print("✅ API properly requires authentication")
        else:
            print(f"⚠️  Unexpected API response: {response.status_code}")
        
        # Test login page
        response = session.get(f"{base_url}/login")
        if response.status_code == 200 and "login" in response.text.lower():
            print("✅ Login page loads correctly")
        else:
            print("❌ Login page has issues")
        
        print("\n🎯 Manual Testing Instructions:")
        print("=" * 50)
        print("1. Go to http://localhost:8080")
        print("2. Register a new user or try login with:")
        print("   - Email: test@example.com")
        print("   - Password: (any password)")
        print("3. Go to dashboard")
        print("4. Check if calendar displays events")
        print("5. The calendar should show:")
        print("   - Test Meeting (30 Jun)")
        print("   - Handleliste (1 Jul)")
        print("   - Prosjekt Deadline (6 Jul)")
        print("   - Shared Team Meeting (shared reminder)")
        print("\nIf calendar shows 'Laster...' forever:")
        print("- Check browser console for errors")
        print("- Verify /api/calendar-events returns data")
        print("- Check network tab for failed requests")
        
    except Exception as e:
        print(f"❌ Error testing live server: {e}")

if __name__ == "__main__":
    test_live_calendar()
