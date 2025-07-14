#!/usr/bin/env python3
"""Test VAPID endpoint fix"""

import sys
import tempfile
from pathlib import Path

# Setup environment
sys.path.insert(0, '.')
temp_dir = tempfile.mkdtemp()

try:
    from app import app, dm
    dm.data_dir = Path(temp_dir)
    dm._ensure_data_files()

    app.config.update({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key'
    })

    with app.test_client() as client:
        print('🔍 Testing VAPID endpoint...')
        response = client.get('/api/vapid-public-key')
        print(f'Status: {response.status_code}')
        
        if response.status_code == 200:
            data = response.get_json()
            print(f'✅ VAPID endpoint working: {data}')
        else:
            print(f'❌ VAPID endpoint failed: {response.data.decode()[:200]}')

        print('\n🔍 Testing focus-modes page...')
        response = client.get('/focus-modes')
        print(f'Status: {response.status_code}')
        
        if response.status_code == 302:  # Redirect to login
            print('✅ Focus modes page redirects to login (correct for unauthenticated user)')
        elif response.status_code == 200:
            print('✅ Focus modes page loads successfully')
        else:
            print(f'❌ Focus modes page failed: {response.data.decode()[:200]}')

except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()

print('Test completed')
