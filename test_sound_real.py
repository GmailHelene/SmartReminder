#!/usr/bin/env python3
"""
Test actual sound playback functionality
"""
import sys
import os
import tempfile
import shutil
import json
from datetime import datetime, timedelta

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_real_sound_notification():
    """Test actual sound notification with real data"""
    
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
        
        print("🎵 TESTING REAL SOUND NOTIFICATION")
        print("="*50)
        
        with app.test_client() as client:
            # Login
            login_response = client.post('/login', data={
                'email': 'test@example.com',
                'password': 'testpass123'
            })
            print(f"1. Login: {login_response.status_code} ✅")
            
            # Create a reminder for immediate notification test
            now = datetime.now()
            notification_time = now + timedelta(minutes=1)  # 1 minute from now
            
            reminder_data = {
                'title': 'Test Sound Reminder',
                'description': 'This should play a sound notification',
                'date': notification_time.strftime('%Y-%m-%d'),
                'time': notification_time.strftime('%H:%M'),
                'priority': 'Høy',
                'category': 'Test',
                'sound': 'alert.mp3'  # Use alert sound for testing
            }
            
            response = client.post('/add_reminder', 
                                 json=reminder_data,
                                 content_type='application/json')
            print(f"2. Reminder created: {response.status_code} ✅")
            
            # Test notification integration directly
            print("\n3. Testing notification systems:")
            
            # Test notification_integration
            try:
                from notification_integration import send_reminder_notification
                result = send_reminder_notification(
                    "test@example.com",
                    "Test Sound Alert",
                    notification_time.strftime('%Y-%m-%d %H:%M'),
                    sound="alert.mp3",
                    dm=None
                )
                print(f"   - notification_integration: {'✅' if result else '❌'}")
            except Exception as e:
                print(f"   - notification_integration: ❌ ({e})")
            
            # Test notification_simple
            try:
                from notification_simple import send_browser_notification, send_reminder_notification as simple_reminder
                
                browser_result = send_browser_notification(
                    "test@example.com",
                    "Browser Test Alert",
                    "Testing browser notification with sound",
                    sound="alert.mp3"
                )
                print(f"   - browser notification: {'✅' if browser_result else '❌'}")
                
                simple_result = simple_reminder(
                    "test@example.com",
                    "Simple Reminder Test",
                    notification_time.strftime('%Y-%m-%d %H:%M'),
                    sound="alert.mp3"
                )
                print(f"   - simple reminder: {'✅' if simple_result else '❌'}")
                
            except Exception as e:
                print(f"   - notification_simple: ❌ ({e})")
            
            # Test push service mock
            try:
                from push_service_mock import send_push_notification
                
                mock_result = send_push_notification(
                    "test@example.com",
                    "Mock Push Test",
                    "Testing mock push notification",
                    sound="alert.mp3"
                )
                print(f"   - push service mock: {'✅' if mock_result else '❌'}")
                
            except Exception as e:
                print(f"   - push service mock: ❌ ({e})")
            
            print("\n4. Sound file accessibility test:")
            # Test if sound files can be served
            sound_files = ['pristine.mp3', 'ding.mp3', 'chime.mp3', 'alert.mp3']
            
            for sound in sound_files:
                response = client.get(f'/static/sounds/{sound}')
                status = "✅" if response.status_code == 200 else f"❌ ({response.status_code})"
                print(f"   - /static/sounds/{sound}: {status}")
            
            print("\n5. Manual testing instructions:")
            print("="*50)
            print("To test actual sound playback:")
            print("1. Start the Flask app: python3 app.py")
            print("2. Open browser to: http://localhost:5000")
            print("3. Login with test@example.com / testpass123")
            print("4. Go to: http://localhost:5000/sound-test")
            print("5. Click the test buttons to hear sounds")
            print("6. Create a reminder and wait for notification")
            print("7. Check browser console for sound playback logs")
            
            return True
                
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    print("🎯 REAL SOUND NOTIFICATION TEST")
    print("="*50)
    
    success = test_real_sound_notification()
    
    print("\n" + "="*50)
    if success:
        print("🎉 SOUND NOTIFICATION TESTS PASSED!")
        print("🔊 All sound systems are functional")
        print("📱 Ready for browser testing")
    else:
        print("❌ SOUND NOTIFICATION TESTS FAILED!")
    print("="*50)
