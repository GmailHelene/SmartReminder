#!/usr/bin/env python3
"""Test calendar and email settings fixes"""

import os
os.environ['FLASK_ENV'] = 'development'
os.environ['TESTING'] = '1'

try:
    from app import app, dm
    import tempfile
    from pathlib import Path
    
    # Create temporary directory for testing
    test_dir = tempfile.mkdtemp()
    dm.data_dir = Path(test_dir)
    dm._ensure_data_files()
    
    app.config.update({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key',
        'MAIL_SUPPRESS_SEND': True
    })
    
    print("🧪 Testing calendar and email settings fixes...")
    
    with app.test_client() as client:
        # Create test user
        user_data = {
            'username': 'test@example.com',
            'password': 'testpass123'
        }
        
        # Register and login
        register_response = client.post('/register', data=user_data)
        login_response = client.post('/login', data=user_data)
        
        print("🔍 Testing email settings page...")
        email_settings_response = client.get('/email-settings')
        if email_settings_response.status_code == 200:
            print("✅ Email settings page loads successfully!")
            content = email_settings_response.get_data(as_text=True)
            if 'MAIL_SERVER' in content or 'Ikke konfigurert' in content:
                print("✅ Config variables are accessible!")
            else:
                print("❌ Config variables not found in template")
        else:
            print(f"❌ Email settings failed: {email_settings_response.status_code}")
        
        print("\n🔍 Testing API endpoints...")
        
        # Test reminder count API
        count_response = client.get('/api/reminder-count')
        if count_response.status_code == 200:
            print("✅ /api/reminder-count works!")
            data = count_response.get_json()
            print(f"   Response: {data}")
        else:
            print(f"❌ /api/reminder-count failed: {count_response.status_code}")
        
        # Test add reminder API (JSON)
        reminder_data = {
            'title': 'Test Reminder',
            'date': '2024-12-20',
            'time': '09:00',
            'description': 'Test description',
            'priority': 'Medium',
            'category': 'Test'
        }
        
        add_response = client.post('/add_reminder', 
                                 json=reminder_data,
                                 headers={'Content-Type': 'application/json'})
        
        if add_response.status_code == 200:
            print("✅ /add_reminder (JSON) works!")
            data = add_response.get_json()
            print(f"   Success: {data.get('success')}")
        else:
            print(f"❌ /add_reminder failed: {add_response.status_code}")
            print(f"   Response: {add_response.get_data(as_text=True)[:200]}")
        
        print("\n🔍 Testing dashboard page...")
        dashboard_response = client.get('/dashboard')
        if dashboard_response.status_code == 200:
            print("✅ Dashboard loads successfully!")
            content = dashboard_response.get_data(as_text=True)
            
            # Check for potential hang-causing elements
            if 'setTimeout(() => location.reload()' in content:
                print("❌ Found location.reload() in dashboard - potential hang source!")
            else:
                print("✅ No location.reload() found - hang issue likely fixed!")
                
            if 'updateReminderCount' in content:
                print("✅ updateReminderCount function found!")
            else:
                print("❌ updateReminderCount function missing!")
        else:
            print(f"❌ Dashboard failed: {dashboard_response.status_code}")

    print("\n🎉 Test completed!")
        
except Exception as e:
    print(f"❌ Error during test: {e}")
    import traceback
    traceback.print_exc()
