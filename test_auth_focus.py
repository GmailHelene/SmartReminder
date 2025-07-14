#!/usr/bin/env python3
"""Test focus modes with authentication"""

import sys
import tempfile
from pathlib import Path
import os

# Setup environment
os.environ['FLASK_ENV'] = 'development'
os.environ['TESTING'] = '1'
sys.path.insert(0, '.')

print("Testing with authentication...")

try:
    from app import app, dm
    from werkzeug.security import generate_password_hash
    
    # Setup temp directory
    temp_dir = tempfile.mkdtemp()
    print(f'Using temp directory: {temp_dir}')
    dm.data_dir = Path(temp_dir)
    dm._ensure_data_files()

    app.config.update({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key'
    })

    # Create a test user
    users = dm.load_data('users')
    user_id = 'test-user-123'
    users[user_id] = {
        'username': 'test@example.com',
        'email': 'test@example.com',
        'password_hash': generate_password_hash('testpass'),
        'focus_mode': 'normal',
        'created': '2025-07-14T10:00:00'
    }
    dm.save_data('users', users)
    print('Test user created')

    with app.test_client() as client:
        # Login the test user
        print('\n=== Logging in test user ===')
        response = client.post('/login', data={
            'username': 'test@example.com',
            'password': 'testpass'
        })
        print(f'Login status: {response.status_code}')
        
        # Test focus modes page with authentication
        print('\n=== Testing Focus Modes Page (authenticated) ===')
        response = client.get('/focus-modes')
        print(f'Status: {response.status_code}')
        
        if response.status_code == 200:
            print('✅ Focus modes page loads successfully')
            content = response.data.decode()
            if 'normal' in content.lower() and 'silent' in content.lower():
                print('✅ Focus modes content looks correct')
            else:
                print('⚠️ Focus modes content may be incomplete')
        elif response.status_code == 302:
            print('⚠️ Still redirecting - login may have failed')
        else:
            print(f'❌ Unexpected status: {response.data.decode()[:200]}')

        # Test changing focus mode
        print('\n=== Testing Focus Mode Change ===')
        response = client.post('/focus-modes', data={'focus_mode': 'silent'})
        print(f'Status: {response.status_code}')
        
        if response.status_code == 302:
            print('✅ Focus mode change redirects (probably back to focus-modes)')
            
            # Check if the change was saved
            users_after = dm.load_data('users')
            user_after = users_after.get(user_id, {})
            new_focus_mode = user_after.get('focus_mode')
            print(f'Focus mode after change: {new_focus_mode}')
            
            if new_focus_mode == 'silent':
                print('✅ Focus mode successfully changed to silent')
            else:
                print(f'❌ Focus mode not changed, still: {new_focus_mode}')
        else:
            print(f'❌ Unexpected response: {response.data.decode()[:200]}')

except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()

print('Authentication test completed')
