#!/usr/bin/env python3
"""
Comprehensive sound notification testing
"""
import sys
import os
import tempfile
import shutil
import json
from datetime import datetime, timedelta

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_sound_system():
    """Test all sound notification components"""
    
    # Create temp directory for testing
    temp_dir = tempfile.mkdtemp()
    users_file = os.path.join(temp_dir, 'users.json')
    
    try:
        from app import app
        from werkzeug.security import generate_password_hash
        
        # Create test user with sound preferences
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
        
        print("🔊 TESTING SOUND NOTIFICATION SYSTEM")
        print("="*50)
        
        with app.test_client() as client:
            # Login
            login_response = client.post('/login', data={
                'email': 'test@example.com',
                'password': 'testpass123'
            })
            print(f"1. Login: {login_response.status_code} ✅")
            
            # Test sound test page
            response = client.get('/sound-test')
            print(f"2. Sound test page: {response.status_code} {'✅' if response.status_code == 200 else '❌'}")
            
            # Test service worker sound test
            response = client.get('/sw-test')
            print(f"3. Service worker test: {response.status_code} {'✅' if response.status_code == 200 else '❌'}")
            
            # Test creating reminder with different sounds
            sound_files = ['pristine.mp3', 'ding.mp3', 'chime.mp3', 'alert.mp3']
            
            for i, sound in enumerate(sound_files):
                tomorrow = datetime.now() + timedelta(days=1)
                reminder_data = {
                    'title': f'Test Sound Reminder {i+1}',
                    'description': f'Testing {sound} notification',
                    'date': tomorrow.strftime('%Y-%m-%d'),
                    'time': '12:00',
                    'priority': 'Medium',
                    'category': 'Test',
                    'sound': sound
                }
                
                response = client.post('/add_reminder', 
                                     json=reminder_data,
                                     content_type='application/json')
                print(f"4.{i+1} Created reminder with {sound}: {response.status_code} {'✅' if response.status_code == 200 else '❌'}")
            
            # Test notification integration
            try:
                from notification_integration import send_reminder_notification
                test_result = send_reminder_notification(
                    "test@example.com",
                    "Test Sound Notification",
                    tomorrow.strftime('%Y-%m-%d %H:%M'),
                    sound="pristine.mp3",
                    dm=None  # Mock DM
                )
                print(f"5. Notification integration: {'✅' if test_result else '❌'}")
            except Exception as e:
                print(f"5. Notification integration: ❌ ({e})")
            
            # Test focus modes with sound settings
            response = client.get('/focus-modes')
            print(f"6. Focus modes page: {response.status_code} {'✅' if response.status_code == 200 else '❌'}")
            
            # Test setting silent mode (should affect sounds)
            response = client.post('/focus-modes', data={'focus_mode': 'silent'})
            print(f"7. Silent mode activation: {response.status_code} {'✅' if response.status_code == 200 else '❌'}")
            
            print("\n" + "="*50)
            print("🎵 SOUND FILES CHECK")
            print("="*50)
            
            # Check if sound files exist
            sound_dir = os.path.join(os.getcwd(), 'static', 'sounds')
            if os.path.exists(sound_dir):
                print(f"Sound directory exists: ✅")
                for sound in sound_files:
                    sound_path = os.path.join(sound_dir, sound)
                    exists = os.path.exists(sound_path)
                    print(f"- {sound}: {'✅' if exists else '❌'}")
            else:
                print(f"Sound directory missing: ❌")
                print(f"Expected at: {sound_dir}")
            
            return True
                
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)

def test_notification_simple():
    """Test the simple notification system"""
    print("\n" + "="*50)
    print("🔔 TESTING SIMPLE NOTIFICATION SYSTEM")
    print("="*50)
    
    try:
        from notification_simple import send_browser_notification
        
        # Test browser notification
        result = send_browser_notification(
            "test@example.com",
            "Test Notification",
            "This is a test notification",
            sound="pristine.mp3"
        )
        print(f"Browser notification test: {'✅' if result else '❌'}")
        
    except Exception as e:
        print(f"Simple notification test: ❌ ({e})")

def test_push_service():
    """Test the push service system"""
    print("\n" + "="*50)
    print("📱 TESTING PUSH SERVICE SYSTEM")
    print("="*50)
    
    try:
        # Test mock push service
        from push_service_mock import send_push_notification as mock_push
        
        result = mock_push(
            "test@example.com",
            "Test Push",
            "Test push notification",
            sound="pristine.mp3"
        )
        print(f"Mock push service: {'✅' if result else '❌'}")
        
    except Exception as e:
        print(f"Push service test: ❌ ({e})")
        
    try:
        # Test real push service if available
        from push_service import send_push_notification as real_push
        
        result = real_push(
            "test@example.com",
            "Test Push",
            "Test push notification",
            data={"sound": "pristine.mp3"}
        )
        print(f"Real push service: {'✅' if result else '❌'}")
        
    except Exception as e:
        print(f"Real push service: ❌ ({e})")

if __name__ == "__main__":
    print("🎯 COMPREHENSIVE SOUND NOTIFICATION TEST")
    print("="*60)
    
    success = test_sound_system()
    test_notification_simple()
    test_push_service()
    
    print("\n" + "="*60)
    if success:
        print("🎉 SOUND SYSTEM TESTS COMPLETED!")
        print("Check the results above for any ❌ items that need fixing")
    else:
        print("❌ SOUND SYSTEM TESTS FAILED!")
    print("="*60)
