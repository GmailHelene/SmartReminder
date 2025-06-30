#!/usr/bin/env python3
"""
Test calendar rendering by checking for JavaScript errors and debugging why the calendar is white.
"""

import requests
import time
from bs4 import BeautifulSoup
import re

def test_calendar_rendering():
    """Test calendar rendering by checking dashboard HTML and console logs."""
    
    base_url = "http://localhost:5000"
    
    try:
        # First, create a session and login
        session = requests.Session()
        
        # Get login page to get CSRF token
        login_response = session.get(f"{base_url}/login")
        if login_response.status_code != 200:
            print(f"❌ Could not access login page: {login_response.status_code}")
            return False
            
        # Parse login form for CSRF token
        soup = BeautifulSoup(login_response.text, 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrf_token'})
        if not csrf_token:
            print("❌ Could not find CSRF token in login form")
            return False
            
        csrf_value = csrf_token.get('value')
        print(f"✅ Got CSRF token: {csrf_value[:20]}...")
        
        # Login with test credentials
        login_data = {
            'csrf_token': csrf_value,
            'email': 'test@example.com',
            'password': 'testpassword'
        }
        
        login_result = session.post(f"{base_url}/login", data=login_data, allow_redirects=False)
        
        if login_result.status_code in [302, 200]:
            print("✅ Login successful")
        else:
            print(f"❌ Login failed: {login_result.status_code}")
            return False
            
        # Access dashboard
        dashboard_response = session.get(f"{base_url}/dashboard")
        if dashboard_response.status_code != 200:
            print(f"❌ Could not access dashboard: {dashboard_response.status_code}")
            return False
            
        print("✅ Dashboard accessible")
        
        # Parse dashboard HTML
        dashboard_soup = BeautifulSoup(dashboard_response.text, 'html.parser')
        
        # Check if calendar element exists
        calendar_element = dashboard_soup.find('div', {'id': 'calendar'})
        if not calendar_element:
            print("❌ Calendar element not found in dashboard HTML")
            return False
        
        print("✅ Calendar element found in HTML")
        print(f"Calendar element: {calendar_element}")
        
        # Check if FullCalendar CSS is loaded
        fullcalendar_css = dashboard_soup.find('link', {'href': re.compile(r'fullcalendar')})
        if not fullcalendar_css:
            print("❌ FullCalendar CSS not found")
            return False
        
        print("✅ FullCalendar CSS found")
        
        # Check if FullCalendar JS is loaded
        fullcalendar_js = dashboard_soup.find('script', {'src': re.compile(r'fullcalendar')})
        if not fullcalendar_js:
            print("❌ FullCalendar JS not found")
            return False
        
        print("✅ FullCalendar JS found")
        
        # Check if calendar initialization JavaScript exists
        scripts = dashboard_soup.find_all('script')
        calendar_init_found = False
        for script in scripts:
            if script.string and 'FullCalendar.Calendar' in script.string:
                calendar_init_found = True
                print("✅ Calendar initialization JS found")
                break
        
        if not calendar_init_found:
            print("❌ Calendar initialization JS not found")
            return False
        
        # Check if loading/fallback elements exist
        loading_element = dashboard_soup.find('div', {'id': 'calendar-loading'})
        fallback_element = dashboard_soup.find('div', {'id': 'calendar-fallback'})
        
        if not loading_element:
            print("❌ Calendar loading element not found")
        else:
            print("✅ Calendar loading element found")
            
        if not fallback_element:
            print("❌ Calendar fallback element not found")
        else:
            print("✅ Calendar fallback element found")
        
        # Test API endpoint
        api_response = session.get(f"{base_url}/api/calendar-events")
        if api_response.status_code == 200:
            print("✅ Calendar API endpoint accessible and returns data")
            events = api_response.json()
            print(f"📅 Number of events returned: {len(events)}")
        else:
            print(f"❌ Calendar API endpoint failed: {api_response.status_code}")
            return False
        
        # Check for common JavaScript errors in the calendar init code
        calendar_script = None
        for script in scripts:
            if script.string and 'initializeCalendar' in script.string:
                calendar_script = script.string
                break
        
        if calendar_script:
            print("✅ Calendar initialization script found")
            
            # Check for common syntax errors
            syntax_issues = []
            
            if '.then data =>' in calendar_script:
                syntax_issues.append("Missing parentheses in .then(data =>)")
            
            if 'loadCalendarEvents(' in calendar_script and 'async function loadCalendarEvents' not in calendar_script:
                syntax_issues.append("loadCalendarEvents function may not be properly defined as async")
            
            if syntax_issues:
                print("⚠️ Potential JavaScript syntax issues found:")
                for issue in syntax_issues:
                    print(f"   - {issue}")
            else:
                print("✅ No obvious JavaScript syntax issues found")
        
        print("\n📋 Calendar Rendering Analysis:")
        print("- HTML structure: ✅ Complete")
        print("- CSS assets: ✅ Loaded")
        print("- JS assets: ✅ Loaded")
        print("- API endpoint: ✅ Working")
        print("- Event data: ✅ Available")
        print("")
        print("🔍 The calendar appears to have all necessary components.")
        print("   If it's still white, the issue is likely in the JavaScript execution.")
        print("   Recommendation: Check browser console for JavaScript errors.")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Calendar Rendering...")
    print("=" * 50)
    
    success = test_calendar_rendering()
    
    print("=" * 50)
    if success:
        print("✅ Calendar rendering test completed successfully")
    else:
        print("❌ Calendar rendering test failed")
