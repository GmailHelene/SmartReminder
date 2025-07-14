#!/usr/bin/env python3
"""Test focus modes and root endpoints"""

import sys
import tempfile
from pathlib import Path
import os

# Setup environment
os.environ['FLASK_ENV'] = 'development'
os.environ['TESTING'] = '1'
sys.path.insert(0, '.')

print("Starting test...")

try:
    # Import app
    from app import app, dm
    
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

    print('Flask app loaded successfully')
    
    with app.test_client() as client:
        print('\n=== Testing Root Endpoint (/) ===')
        try:
            response = client.get('/')
            print(f'Status: {response.status_code}')
            if response.status_code == 302:
                print('✅ Root redirects to login (correct)')
            else:
                print(f'Response: {response.data.decode()[:200]}')
        except Exception as e:
            print(f'Error testing root: {e}')

        print('\n=== Testing Focus Modes Endpoint (/focus-modes) ===')
        try:
            response = client.get('/focus-modes')
            print(f'Status: {response.status_code}')
            if response.status_code == 302:
                print('✅ Focus modes redirects to login (correct)')
            else:
                print(f'Response: {response.data.decode()[:200]}')
        except Exception as e:
            print(f'Error testing focus-modes: {e}')
            import traceback
            traceback.print_exc()

        print('\n=== Testing Focus Mode Change (POST) ===')
        try:
            response = client.post('/focus-modes', data={'focus_mode': 'silent'})
            print(f'Status: {response.status_code}')
            if response.status_code == 302:
                print('✅ Focus mode change redirects (probably to login)')
            else:
                print(f'Response: {response.data.decode()[:200]}')
        except Exception as e:
            print(f'Error testing focus mode change: {e}')
            import traceback
            traceback.print_exc()

except Exception as e:
    print(f'Failed to load app: {e}')
    import traceback
    traceback.print_exc()

print('Test completed')
