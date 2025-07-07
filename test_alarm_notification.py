"""
Test script for alarm notification functionality
This script sends a test notification with sound to verify the full notification flow
"""

import os
import sys
import json
import time
from datetime import datetime

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import app modules
from app import app, dm
from push_service import send_push_notification

def test_notification_with_sound(user_email, sound_file="alert.mp3"):
    """Send a test notification with sound to the specified user"""
    
    print(f"Sending test notification to {user_email} with sound {sound_file}")
    
    # Create test notification data
    notification_data = {
        "type": "test",
        "timestamp": datetime.now().isoformat(),
        "sound": sound_file,
        "url": "/dashboard"
    }
    
    # Send the notification
    result = send_push_notification(
        user_email=user_email,
        title="🔊 Test Notification",
        body=f"Dette er en test av lydvarsling ({sound_file})",
        data=notification_data,
        dm=dm
    )
    
    if result:
        print("✅ Notification sent successfully!")
        return True
    else:
        print("❌ Failed to send notification")
        return False

def check_user_subscriptions(user_email):
    """Check if the user has any push subscriptions"""
    subscriptions_data = dm.load_data('push_subscriptions')
    user_subscriptions = subscriptions_data.get(user_email, [])
    
    if not user_subscriptions:
        print(f"⚠️ No push subscriptions found for {user_email}")
        return False
    
    print(f"Found {len(user_subscriptions)} push subscriptions for {user_email}")
    
    # Print subscription details
    for i, sub in enumerate(user_subscriptions):
        print(f"\nSubscription #{i+1}:")
        print(f"  Endpoint: {sub.get('endpoint', 'N/A')[:60]}...")
        print(f"  Created: {sub.get('subscribed_at', 'N/A')}")
    
    return True

def check_sound_files():
    """Check if sound files exist"""
    sound_files = ['pristine.mp3', 'ding.mp3', 'chime.mp3', 'alert.mp3']
    sound_dir = os.path.join(os.path.dirname(__file__), 'static', 'sounds')
    
    print("\nChecking sound files:")
    missing = []
    
    for sound in sound_files:
        path = os.path.join(sound_dir, sound)
        if os.path.exists(path):
            print(f"✅ {sound} exists")
            # Check file size
            size = os.path.getsize(path)
            print(f"   Size: {size} bytes")
        else:
            print(f"❌ {sound} is missing")
            missing.append(sound)
    
    return len(missing) == 0

def check_service_worker():
    """Check if service worker file exists and contains sound handling code"""
    sw_path = os.path.join(os.path.dirname(__file__), 'static', 'sw.js')
    
    print("\nChecking service worker:")
    if not os.path.exists(sw_path):
        print("❌ Service worker file not found")
        return False
    
    with open(sw_path, 'r') as f:
        sw_code = f.read()
    
    # Check for key sound-related code
    checks = [
        ("Sound event listener", "addEventListener('message'" in sw_code),
        ("PLAY_NOTIFICATION_SOUND handling", "PLAY_NOTIFICATION_SOUND" in sw_code),
        ("Sound data extraction", "data.sound" in sw_code)
    ]
    
    all_passed = True
    for name, result in checks:
        if result:
            print(f"✅ {name}: Found")
        else:
            print(f"❌ {name}: Missing")
            all_passed = False
    
    return all_passed

def check_app_js():
    """Check if app.js contains sound handling code"""
    app_js_path = os.path.join(os.path.dirname(__file__), 'static', 'js', 'app.js')
    
    print("\nChecking app.js:")
    if not os.path.exists(app_js_path):
        print("❌ app.js file not found")
        return False
    
    with open(app_js_path, 'r') as f:
        app_js_code = f.read()
    
    # Check for key sound-related code
    checks = [
        ("playNotificationSound function", "playNotificationSound" in app_js_code),
        ("Service worker message listener", "addEventListener('message'" in app_js_code),
        ("Audio play implementation", "new Audio" in app_js_code)
    ]
    
    all_passed = True
    for name, result in checks:
        if result:
            print(f"✅ {name}: Found")
        else:
            print(f"❌ {name}: Missing")
            all_passed = False
    
    return all_passed

def run_full_test(user_email):
    """Run a full test of the notification sound system"""
    print("=" * 60)
    print("ALARM NOTIFICATION SYSTEM TEST")
    print("=" * 60)
    
    # Check sound files
    sounds_ok = check_sound_files()
    
    # Check service worker
    sw_ok = check_service_worker()
    
    # Check app.js
    app_js_ok = check_app_js()
    
    # Check user subscriptions
    subscriptions_ok = check_user_subscriptions(user_email)
    
    # Print test summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Sound files: {'✅ OK' if sounds_ok else '❌ Issues found'}")
    print(f"Service worker: {'✅ OK' if sw_ok else '❌ Issues found'}")
    print(f"App.js: {'✅ OK' if app_js_ok else '❌ Issues found'}")
    print(f"User subscriptions: {'✅ OK' if subscriptions_ok else '❌ No subscriptions'}")
    
    if not subscriptions_ok:
        print("\n⚠️ Cannot send test notification: No subscriptions found")
        print("Please make sure the user has enabled notifications in their browser")
        return
    
    # If all checks pass, send test notification
    if sounds_ok and sw_ok and app_js_ok and subscriptions_ok:
        print("\nAll checks passed! Sending test notification...")
        
        # Send tests with different sounds
        for sound in ['alert.mp3', 'ding.mp3', 'chime.mp3', 'pristine.mp3']:
            print(f"\nTesting with sound: {sound}")
            success = test_notification_with_sound(user_email, sound)
            
            if success:
                print("✅ Test notification sent")
            else:
                print("❌ Test notification failed")
            
            # Wait between notifications
            if sound != 'pristine.mp3':  # Don't wait after the last one
                print("Waiting 3 seconds before next test...")
                time.sleep(3)
        
        print("\nAll test notifications sent!")
        print("\nPlease check your device to see if you received the notifications with sound")
        print("Remember that on mobile, the browser or app must be open for the service worker to be active")
    else:
        print("\n⚠️ Some checks failed. Please fix the issues before testing notifications.")

if __name__ == "__main__":
    # Get user email from command line argument or use default
    if len(sys.argv) > 1:
        user_email = sys.argv[1]
    else:
        # Try to get the first user from the data
        users = dm.load_data('users')
        if users:
            user_email = list(users.keys())[0]
        else:
            user_email = "user@example.com"
    
    run_full_test(user_email)
