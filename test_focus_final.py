#!/usr/bin/env python3
"""
Test focus modes with authentication
"""
import sys
import os
import tempfile
import shutil
import json

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_focus_with_auth():
    """Test focus modes with proper authentication"""
    
    # Create temp directory for testing
    temp_dir = tempfile.mkdtemp()
    users_file = os.path.join(temp_dir, 'users.json')
    
    try:
        from app import app
        from werkzeug.security import generate_password_hash
        
        # Create test user data
        test_users = {
            "test@example.com": {
                "email": "test@example.com",
                "password": generate_password_hash("testpass123"),
                "focus_mode": "normal",
                "reminders": []
            }
        }
        
        with open(users_file, 'w') as f:
            json.dump(test_users, f, indent=2)
        
        # Configure app for testing
        app.config.update({
            'TESTING': True,
            'SECRET_KEY': 'test-secret-key',
            'WTF_CSRF_ENABLED': False,
            'DATA_DIR': temp_dir
        })
        
        with app.test_client() as client:
            # Login first
            login_response = client.post('/login', data={
                'email': 'test@example.com',
                'password': 'testpass123'
            })
            print(f"Login status: {login_response.status_code}")
            
            if login_response.status_code in [200, 302]:
                # Test focus modes GET request
                response = client.get('/focus-modes', follow_redirects=True)
                print(f"Focus modes status: {response.status_code}")
                
                if response.status_code == 200:
                    print("✅ Focus modes template renders successfully!")
                    print("✅ Template syntax is fixed!")
                    return True
                else:
                    print(f"❌ Error rendering focus modes: {response.status_code}")
                    if hasattr(response, 'data'):
                        error_text = response.data.decode()[:1000]
                        print(f"Error details: {error_text}")
                    return False
            else:
                print(f"❌ Login failed: {login_response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    success = test_focus_with_auth()
    if success:
        print("\n🎉 All focus modes tests passed!")
    else:
        print("\n❌ Tests failed!")
