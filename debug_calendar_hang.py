#!/usr/bin/env python3
"""
Quick debug test for calendar hanging issue
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, dm
import tempfile
import unittest
from flask import session

def test_calendar_debug():
    """Debug test for calendar hanging issue"""
    
    # Test with a temporary database
    with tempfile.NamedTemporaryFile(delete=False) as f:
        temp_db_path = f.name
    
    # Override the data manager to use temp files
    from pathlib import Path
    dm.data_dir = Path(os.path.dirname(temp_db_path))
    
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    with app.test_client() as client:
        # Create a test user
        users = dm.load_data('users')
        users.append({
            'email': 'test@example.com',
            'password': 'hashed_password',
            'name': 'Test User'
        })
        dm.save_data('users', users)
        
        # Simulate login
        with client.session_transaction() as sess:
            sess['user_id'] = 'test@example.com'
            sess['_fresh'] = True
        
        print("🧪 Testing Calendar Hanging Issue Debug")
        print("=" * 50)
        
        # Test 1: Check if calendar events endpoint works
        print("\n1. Testing /api/calendar-events endpoint...")
        events_response = client.get('/api/calendar-events')
        print(f"   Status: {events_response.status_code}")
        if events_response.status_code == 200:
            data = events_response.get_json()
            print(f"   ✅ Success! Events count: {len(data)}")
        else:
            print(f"   ❌ Failed with status {events_response.status_code}")
            print(f"   Response: {events_response.get_data(as_text=True)[:200]}")
        
        # Test 2: Try to create a quick reminder via JSON
        print("\n2. Testing quick reminder creation via JSON...")
        reminder_data = {
            'title': 'Test Quick Reminder',
            'description': 'Test description',
            'date': '2024-12-25',
            'time': '10:00',
            'priority': 'Medium',
            'category': 'Test'
        }
        
        create_response = client.post('/add_reminder', 
                                    json=reminder_data,
                                    headers={'Content-Type': 'application/json'})
        
        print(f"   Status: {create_response.status_code}")
        if create_response.status_code == 200:
            data = create_response.get_json()
            print(f"   ✅ Success! Response: {data}")
        else:
            print(f"   ❌ Failed with status {create_response.status_code}")
            print(f"   Response: {create_response.get_data(as_text=True)[:300]}")
        
        # Test 3: Check dashboard loads properly
        print("\n3. Testing dashboard page...")
        dashboard_response = client.get('/dashboard')
        print(f"   Status: {dashboard_response.status_code}")
        if dashboard_response.status_code == 200:
            content = dashboard_response.get_data(as_text=True)
            
            # Check for key elements
            checks = [
                ('quickReminderForm', 'Quick reminder form'),
                ('calendar', 'Calendar element'),
                ('fullcalendar', 'FullCalendar library'),
                ('/api/calendar-events', 'Calendar events API'),
                ('preventDefault', 'Event prevention'),
            ]
            
            print("   ✅ Dashboard loaded successfully!")
            print("   Checking for key elements:")
            for check, desc in checks:
                if check.lower() in content.lower():
                    print(f"      ✅ {desc} found")
                else:
                    print(f"      ❌ {desc} missing")
        else:
            print(f"   ❌ Dashboard failed with status {dashboard_response.status_code}")
        
        # Test 4: Check for problematic code patterns
        print("\n4. Checking for problematic code patterns...")
        if dashboard_response.status_code == 200:
            content = dashboard_response.get_data(as_text=True)
            
            # Patterns that could cause issues
            problematic_patterns = [
                ('location.href =', 'Direct location assignment'),
                ('window.location =', 'Window location assignment'),
                ('form.submit()', 'Direct form submission'),
                ('action=', 'Form action attribute'),
            ]
            
            for pattern, desc in problematic_patterns:
                if pattern in content:
                    print(f"      ⚠️  {desc} found - might cause issues")
                else:
                    print(f"      ✅ {desc} not found")
        
        print("\n" + "=" * 50)
        print("🎯 Debug test completed!")
        
        # Clean up
        try:
            os.unlink(temp_db_path)
        except:
            pass

if __name__ == '__main__':
    test_calendar_debug()
