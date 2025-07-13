#!/usr/bin/env python3
"""Test script to check the problematic endpoints"""

import sys
import os
import tempfile
from pathlib import Path

# Setup environment
os.environ['FLASK_ENV'] = 'development'
os.environ['TESTING'] = '1'
sys.path.insert(0, '.')

# Setup temp directory
temp_dir = tempfile.mkdtemp()
print(f'Using temp directory: {temp_dir}')

try:
    # Import and setup
    from app import app, dm
    dm.data_dir = Path(temp_dir)
    dm._ensure_data_files()
    
    # Configure app
    app.config.update({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key'
    })
    
    print('Flask app loaded successfully')
    
    # Test the problematic endpoints
    with app.test_client() as client:
        print('\n=== Testing Problematic Endpoints ===')
        
        print('Testing /robots.txt...')
        try:
            response = client.get('/robots.txt')
            print(f'Status: {response.status_code}')
        except Exception as e:
            print(f'Error: {e}')
        
        print('Testing /favicon.ico...')
        try:
            response = client.get('/favicon.ico')
            print(f'Status: {response.status_code}')
        except Exception as e:
            print(f'Error: {e}')
        
        print('Testing /login...')
        try:
            response = client.get('/login')
            print(f'Status: {response.status_code}')
            if response.status_code != 200:
                print(f'Response data: {response.data.decode()[:500]}')
        except Exception as e:
            print(f'Error: {e}')
            import traceback
            traceback.print_exc()

except Exception as e:
    print(f'Failed to load app: {e}')
    import traceback
    traceback.print_exc()

print('Test completed')
