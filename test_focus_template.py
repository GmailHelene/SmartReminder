#!/usr/bin/env python3
"""
Test focus modes template rendering
"""
import sys
import os
import tempfile
import shutil
import json

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_focus_template():
    """Test focus modes template rendering"""
    
    # Create temp directory for testing
    temp_dir = tempfile.mkdtemp()
    users_file = os.path.join(temp_dir, 'users.json')
    
    # Create test user data
    test_users = {
        "test@example.com": {
            "email": "test@example.com",
            "password": "hashed_password_here",
            "focus_mode": "normal",
            "reminders": []
        }
    }
    
    with open(users_file, 'w') as f:
        json.dump(test_users, f)
    
    try:
        from app import app
        from werkzeug.security import generate_password_hash
        
        # Configure app for testing
        app.config.update({
            'TESTING': True,
            'SECRET_KEY': 'test-secret-key',
            'WTF_CSRF_ENABLED': False,
            'DATA_DIR': temp_dir
        })
        
        with app.test_client() as client:
            # Test focus modes GET request
            response = client.get('/focus-modes')
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Focus modes template renders successfully!")
                return True
            else:
                print(f"❌ Error: {response.status_code}")
                if hasattr(response, 'data'):
                    print(response.data.decode()[:500])
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
    test_focus_template()
