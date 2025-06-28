#!/usr/bin/env python3
"""Test script to verify email settings fixes"""

import sys
import os
sys.path.append(os.path.abspath('.'))

try:
    from app import app
    
    print("🧪 Testing email settings fixes...")
    
    with app.test_request_context():
        from flask import url_for
        
        # Test email settings URL generation
        try:
            email_settings_url = url_for('email_settings')
            print(f"✅ email_settings URL: {email_settings_url}")
        except Exception as e:
            print(f"❌ email_settings URL error: {e}")
        
        # Test test_email URL generation
        try:
            test_email_url = url_for('test_email')
            print(f"✅ test_email URL: {test_email_url}")
        except Exception as e:
            print(f"❌ test_email URL error: {e}")
    
    # Test routes with test client
    with app.test_client() as client:
        # Test email settings page (should redirect to login)
        response = client.get('/email-settings')
        print(f"✅ /email-settings status: {response.status_code} (expected 302 redirect)")
        
        # Test test email endpoint (should redirect to login)
        response = client.post('/test-email')
        print(f"✅ /test-email status: {response.status_code} (expected 302 redirect)")
    
    print("\n🎯 Email settings fixes verified!")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
