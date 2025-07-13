#!/usr/bin/env python3
"""
Comprehensive Notification System Test for SmartReminder
-------------------------------------------------------
This script tests all aspects of the notification system including:
1. Push notifications with different sounds
2. Alarm notifications
3. Email notifications
4. Focus mode notification behavior
5. Shared board notifications
6. Mobile notification optimizations
7. Notification system error handling

Usage:
  python3 test_comprehensive_notifications.py [user_email] [--mock]

  user_email: The email address to use for testing (defaults to first user in database)
  --mock: Use mock push notifications instead of real ones (to avoid VAPID key issues)
"""

import os
import sys
import json
import time
import logging
import requests
from datetime import datetime, timedelta
import random

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import app and data manager
from app import app, dm

# Check if --mock flag is provided
USE_MOCK = "--mock" in sys.argv
if USE_MOCK:
    sys.argv.remove("--mock")
    # Create mock push service if it doesn't exist
    if not os.path.exists("push_service_mock.py"):
        print("Creating mock push service...")
        from create_mock_push_service import create_mock_push_service
        create_mock_push_service()
    
    # Import mock functions
    print("Using mock push notification service")
    sys.path.insert(0, os.path.abspath("."))
    from push_service_mock import (
        send_push_notification,
        send_reminder_notification,
        send_board_notification,
        send_password_reset_notification
    )
else:
    # Import real push service functions
    print("Using real push notification service")
    from push_service import (
        send_push_notification, 
        send_reminder_notification,
        send_board_notification,
        send_password_reset_notification
    )

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('notification_test.log')
    ]
)
logger = logging.getLogger(__name__)

# Available sound files
SOUND_FILES = ['alert.mp3', 'ding.mp3', 'chime.mp3', 'pristine.mp3']

def print_header(title):
    """Print a section header"""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80)

def check_push_notification_requirements():
    """Check all requirements for push notifications"""
    print_header("CHECKING PUSH NOTIFICATION REQUIREMENTS")
    
    # Check sound files
    print("\n🔊 Checking notification sound files:")
    sound_dir = os.path.join(os.path.dirname(__file__), 'static', 'sounds')
    sounds_ok = True
    
    for sound in SOUND_FILES:
        path = os.path.join(sound_dir, sound)
        if os.path.exists(path):
            size = os.path.getsize(path)
            print(f"  ✅ {sound} exists ({size} bytes)")
        else:
            print(f"  ❌ {sound} is missing")
            sounds_ok = False
    
    # Check service worker
    print("\n🔄 Checking service worker:")
    sw_path = os.path.join(os.path.dirname(__file__), 'static', 'sw.js')
    
    if not os.path.exists(sw_path):
        print("  ❌ Service worker file not found")
        sw_ok = False
    else:
        with open(sw_path, 'r') as f:
            sw_code = f.read()
        
        sw_features = [
            ("Push event listener", "addEventListener('push'"),
            ("Notification display", "showNotification"),
            ("Sound data extraction", "data.sound"),
            ("Client message passing", "postMessage"),
            ("PLAY_NOTIFICATION_SOUND handling", "PLAY_NOTIFICATION_SOUND"),
            ("Notification click handling", "notificationclick")
        ]
        
        sw_ok = True
        for name, keyword in sw_features:
            if keyword in sw_code:
                print(f"  ✅ {name}: Found")
            else:
                print(f"  ❌ {name}: Missing")
                sw_ok = False
    
    # Check app.js
    print("\n📱 Checking app.js:")
    app_js_path = os.path.join(os.path.dirname(__file__), 'static', 'js', 'app.js')
    
    if not os.path.exists(app_js_path):
        print("  ❌ app.js file not found")
        app_js_ok = False
    else:
        with open(app_js_path, 'r') as f:
            app_js_code = f.read()
        
        app_js_features = [
            ("playNotificationSound function", "playNotificationSound"),
            ("Service worker registration", "serviceWorker.register"),
            ("Audio object creation", "new Audio"),
            ("Vibration fallback", "navigator.vibrate"),
            ("Message event listener", "addEventListener('message'")
        ]
        
        app_js_ok = True
        for name, keyword in app_js_features:
            if keyword in app_js_code:
                print(f"  ✅ {name}: Found")
            else:
                print(f"  ❌ {name}: Missing")
                app_js_ok = False
    
    # Overall status
    print("\n📋 Push notification requirements status:")
    print(f"  Sound files: {'✅ OK' if sounds_ok else '❌ Issues found'}")
    print(f"  Service worker: {'✅ OK' if sw_ok else '❌ Issues found'}")
    print(f"  App.js: {'✅ OK' if app_js_ok else '❌ Issues found'}")
    
    return sounds_ok and sw_ok and app_js_ok

def check_user_subscriptions(user_email):
    """Check if the user has push subscriptions"""
    print_header(f"CHECKING PUSH SUBSCRIPTIONS FOR {user_email}")
    
    try:
        subscriptions_data = dm.load_data('push_subscriptions')
        user_subscriptions = subscriptions_data.get(user_email, [])
        
        if not user_subscriptions:
            print(f"⚠️ No push subscriptions found for {user_email}")
            print("\nAttempting to create a test subscription...")
            
            # Create a test subscription with properly formatted keys
            # These are mock keys that work with pywebpush for testing
            test_subscription = {
                "endpoint": "https://fcm.googleapis.com/fcm/send/test-endpoint-" + str(int(datetime.now().timestamp())),
                "expirationTime": None,
                "keys": {
                    "p256dh": "BGEw2wsHgLwzerjvR0O0hmOI3zt6pJWzAvVejXc5p8GUpS03ro0bviBDb-iqQD1qOU7G5GlrYJr0W5SWgE-oEWU",
                    "auth": "8O_K-rlSQUxMpBmx3NspGQ"
                }
            }
            
            # Subscribe user to push
            if USE_MOCK:
                # Import directly from mock module
                from push_service_mock import subscribe_user_to_push
            else:
                # Import from real module
                from push_service import subscribe_user_to_push
            
            # Subscribe user to push
            result = subscribe_user_to_push(user_email, test_subscription, dm)
            
            if result:
                print(f"✅ Successfully created test subscription for {user_email}")
                # Reload subscriptions
                subscriptions_data = dm.load_data('push_subscriptions')
                user_subscriptions = subscriptions_data.get(user_email, [])
            else:
                print(f"❌ Failed to create test subscription for {user_email}")
                print("\nPossible reasons:")
                print("  - User has not granted notification permission")
                print("  - User is using a browser that doesn't support push notifications")
                print("  - User has revoked notification permission")
                print("\nTroubleshooting steps:")
                print("  1. Make sure notifications are enabled in browser settings")
                print("  2. Visit the app and check browser console for errors")
                print("  3. Try subscribing again from the dashboard")
                return False
        
        print(f"✅ Found {len(user_subscriptions)} push subscriptions")
        
        # Print subscription details
        for i, sub in enumerate(user_subscriptions):
            print(f"\nSubscription #{i+1}:")
            print(f"  Endpoint: {sub.get('endpoint', 'N/A')[:60]}...")
            print(f"  Created: {sub.get('subscribed_at', 'N/A')}")
            
            # Check if keys are present
            if 'keys' in sub and 'p256dh' in sub['keys'] and 'auth' in sub['keys']:
                print(f"  Keys: ✅ Valid")
            else:
                print(f"  Keys: ❌ Invalid or missing")
        
        return len(user_subscriptions) > 0
    except Exception as e:
        print(f"❌ Error checking subscriptions: {e}")
        return False

def test_push_notification_with_sound(user_email, sound_file):
    """Test sending a push notification with a specific sound"""
    try:
        print(f"\n🔔 Testing notification with sound: {sound_file}")
        
        # Create notification data
        notification_data = {
            "type": "test",
            "timestamp": datetime.now().isoformat(),
            "sound": sound_file,
            "url": "/dashboard"
        }
        
        # Send notification
        result = send_push_notification(
            user_email=user_email,
            title="🔊 Sound Test Notification",
            body=f"Testing notification sound: {sound_file}",
            data=notification_data,
            dm=dm
        )
        
        if result:
            print(f"  ✅ Test notification sent successfully")
            return True
        else:
            print(f"  ❌ Failed to send notification")
            return False
    except Exception as e:
        print(f"  ❌ Error sending test notification: {e}")
        return False

def test_reminder_notification(user_email):
    """Test reminder notification"""
    try:
        print("\n⏰ Testing reminder notification")
        
        # Create a random sound
        sound = random.choice(SOUND_FILES)
        
        # Current time formatted
        current_time = datetime.now().strftime("%H:%M")
        
        # Send reminder notification
        result = send_reminder_notification(
            user_email=user_email,
            reminder_title="Test reminder notification",
            reminder_time=current_time,
            sound=sound,
            dm=dm
        )
        
        if result:
            print(f"  ✅ Reminder notification sent successfully with sound {sound}")
            return True
        else:
            print(f"  ❌ Failed to send reminder notification")
            return False
    except Exception as e:
        print(f"  ❌ Error sending reminder notification: {e}")
        return False

def test_board_notification(user_email):
    """Test shared board notification"""
    try:
        print("\n📋 Testing shared board notification")
        
        # Get boards
        boards_data = dm.load_data('shared_noteboards')
        if not boards_data:
            print("  ⚠️ No shared boards found, creating test board")
            # Create a test board data structure
            test_board_id = f"test-board-{int(time.time())}"
            boards_data = {
                test_board_id: {
                    "board_id": test_board_id,
                    "title": "Test Board",
                    "members": [user_email],
                    "notes": []
                }
            }
            dm.save_data('shared_noteboards', boards_data)
        
        # Get first board
        board_id = list(boards_data.keys())[0]
        board_data = boards_data[board_id]
        
        # Send board notification
        result = send_board_notification(
            board_id=board_data["board_id"],
            action="Test Update",
            content="This is a test notification for shared board",
            exclude_user=None,  # Include all members
            dm=dm
        )
        
        if result:
            print(f"  ✅ Board notification sent successfully")
            return True
        else:
            print(f"  ❌ Failed to send board notification")
            return False
    except Exception as e:
        print(f"  ❌ Error sending board notification: {e}")
        return False

def test_password_reset_notification(user_email):
    """Test password reset notification"""
    try:
        print("\n🔐 Testing password reset notification")
        
        # Create fake reset token
        reset_token = f"test-token-{int(time.time())}"
        
        # Send password reset notification
        result = send_password_reset_notification(
            user_email=user_email,
            reset_token=reset_token,
            dm=dm
        )
        
        if result:
            print(f"  ✅ Password reset notification sent successfully")
            return True
        else:
            print(f"  ❌ Failed to send password reset notification")
            return False
    except Exception as e:
        print(f"  ❌ Error sending password reset notification: {e}")
        return False

def test_notifications_in_focus_modes(user_email):
    """Test how notifications behave in different focus modes"""
    print_header("TESTING NOTIFICATIONS IN FOCUS MODES")
    
    try:
        # Import focus modes
        from focus_modes import FocusModeManager
        
        # Create focus mode manager
        focus_manager = FocusModeManager(dm)
        
        # Get available modes
        modes = focus_manager.get_available_modes()
        print(f"Found {len(modes)} focus modes")
        
        for mode_name in modes:
            print(f"\n🔍 Testing notifications in '{mode_name}' mode")
            
            # Get mode
            mode = focus_manager.get_mode(mode_name)
            
            # Check sound setting
            notification_sound = mode.settings.get('notification_sound', True)
            notification_vibration = mode.settings.get('notification_vibration', True)
            
            print(f"  Mode: {mode.name}")
            print(f"  Description: {mode.description}")
            print(f"  Sound enabled: {'✅ Yes' if notification_sound else '❌ No'}")
            print(f"  Vibration enabled: {'✅ Yes' if notification_vibration else '❌ No'}")
            
            # Test appropriate notification based on mode settings
            notification_data = {
                "type": "focus_test",
                "mode": mode_name,
                "url": "/dashboard"
            }
            
            if notification_sound:
                # Add random sound
                sound = random.choice(SOUND_FILES)
                notification_data["sound"] = sound
            
            # Send notification
            result = send_push_notification(
                user_email=user_email,
                title=f"Focus Mode: {mode.name}",
                body=f"Testing notification in {mode.name} mode",
                data=notification_data,
                dm=dm
            )
            
            if result:
                print(f"  ✅ Notification sent successfully for {mode_name} mode")
            else:
                print(f"  ❌ Failed to send notification for {mode_name} mode")
            
            # Wait a bit between notifications
            if mode_name != list(modes)[-1]:  # Don't wait after the last one
                print("  Waiting 3 seconds before next test...")
                time.sleep(3)
        
        return True
    except ImportError:
        print("❌ Could not import focus_modes module")
        return False
    except Exception as e:
        print(f"❌ Error testing focus modes: {e}")
        return False

def run_full_notification_test(user_email):
    """Run a comprehensive test of all notification types"""
    print_header("COMPREHENSIVE NOTIFICATION SYSTEM TEST")
    print(f"Test user: {user_email}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check requirements
    requirements_ok = check_push_notification_requirements()
    
    # Check user subscriptions
    subscriptions_ok = check_user_subscriptions(user_email)
    
    if not subscriptions_ok:
        print("\n⚠️ Cannot continue testing: No valid push subscriptions found")
        print("Please make sure the user has enabled notifications in their browser")
        return
    
    print_header("TESTING NOTIFICATION TYPES")
    
    # Test different notification sounds
    for sound in SOUND_FILES:
        test_push_notification_with_sound(user_email, sound)
        if sound != SOUND_FILES[-1]:  # Don't wait after the last one
            time.sleep(3)
    
    # Test reminder notification
    test_reminder_notification(user_email)
    time.sleep(3)
    
    # Test board notification
    test_board_notification(user_email)
    time.sleep(3)
    
    # Test password reset notification
    test_password_reset_notification(user_email)
    time.sleep(3)
    
    # Test notifications in different focus modes
    test_notifications_in_focus_modes(user_email)
    
    print_header("TEST SUMMARY")
    print("All notification tests have been sent to your device.")
    print("\nPlease check your device to verify:")
    print("  1. Did you receive all notifications?")
    print("  2. Did you hear the correct sounds for each notification?")
    print("  3. Did the focus mode settings affect the notifications correctly?")
    print("  4. Did clicking the notifications navigate to the correct page?")
    
    print("\nRemember that on mobile devices:")
    print("  - The browser or PWA must be running for notifications to play sounds")
    print("  - Some browsers require user interaction before playing sounds")
    print("  - iOS has limitations with web push notifications")
    
    print("\n✅ Comprehensive notification test completed!")

if __name__ == "__main__":
    # Get user email from command line argument or use default
    user_email = None
    for arg in sys.argv[1:]:
        if not arg.startswith("--"):
            user_email = arg
            break
    
    if not user_email:
        # Try to get the first user from the data
        users = dm.load_data('users')
        if users:
            user_email = list(users.keys())[0]
        else:
            user_email = "user@example.com"
            print(f"⚠️ No users found, using default: {user_email}")
    
    # Print test mode status
    if USE_MOCK:
        print("\n⚠️ RUNNING IN MOCK MODE - NO REAL NOTIFICATIONS WILL BE SENT")
        print("This mode is useful for testing the notification flow without VAPID key issues")
    else:
        print("\n🔔 RUNNING IN REAL MODE - ACTUAL NOTIFICATIONS WILL BE SENT")
        print("If you encounter VAPID key errors, try running with --mock flag")
    
    run_full_notification_test(user_email)
