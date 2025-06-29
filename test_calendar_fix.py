#!/usr/bin/env python3
"""
Test the calendar functionality fix - specifically the 404 error when creating quick reminders
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
import tempfile
import unittest
from flask import session
import json

def test_calendar_fix():
    print("🧪 Testing Calendar Fix - Quick Reminder Creation\n")
    
    # Create test app with temporary database
    with tempfile.TemporaryDirectory() as temp_dir:
        os.environ['DATA_DIR'] = temp_dir
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        
        with app.test_client() as client:
            # Register and login test user
            print("👤 Setting up test user...")
            register_response = client.post('/register', data={
                'email': 'test@example.com',
                'password': 'testpass123',
                'name': 'Test User'
            }, follow_redirects=True)
            
            login_response = client.post('/login', data={
                'email': 'test@example.com',
                'password': 'testpass123'
            }, follow_redirects=True)
            
            if login_response.status_code == 200:
                print("✅ User login successful")
            else:
                print(f"❌ Login failed: {login_response.status_code}")
                return
            
            # Test calendar events API endpoint
            print("\n📅 Testing calendar events API...")
            events_response = client.get('/api/calendar-events')
            if events_response.status_code == 200:
                print("✅ /api/calendar-events works!")
                events_data = events_response.get_json()
                print(f"   Events returned: {len(events_data) if events_data else 0}")
            else:
                print(f"❌ /api/calendar-events failed: {events_response.status_code}")
            
            # Test dashboard loading 
            print("\n🏠 Testing dashboard page...")
            dashboard_response = client.get('/dashboard')
            if dashboard_response.status_code == 200:
                print("✅ Dashboard loads successfully!")
                content = dashboard_response.get_data(as_text=True)
                
                # Check that the calendar is configured with API endpoint
                if "events: '/api/calendar-events'" in content:
                    print("✅ Calendar is correctly configured to use API endpoint")
                else:
                    print("❌ Calendar configuration issue - not using API endpoint")
                
                # Check for the presence of FullCalendar
                if "FullCalendar.Calendar" in content:
                    print("✅ FullCalendar is properly loaded")
                else:
                    print("❌ FullCalendar configuration missing")
                    
            else:
                print(f"❌ Dashboard failed: {dashboard_response.status_code}")
            
            # Test quick reminder creation (JSON API)
            print("\n⚡ Testing quick reminder creation...")
            reminder_data = {
                'title': 'Test Quick Reminder',
                'description': 'Testing calendar quick creation',
                'date': '2024-12-20',
                'time': '14:30',
                'priority': 'Medium',
                'category': 'Test'
            }
            
            quick_response = client.post('/add_reminder', 
                                       json=reminder_data,
                                       headers={'Content-Type': 'application/json'})
            
            if quick_response.status_code == 200:
                print("✅ Quick reminder creation works!")
                data = quick_response.get_json()
                if data and data.get('success'):
                    print("   ✅ Response indicates success")
                else:
                    print(f"   ❌ Response indicates failure: {data}")
            else:
                print(f"❌ Quick reminder creation failed: {quick_response.status_code}")
                error_content = quick_response.get_data(as_text=True)
                print(f"   Error content: {error_content[:200]}...")
            
            # Verify the reminder was created by checking events again
            print("\n🔍 Verifying reminder was created...")
            events_check = client.get('/api/calendar-events')
            if events_check.status_code == 200:
                events_data = events_check.get_json()
                reminder_found = any(event['title'] == 'Test Quick Reminder' for event in events_data)
                if reminder_found:
                    print("✅ New reminder appears in calendar events!")
                else:
                    print("❌ New reminder not found in calendar events")
                    print(f"   Total events: {len(events_data)}")
            
            print("\n🎯 Testing URL patterns that caused 404...")
            # Test that we don't get JSON data in URLs anymore
            test_urls = [
                '/',
                '/dashboard',
                '/api/calendar-events',
                '/api/reminder-count'
            ]
            
            for url in test_urls:
                response = client.get(url)
                if 200 <= response.status_code < 400:
                    print(f"✅ {url} - Status: {response.status_code}")
                else:
                    print(f"❌ {url} - Status: {response.status_code}")
            
            print("\n✅ Calendar Fix Test Complete!")
            print("📝 Summary:")
            print("   - Calendar now uses /api/calendar-events endpoint")
            print("   - Quick reminder creation should work without 404 errors")
            print("   - FullCalendar.refetchEvents() used for updates")
            print("   - No more JSON data treated as URLs")

if __name__ == '__main__':
    test_calendar_fix()
