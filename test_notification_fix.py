#!/usr/bin/env python3
"""
Quick Test for Notification System
Tests if the basic notification functionality is working with the new fixes
"""

import os
import sys
import json
import time
from datetime import datetime

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
    from push_service_mock import send_push_notification, subscribe_user_to_push
else:
    # Import real push service functions
    print("Using real push notification service")
    from push_service import send_push_notification, subscribe_user_to_push

def test_notification_fix():
    """Test the fixed notification system"""
    print("=" * 60)
    print("NOTIFICATION FIX TEST")
    print("=" * 60)
    
    # Get the first user or use default
    users = dm.load_data('users')
    if users:
        user_email = list(users.keys())[0]
    else:
        user_email = "test-user-123"
    
    print(f"Testing with user: {user_email}")
    
    # Create test subscription
    subscriptions_data = dm.load_data('push_subscriptions')
    user_subscriptions = subscriptions_data.get(user_email, [])
    
    if not user_subscriptions:
        print("Creating a test subscription...")
        test_subscription = {
            "endpoint": "https://fcm.googleapis.com/fcm/send/test-endpoint-" + str(int(datetime.now().timestamp())),
            "expirationTime": None,
            "keys": {
                "p256dh": "BPK-0FY2VgqSYagYl25a16lxCINyJSvi-Qjkt8x0ueYMX6fj0mwY-PPp9eQjSNulrnyIB9ypXZFfO6t5Gdr3ej",
                "auth": "fmmV4Gh2u68qWbbt8hg-_A"
            }
        }
        
        # Subscribe user to push
        result = subscribe_user_to_push(user_email, test_subscription, dm)
        
        if result:
            print("✅ Successfully created test subscription")
        else:
            print("❌ Failed to create test subscription")
            return
    
    # Test simple notification with sound
    print("\nSending test notification with sound...")
    notification_data = {
        "type": "test",
        "timestamp": datetime.now().isoformat(),
        "sound": "pristine.mp3",
        "url": "/dashboard"
    }
    
    # Send notification
    result = send_push_notification(
        user_email=user_email,
        title="🔔 Fix Test Notification",
        body="Testing if notification fix works",
        data=notification_data,
        dm=dm
    )
    
    if result:
        print("✅ Test notification sent successfully!")
    else:
        print("❌ Failed to send notification")
    
    print("\nTest completed!")

if __name__ == "__main__":
    # Print test mode status
    if USE_MOCK:
        print("\n⚠️ RUNNING IN MOCK MODE - NO REAL NOTIFICATIONS WILL BE SENT")
        print("This mode is useful for testing the notification flow without VAPID key issues")
    else:
        print("\n🔔 RUNNING IN REAL MODE - ACTUAL NOTIFICATIONS WILL BE SENT")
        print("If you encounter VAPID key errors, try running with --mock flag")
    
    test_notification_fix()
