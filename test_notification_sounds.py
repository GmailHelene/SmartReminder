#!/usr/bin/env python3
"""
Test script for sending notifications with different sounds.
This is useful for testing how notification sounds work on different devices.

Usage:
  python3 test_notification_sounds.py [email] [sound]

  email: The email address to send the notification to (defaults to admin@example.com)
  sound: The sound to play (alert, ding, chime, pristine - defaults to all sounds in sequence)
"""

import sys
import time
import json
import requests
from datetime import datetime, timedelta

# Default values
DEFAULT_EMAIL = "admin@example.com"
SOUNDS = ['alert', 'ding', 'chime', 'pristine']
BASE_URL = "http://localhost:5000"  # Change to your actual app URL when testing remotely

def send_test_notification(email, sound):
    """Send a test notification with the specified sound"""
    try:
        print(f"📱 Sending test notification to {email} with sound: {sound}")
        
        # Prepare test data
        test_data = {
            "title": f"Test Notification Sound: {sound}",
            "message": f"This is a test notification with sound: {sound}",
            "email": email,
            "sound": sound
        }
        
        # Send request to test notification endpoint
        response = requests.post(
            f"{BASE_URL}/send-test-notification",
            json=test_data
        )
        
        if response.status_code == 200:
            print(f"✅ Test notification sent successfully with sound: {sound}")
            print(f"   Response: {response.json().get('message', 'No message')}")
            return True
        else:
            print(f"❌ Failed to send test notification: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    
    except Exception as e:
        print(f"❌ Error sending test notification: {e}")
        return False

def main():
    """Main function to parse arguments and send test notifications"""
    # Parse command line arguments
    email = DEFAULT_EMAIL
    sound = None
    
    if len(sys.argv) > 1:
        email = sys.argv[1]
    
    if len(sys.argv) > 2:
        sound = sys.argv[2]
        if sound not in SOUNDS:
            print(f"⚠️ Unknown sound: {sound}")
            print(f"Available sounds: {', '.join(SOUNDS)}")
            return
    
    print("🔊 Smart Reminder Pro - Notification Sound Test")
    print("===============================================")
    
    if sound:
        # Send notification with specified sound
        send_test_notification(email, sound)
    else:
        # Send notifications with all sounds, one after the other
        print(f"🔄 Sending test notifications with all sounds to {email}")
        
        for sound in SOUNDS:
            success = send_test_notification(email, sound)
            if success and sound != SOUNDS[-1]:
                print("⏳ Waiting 5 seconds before next notification...")
                time.sleep(5)  # Wait between notifications
    
    print("\n📝 Testing Tips:")
    print("  - Make sure the device is not on silent mode")
    print("  - Check that notifications are enabled for the app")
    print("  - Test with the app in foreground, background, and closed")
    print("  - On iOS, user interaction may be required to play sounds")
    print("  - Check service worker registration and subscription")

if __name__ == "__main__":
    main()
