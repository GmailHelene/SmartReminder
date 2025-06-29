#!/usr/bin/env python3
"""Test mobile calendar fixes"""

import requests
import time

def test_mobile_calendar():
    """Test the mobile calendar functionality"""
    base_url = "https://smartremind-production.up.railway.app"
    
    print("🧪 Testing mobile calendar fixes...")
    
    try:
        # Test main dashboard page
        print("🔍 Testing dashboard page...")
        response = requests.get(base_url, timeout=10)
        if response.status_code == 200:
            print("✅ Dashboard page loads successfully!")
            
            # Check for FullCalendar includes
            content = response.text
            if 'fullcalendar' in content.lower():
                print("✅ FullCalendar library included!")
            else:
                print("❌ FullCalendar library not found")
                
            # Check for mobile-specific calendar code
            if 'window.innerWidth < 768' in content:
                print("✅ Mobile responsive calendar code found!")
            else:
                print("❌ Mobile responsive code not found")
                
            # Check for calendar element
            if 'id="calendar"' in content:
                print("✅ Calendar element found!")
            else:
                print("❌ Calendar element not found")
                
        else:
            print(f"❌ Dashboard failed: {response.status_code}")
        
        # Test calendar events API
        print("\n🔍 Testing calendar events API...")
        api_response = requests.get(f"{base_url}/api/calendar-events", timeout=10, allow_redirects=False)
        if api_response.status_code in [200, 401, 302]:  # 401/302 = needs auth, which is expected
            print("✅ Calendar events API endpoint accessible!")
        else:
            print(f"❌ Calendar events API failed: {api_response.status_code}")
        
        # Test CSS file for mobile styles
        print("\n🔍 Testing mobile CSS styles...")
        css_response = requests.get(f"{base_url}/static/css/style.css", timeout=10)
        if css_response.status_code == 200:
            css_content = css_response.text
            if 'fc-' in css_content and 'max-width: 768px' in css_content:
                print("✅ Mobile calendar CSS styles found!")
            else:
                print("❌ Mobile calendar CSS styles not found")
        else:
            print(f"❌ CSS file not accessible: {css_response.status_code}")
        
        print("\n🎉 Mobile calendar test completed!")
        print("\n📱 MOBILE TESTING RECOMMENDATIONS:")
        print("1. Open browser developer tools")
        print("2. Enable mobile device simulation (iPhone/Android)")
        print("3. Navigate to dashboard")
        print("4. Check console for calendar debug messages")
        print("5. Verify calendar shows up (not white)")
        print("6. Test calendar interactions (click dates, etc.)")
        
    except Exception as e:
        print(f"❌ Error testing mobile calendar: {e}")

if __name__ == "__main__":
    test_mobile_calendar()
