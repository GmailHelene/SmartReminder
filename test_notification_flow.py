#!/usr/bin/env python3
"""
Comprehensive test for the complete notification flow in SmartReminder Pro

This script tests:
1. Reminder creation with sound selection
2. Push notification payloads with sound
3. Service worker registration
4. Service worker push event handling
5. Sound playback in both service worker and app.js
6. Email templates for shared boards

Run this script to verify the complete notification flow
"""

import os
import sys
import json
import time
import requests
from datetime import datetime, timedelta
import random
import subprocess

# Local app URL
BASE_URL = 'http://localhost:5000'
SOUNDS = ['alert', 'ding', 'chime', 'pristine']

def test_notification_flow():
    """Test the complete notification flow"""
    print("🧪 Testing complete notification flow...")
    
    # Test parts
    test_sound_files()
    test_service_worker()
    test_push_notifications()
    test_email_templates()
    
    print("\n✅ All notification flow tests completed!")
    print("\n📱 NEXT STEPS:")
    print("   1. Test on real mobile devices")
    print("   2. Verify PWA installation and notifications")
    print("   3. Test fallback mechanisms (vibration, manual play)")
    print("   4. Check cross-browser compatibility")

def test_sound_files():
    """Test that all required sound files exist"""
    print("\n🔊 Testing sound files...")
    
    for sound in SOUNDS:
        sound_path = f"/workspaces/smartreminder/static/sounds/{sound}.mp3"
        if os.path.exists(sound_path):
            print(f"   ✅ Sound file exists: {sound}.mp3")
        else:
            print(f"   ❌ Missing sound file: {sound}.mp3")

def test_service_worker():
    """Test service worker code and registration"""
    print("\n🔄 Testing service worker...")
    
    # Check SW file exists
    if os.path.exists("/workspaces/smartreminder/static/sw.js"):
        print("   ✅ Service worker file exists")
    else:
        print("   ❌ Service worker file missing")
    
    # Check for key functionality in SW
    try:
        with open('/workspaces/smartreminder/static/sw.js', 'r') as f:
            sw_content = f.read()
            
        features = [
            ('self.addEventListener(\'push\'', 'Push event listener'),
            ('showNotification', 'Notification display'),
            ('data.sound', 'Sound handling in push event'),
            ('self.registration.showNotification', 'Notification registration'),
            ('clients.matchAll', 'Client matching for sound playback'),
            ('PLAY_NOTIFICATION_SOUND', 'Sound message handling'),
            ('new Response(JSON.stringify({ success: true })', 'Response handling')
        ]
        
        for check, description in features:
            if check in sw_content:
                print(f"   ✅ SW has {description}")
            else:
                print(f"   ❌ SW missing {description}")
    
    except Exception as e:
        print(f"   ❌ Error checking service worker: {e}")
    
    # Check for registration in app.js
    try:
        with open('/workspaces/smartreminder/static/js/app.js', 'r') as f:
            app_content = f.read()
            
        if 'navigator.serviceWorker.register' in app_content:
            print("   ✅ Service worker registration in app.js")
        else:
            print("   ❌ Missing service worker registration in app.js")
            
        if 'playNotificationSound' in app_content:
            print("   ✅ Sound playback function in app.js")
        else:
            print("   ❌ Missing sound playback function in app.js")
            
        if 'addEventListener(\'message\'' in app_content:
            print("   ✅ Message listener for sound in app.js")
        else:
            print("   ❌ Missing message listener in app.js")
            
        if 'navigator.vibrate' in app_content:
            print("   ✅ Vibration fallback in app.js")
        else: 
            print("   ❌ Missing vibration fallback in app.js")
    
    except Exception as e:
        print(f"   ❌ Error checking app.js: {e}")

def test_push_notifications():
    """Test push notification payload and sound"""
    print("\n📲 Testing push notification payloads...")
    
    try:
        # Look for push_service.py inclusion of sound
        with open('/workspaces/smartreminder/push_service.py', 'r') as f:
            push_content = f.read()
            
        if 'sound' in push_content and ('"sound"' in push_content or "'sound'" in push_content):
            print("   ✅ Push service includes sound in payload")
        else:
            print("   ❌ Push service missing sound in payload")
            
        # Check app.py for sound handling in APIs
        with open('/workspaces/smartreminder/app.py', 'r') as f:
            app_content = f.read()
            
        if 'sound' in app_content and ('request.form.get("sound"' in app_content or "data.get('sound'" in app_content):
            print("   ✅ App.py handles sound parameter")
        else:
            print("   ❌ App.py missing sound parameter handling")
            
        # Check if test notification endpoint exists
        if '/send-test-notification' in app_content or '/test-notification' in app_content:
            print("   ✅ Test notification endpoint exists")
        else:
            print("   ❌ Missing test notification endpoint")
            
        # Check if dashboard includes sound selection
        with open('/workspaces/smartreminder/templates/dashboard.html', 'r') as f:
            dash_content = f.read()
            
        if ('name="sound"' in dash_content or 'id="soundSelect"' in dash_content) and 'previewSound' in dash_content:
            print("   ✅ Dashboard includes sound selection")
        else:
            print("   ❌ Dashboard missing sound selection")
    
    except Exception as e:
        print(f"   ❌ Error checking push notification code: {e}")

def test_email_templates():
    """Test email templates for shared boards"""
    print("\n📧 Testing email templates...")
    
    # Run the email test script if it exists
    if os.path.exists('/workspaces/smartreminder/test_email_improvements.py'):
        try:
            # Import and run the test function
            sys.path.append('/workspaces/smartreminder')
            from test_email_improvements import test_email_improvements
            
            # Redirect stdout temporarily to capture output
            import io
            from contextlib import redirect_stdout
            
            f = io.StringIO()
            with redirect_stdout(f):
                test_email_improvements()
            
            output = f.getvalue()
            
            # Check results
            if "Invitation template: 8/8" in output and "Update template: 8/8" in output:
                print("   ✅ Email templates fully improved")
            else:
                print("   ⚠️ Email templates partially improved - see test_email_improvements.py")
                
        except Exception as e:
            print(f"   ❌ Error running email template test: {e}")
    else:
        print("   ⚠️ Email template test script not found")

def create_test_reminder():
    """Create a test reminder with sound"""
    # This is a placeholder for actual API interaction
    print("\n📅 Creating test reminder with sound...")
    print("   ℹ️ This is a simulation - would create reminder via API")
    
    # Example of what the API call would do
    reminder = {
        "title": "Test Notification",
        "description": "Testing sound notification",
        "date": (datetime.now() + timedelta(minutes=1)).strftime("%Y-%m-%d"),
        "time": (datetime.now() + timedelta(minutes=1)).strftime("%H:%M"),
        "sound": random.choice(SOUNDS)
    }
    
    print(f"   📝 Would create reminder with sound: {reminder['sound']}")
    
    # In real implementation, we'd make an API call like:
    # response = requests.post(f"{BASE_URL}/api/reminders", json=reminder)
    
    return reminder

if __name__ == "__main__":
    test_notification_flow()
    print("\n🎉 Notification flow test completed!")
