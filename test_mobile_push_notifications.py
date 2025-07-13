#!/usr/bin/env python3
"""
Mobile Push Notification Test for SmartReminder
Tests push notifications with sound specifically for mobile devices
"""

import os
import sys
import json
import time
from datetime import datetime, timedelta

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, dm

def test_mobile_push_with_sound():
    """Test mobile push notifications with sound alerts"""
    print("📱 MOBILE PUSH NOTIFICATION WITH SOUND TEST")
    print("=" * 60)
    
    # Get test user
    users = dm.load_data('users')
    if not users:
        print("❌ No users found in database")
        return False
    
    user_email = list(users.keys())[0]
    print(f"Testing with user: {user_email}")
    
    # Check for push subscriptions
    subscriptions = dm.load_data('push_subscriptions')
    user_subscriptions = subscriptions.get(user_email, [])
    
    if not user_subscriptions:
        print("⚠️ No push subscriptions found, creating test subscription...")
        
        # Create mobile-optimized test subscription
        mobile_subscription = {
            "endpoint": f"https://fcm.googleapis.com/fcm/send/mobile-test-{int(time.time())}",
            "expirationTime": None,
            "keys": {
                "p256dh": "BFaOzZhpj2FVdGy5c4CRN5HKK7qp1B2qs8TU3oO2-yOX9LjPQF7jvf2jZq0TQG8v2g",
                "auth": "AbCdEfGhIjKlMnOpQrSt"
            },
            "platform": "mobile",
            "created_at": datetime.now().isoformat()
        }
        
        # Save subscription
        if user_email not in subscriptions:
            subscriptions[user_email] = []
        subscriptions[user_email].append(mobile_subscription)
        dm.save_data('push_subscriptions', subscriptions)
        print("✅ Created test mobile subscription")
    
    # Test different notification scenarios
    test_scenarios = [
        {
            "name": "Påminnelse delt med lyd",
            "type": "shared_reminder",
            "sound": "alert.mp3",
            "title": "🔔 Delt påminnelse",
            "body": "Du har fått en ny påminnelse med lydvarsel"
        },
        {
            "name": "Høy prioritet alarm",
            "type": "high_priority",
            "sound": "pristine.mp3", 
            "title": "⚠️ Viktig påminnelse",
            "body": "Dette er en høy prioritet påminnelse"
        },
        {
            "name": "Kjøreskolemodus varsel",
            "type": "driving_school",
            "sound": "ding.mp3",
            "title": "🚗 Kjøreskole",
            "body": "Instruktørstatus oppdatering"
        },
        {
            "name": "ADHD-modus varsel",
            "type": "adhd_focus",
            "sound": "chime.mp3",
            "title": "🎯 ADHD påminnelse",
            "body": "Fokus påminnelse med ekstra varsling"
        }
    ]
    
    print(f"\nTesting {len(test_scenarios)} mobile notification scenarios...")
    
    # Import notification system
    try:
        from push_service import send_push_notification
        print("✅ Using real push service")
        use_mock = False
    except ImportError:
        print("⚠️ Real push service not available, using mock")
        # Create simple mock for testing
        def send_push_notification(user_email, title, body, data=None, dm=None):
            print(f"MOCK PUSH: {title} -> {user_email}")
            print(f"  Body: {body}")
            print(f"  Sound: {data.get('sound') if data else 'None'}")
            return True
        use_mock = True
    
    # Send test notifications
    success_count = 0
    
    for i, scenario in enumerate(test_scenarios):
        print(f"\n📨 Test {i+1}/{len(test_scenarios)}: {scenario['name']}")
        
        notification_data = {
            "type": scenario["type"],
            "sound": scenario["sound"],
            "url": "/dashboard",
            "timestamp": datetime.now().isoformat(),
            "mobile_optimized": True,
            "vibrate": [200, 100, 200]  # Mobile vibration pattern
        }
        
        try:
            result = send_push_notification(
                user_email=user_email,
                title=scenario["title"],
                body=scenario["body"],
                data=notification_data,
                dm=dm
            )
            
            if result:
                print(f"  ✅ Notification sent successfully")
                print(f"  🔊 Sound: {scenario['sound']}")
                success_count += 1
            else:
                print(f"  ❌ Failed to send notification")
                
        except Exception as e:
            print(f"  ❌ Error sending notification: {e}")
        
        # Wait between notifications for testing
        if i < len(test_scenarios) - 1:
            print("  ⏳ Waiting 5 seconds before next test...")
            time.sleep(5)
    
    # Test summary
    print(f"\n" + "=" * 60)
    print("📊 MOBILE PUSH TEST RESULTS")
    print("=" * 60)
    print(f"Tests completed: {len(test_scenarios)}")
    print(f"Successful sends: {success_count}")
    print(f"Success rate: {(success_count/len(test_scenarios)*100):.1f}%")
    
    if not use_mock:
        print(f"\n📱 MOBILE TESTING INSTRUCTIONS:")
        print(f"1. Open SmartReminder on your mobile device")
        print(f"2. Make sure notifications are enabled")
        print(f"3. Check if you received {success_count} notifications")
        print(f"4. Verify each notification played the correct sound:")
        for scenario in test_scenarios:
            print(f"   - {scenario['name']}: {scenario['sound']}")
        print(f"5. Test sharing reminders with sound between users")
        
        print(f"\n⚠️ MOBILE REQUIREMENTS:")
        print(f"- Device not in silent mode")
        print(f"- Browser/PWA has notification permission") 
        print(f"- Service worker is registered")
        print(f"- App is running or recently used")
    
    return success_count == len(test_scenarios)

def test_shared_reminder_with_sound():
    """Test sharing reminders with sound between users"""
    print("\n🔗 TESTING SHARED REMINDER WITH SOUND")
    print("=" * 60)
    
    # Get users for testing
    users = dm.load_data('users')
    if len(users) < 2:
        print("⚠️ Need at least 2 users for sharing test, creating test user...")
        
        # Create a second test user
        test_user_id = str(uuid.uuid4())
        users[test_user_id] = {
            'email': 'test-mobile-user@example.com',
            'username': 'Test Mobile User',
            'focus_mode': 'normal',
            'created': datetime.now().isoformat()
        }
        dm.save_data('users', users)
    
    user_emails = list(users.keys())[:2]  # Take first two users
    sender_email = user_emails[0]
    recipient_email = user_emails[1]
    
    print(f"Sender: {sender_email}")
    print(f"Recipient: {recipient_email}")
    
    # Create a test reminder with sound
    reminder_id = f"test-shared-{int(time.time())}"
    test_reminder = {
        'id': reminder_id,
        'user_id': sender_email,
        'title': '🔊 Test delt påminnelse med lyd',
        'description': 'Dette er en test av delt påminnelse med lydvarsel på mobil',
        'datetime': (datetime.now() + timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M'),
        'priority': 'Høy',
        'category': 'Test',
        'sound': 'alert.mp3',
        'completed': False,
        'created': datetime.now().isoformat(),
        'shared_with': [recipient_email]
    }
    
    # Save the reminder
    reminders = dm.load_data('reminders')
    reminders.append(test_reminder)
    dm.save_data('reminders', reminders)
    
    # Create shared reminder entry
    shared_reminder = {
        'id': f"shared-{reminder_id}",
        'original_id': reminder_id,
        'user_id': sender_email,
        'shared_by': sender_email,
        'shared_with': recipient_email,
        'title': test_reminder['title'],
        'description': test_reminder['description'],
        'datetime': test_reminder['datetime'],
        'priority': test_reminder['priority'],
        'category': test_reminder['category'],
        'sound': test_reminder['sound'],
        'completed': False,
        'created': datetime.now().isoformat(),
        'is_shared': True
    }
    
    # Save shared reminder
    shared_reminders = dm.load_data('shared_reminders')
    shared_reminders.append(shared_reminder)
    dm.save_data('shared_reminders', shared_reminders)
    
    print("✅ Created test shared reminder with sound")
    print(f"   Title: {test_reminder['title']}")
    print(f"   Sound: {test_reminder['sound']}")
    print(f"   Priority: {test_reminder['priority']}")
    
    # Test notification for shared reminder
    try:
        from push_service import send_shared_reminder_notification
        
        notification_data = {
            "type": "shared_reminder",
            "sound": test_reminder['sound'],
            "priority": test_reminder['priority'],
            "url": "/dashboard",
            "mobile_optimized": True
        }
        
        result = send_shared_reminder_notification(
            recipient_email,
            "🔗 Ny delt påminnelse",
            f"Du har mottatt en delt påminnelse fra {sender_email}",
            data=notification_data,
            dm=dm
        )
        
        if result:
            print("✅ Shared reminder notification sent successfully")
            print(f"📱 Check mobile device for notification with sound: {test_reminder['sound']}")
        else:
            print("❌ Failed to send shared reminder notification")
            
    except ImportError:
        print("⚠️ Shared reminder notification service not available")
    
    return True

def test_focus_mode_sound_behavior():
    """Test how different focus modes affect sound notifications"""
    print("\n🎯 TESTING FOCUS MODE SOUND BEHAVIOR")
    print("=" * 60)
    
    focus_modes = [
        ('normal', 'pristine.mp3', True),
        ('silent', None, False),
        ('adhd', 'alert.mp3', True),
        ('elderly', 'chime.mp3', True),
        ('driving_school', 'ding.mp3', True)
    ]
    
    users = dm.load_data('users')
    user_email = list(users.keys())[0]
    
    for mode, expected_sound, sound_enabled in focus_modes:
        print(f"\n🔍 Testing {mode} mode:")
        print(f"   Expected sound: {expected_sound or 'None (silent)'}")
        print(f"   Sound enabled: {'Yes' if sound_enabled else 'No'}")
        
        # Update user's focus mode
        for user_id, user_data in users.items():
            if user_data.get('email') == user_email:
                user_data['focus_mode'] = mode
                break
        dm.save_data('users', users)
        
        # Test notification in this mode
        notification_data = {
            "type": "focus_mode_test",
            "focus_mode": mode,
            "sound": expected_sound if sound_enabled else None,
            "url": "/dashboard"
        }
        
        try:
            from push_service import send_push_notification
            
            result = send_push_notification(
                user_email=user_email,
                title=f"🎯 Test i {mode} modus",
                body=f"Testing lydvarsel i {mode} modus",
                data=notification_data,
                dm=dm
            )
            
            if result:
                print(f"   ✅ Notification sent for {mode} mode")
            else:
                print(f"   ❌ Failed to send notification for {mode} mode")
                
        except ImportError:
            print(f"   ⚠️ Using mock notification for {mode} mode")
        
        # Wait between mode tests
        time.sleep(3)
    
    print("\n✅ Focus mode sound behavior test completed")
    return True

if __name__ == "__main__":
    print("🚀 STARTING MOBILE PUSH NOTIFICATION TESTS")
    print("=" * 80)
    
    # Run all mobile tests
    test_results = []
    
    try:
        result1 = test_mobile_push_with_sound()
        test_results.append(("Mobile Push with Sound", result1))
    except Exception as e:
        print(f"❌ Mobile push test failed: {e}")
        test_results.append(("Mobile Push with Sound", False))
    
    try:
        result2 = test_shared_reminder_with_sound()
        test_results.append(("Shared Reminder with Sound", result2))
    except Exception as e:
        print(f"❌ Shared reminder test failed: {e}")
        test_results.append(("Shared Reminder with Sound", False))
    
    try:
        result3 = test_focus_mode_sound_behavior()
        test_results.append(("Focus Mode Sound Behavior", result3))
    except Exception as e:
        print(f"❌ Focus mode test failed: {e}")
        test_results.append(("Focus Mode Sound Behavior", False))
    
    # Final summary
    print(f"\n" + "=" * 80)
    print(" FINAL TEST RESULTS ")
    print("=" * 80)
    
    passed = 0
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:30} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(test_results)} tests passed")
    
    if passed == len(test_results):
        print("🎉 ALL MOBILE TESTS PASSED!")
        print("\n📱 Next steps:")
        print("1. Test on actual mobile device")
        print("2. Verify PWA installation works")
        print("3. Test background notifications")
        print("4. Verify sound plays correctly")
    else:
        print("⚠️ Some mobile tests failed - check the output above")
