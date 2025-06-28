#!/usr/bin/env python3
"""Test email-settings endpoint after fixing config issue"""

import os
os.environ['FLASK_ENV'] = 'development'
os.environ['TESTING'] = '1'

try:
    from app import app
    
    app.config.update({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key',
        'MAIL_SUPPRESS_SEND': True
    })
    
    print("🧪 Testing /email-settings endpoint...")
    
    with app.test_client() as client:
        # Test without login (should redirect)
        response = client.get('/email-settings')
        print(f"Without login: {response.status_code} (should redirect to login)")
        
        # Test with login
        # First register/login a test user
        user_data = {
            'username': 'test@example.com',
            'password': 'testpass123'
        }
        
        # Register user
        register_response = client.post('/register', data=user_data)
        print(f"Register: {register_response.status_code}")
        
        # Login
        login_response = client.post('/login', data=user_data)
        print(f"Login: {login_response.status_code}")
        
        # Now test email-settings
        response = client.get('/email-settings')
        print(f"Email settings page: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Email settings page loads successfully!")
            # Check if config values are accessible in template
            content = response.get_data(as_text=True)
            if 'MAIL_SERVER' in content or 'Ikke konfigurert' in content:
                print("✅ Config variables are accessible in template!")
            else:
                print("❌ Config variables may not be properly accessible")
        else:
            print(f"❌ Email settings failed with status {response.status_code}")
            print("Response:", response.get_data(as_text=True)[:500])
            
except Exception as e:
    print(f"❌ Error during test: {e}")
    import traceback
    traceback.print_exc()
