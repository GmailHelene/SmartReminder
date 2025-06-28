#!/usr/bin/env python3
"""Test dashboard rendering to reproduce the issue"""

import os
import tempfile
from pathlib import Path
import json

os.environ['FLASK_ENV'] = 'development'  
os.environ['TESTING'] = '1'

try:
    from app import app, dm
    from werkzeug.security import generate_password_hash
    
    # Create temporary directory for testing
    test_dir = tempfile.mkdtemp()
    dm.data_dir = Path(test_dir)
    dm._ensure_data_files()
    
    # Configure app for testing
    app.config.update({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key',
        'MAIL_SUPPRESS_SEND': True,
        'SERVER_NAME': 'localhost.localdomain'
    })
    
    print("🧪 Testing dashboard template rendering...")
    
    # Create test user
    users = {}
    test_user_id = 'test-123'
    users[test_user_id] = {
        'username': 'test@example.com',
        'email': 'test@example.com',
        'password_hash': generate_password_hash('password123'),
        'created': '2024-01-01T00:00:00',
        'focus_mode': 'normal'
    }
    dm.save_data('users', users)
    
    # Create test reminders
    reminders = [
        {
            'id': 'reminder-1',
            'user_id': 'test@example.com',
            'title': 'Test Reminder',
            'description': 'Test description',
            'datetime': '2024-12-01 10:00',
            'priority': 'High',
            'category': 'Work',
            'completed': False,
            'created': '2024-01-01T00:00:00'
        }
    ]
    dm.save_data('reminders', reminders)
    dm.save_data('shared_reminders', [])
    
    with app.test_client() as client:
        # First login the user properly
        print("🔐 Logging in user...")
        login_response = client.post('/login', data={
            'username': 'test@example.com',
            'password': 'password123'
        }, follow_redirects=False)
        
        print(f"Login response status: {login_response.status_code}")
        
        with app.app_context():
            print("🌐 Testing dashboard route...")
            response = client.get('/dashboard')
            
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 500:
                print("❌ Dashboard route failed with 500 error!")
                error_text = response.get_data(as_text=True)
                print("Error details (first 1000 chars):")
                print(error_text[:1000])
                
                # Check if it's the url_for noteboards error
                if 'noteboards' in error_text and 'BuildError' in error_text:
                    print("\n🎯 Found the noteboards BuildError!")
                    print("This confirms the issue is in template rendering.")
                else:
                    print("\n❓ Different error than expected")
            elif response.status_code == 200:
                print("✅ Dashboard rendered successfully!")
                # Check if the response contains expected content
                content = response.get_data(as_text=True)
                if 'Smart Påminner Pro' in content:
                    print("✅ Dashboard content looks correct")
                else:
                    print("⚠️  Dashboard content might be incomplete")
            elif response.status_code == 302:
                print("❓ Dashboard is redirecting - checking redirect location")
                print(f"Location header: {response.headers.get('Location')}")
            else:
                print(f"❓ Unexpected status code: {response.status_code}")
                
    # Cleanup
    import shutil
    shutil.rmtree(test_dir)
            
except Exception as e:
    print(f"❌ Test failed with error: {e}")
    import traceback
    traceback.print_exc()
