#!/usr/bin/env python3
"""
End-to-end test of calendar functionality
This tests the full flow: login, dashboard load, API calls
"""

import requests
import json
import time
from app import app
from flask_login import LoginManager

def test_full_calendar_flow():
    """Test complete calendar flow"""
    print("🔧 Testing complete calendar flow...")
    
    with app.test_client() as client:
        # Simulate login
        with client.session_transaction() as sess:
            sess['_user_id'] = 'test-user-123'
            sess['_fresh'] = True
        
        print("\n1. Testing dashboard load...")
        response = client.get('/dashboard')
        print(f"Dashboard status: {response.status_code}")
        
        if response.status_code == 200:
            html_content = response.get_data(as_text=True)
            print("✅ Dashboard loaded successfully")
            
            # Check if calendar element exists
            if 'id="calendar"' in html_content:
                print("✅ Calendar element found in HTML")
            else:
                print("❌ Calendar element not found in HTML")
            
            # Check if FullCalendar scripts are loaded
            if 'fullcalendar' in html_content:
                print("✅ FullCalendar scripts included")
            else:
                print("❌ FullCalendar scripts not found")
            
            # Check if error handling is present
            if 'calendar-fallback' in html_content:
                print("✅ Calendar fallback error handling found")
            else:
                print("❌ Calendar fallback error handling not found")
        else:
            print(f"❌ Dashboard failed to load: {response.status_code}")
        
        print("\n2. Testing calendar API...")
        api_response = client.get('/api/calendar-events')
        print(f"API status: {api_response.status_code}")
        
        if api_response.status_code == 200:
            try:
                events = api_response.get_json()
                print(f"✅ API returned {len(events)} events")
                
                if events:
                    print("📅 Sample event:")
                    sample_event = events[0]
                    print(f"   Title: {sample_event.get('title')}")
                    print(f"   Start: {sample_event.get('start')}")
                    print(f"   Priority: {sample_event.get('extendedProps', {}).get('priority')}")
                    
                    # Validate event structure
                    required_fields = ['id', 'title', 'start', 'backgroundColor', 'borderColor']
                    missing_fields = [field for field in required_fields if field not in sample_event]
                    
                    if not missing_fields:
                        print("✅ Event structure is valid")
                    else:
                        print(f"❌ Missing required fields: {missing_fields}")
                else:
                    print("⚠️  No events found (empty calendar)")
                    
            except Exception as e:
                print(f"❌ Error parsing API response: {e}")
        else:
            print(f"❌ API failed: {api_response.status_code}")
            print(f"Response: {api_response.get_data(as_text=True)}")
        
        print("\n3. Testing other critical routes...")
        
        # Test reminder count API
        count_response = client.get('/api/reminder-count')
        print(f"Reminder count API: {count_response.status_code}")
        if count_response.status_code == 200:
            count_data = count_response.get_json()
            print(f"✅ Reminder counts: {count_data}")
        
        print("\n🎯 Calendar Test Summary:")
        print("=" * 50)
        
        # Overall assessment
        dashboard_ok = response.status_code == 200
        api_ok = api_response.status_code == 200
        events_ok = api_response.status_code == 200 and len(api_response.get_json() or []) > 0
        
        if dashboard_ok and api_ok:
            if events_ok:
                print("✅ CALENDAR IS WORKING - Should display events")
            else:
                print("⚠️  CALENDAR IS WORKING - But no events to display")
        else:
            print("❌ CALENDAR HAS ISSUES - Needs debugging")
        
        return dashboard_ok and api_ok

if __name__ == '__main__':
    test_full_calendar_flow()
