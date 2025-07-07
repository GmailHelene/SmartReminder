"""
Test Notification System

This script tests the notification system by creating a reminder that will trigger
a notification in a few minutes. Use this to verify notification sounds are working correctly.
"""

import os
import sys
import json
import uuid
import time
from datetime import datetime, timedelta

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import app and data manager
from app import app, dm

def create_test_reminder(user_email, minutes_from_now=1, sound='pristine.mp3'):
    """Create a test reminder that will trigger a notification in X minutes"""
    # Generate reminder time (X minutes from now)
    now = datetime.now()
    reminder_time = now + timedelta(minutes=minutes_from_now)
    reminder_dt_str = reminder_time.strftime("%Y-%m-%d %H:%M:%S")
    
    # Create a new reminder
    reminder_id = str(uuid.uuid4())
    reminder = {
        'id': reminder_id,
        'user_id': user_email,
        'title': f'Test Alarm {now.strftime("%H:%M:%S")}',
        'description': f'Dette er en test-påminnelse opprettet {now.strftime("%H:%M:%S")} for å teste varslinger.',
        'datetime': reminder_dt_str,
        'priority': 'Høy',
        'category': 'Test',
        'sound': sound,
        'completed': False,
        'created': now.isoformat(),
        'shared_with': []
    }
    
    # Load existing reminders
    reminders = dm.load_data('reminders')
    
    # Add new reminder
    reminders.append(reminder)
    
    # Save updated reminders
    dm.save_data('reminders', reminders)
    
    print(f"✅ Test reminder created for {user_email}")
    print(f"⏰ Will trigger at: {reminder_dt_str} ({minutes_from_now} minutes from now)")
    print(f"🔔 Using sound: {sound}")
    print(f"🆔 Reminder ID: {reminder_id}")
    
    return reminder_id

def main():
    """Run the test"""
    print("=== SmartReminder Notification Test ===")
    print("This will create a test reminder to trigger soon")
    
    # User email to test with
    test_email = input("Enter email to test notifications with: ").strip()
    
    # Minutes until notification
    try:
        minutes = int(input("Minutes until notification triggers (1-5): ").strip())
        if minutes < 1 or minutes > 5:
            minutes = 1
            print("Using default: 1 minute")
    except ValueError:
        minutes = 1
        print("Using default: 1 minute")
    
    # Sound to use
    print("\nAvailable sounds:")
    print("1) pristine.mp3 (default)")
    print("2) ding.mp3")
    print("3) chime.mp3")
    print("4) alert.mp3")
    
    try:
        sound_choice = int(input("Choose sound (1-4): ").strip())
        sounds = ['pristine.mp3', 'ding.mp3', 'chime.mp3', 'alert.mp3']
        sound = sounds[sound_choice - 1] if 1 <= sound_choice <= 4 else 'pristine.mp3'
    except (ValueError, IndexError):
        sound = 'pristine.mp3'
        print("Using default sound: pristine.mp3")
    
    # Create the test reminder
    reminder_id = create_test_reminder(test_email, minutes, sound)
    
    print("\n🧪 Test setup complete!")
    print(f"📱 Ensure your device is not in silent mode")
    print(f"📱 Make sure the app is open in the browser")
    print(f"📱 Wait approximately {minutes} minutes for the notification to trigger")
    
    if minutes > 1:
        # Countdown timer
        print("\nCountdown until notification:")
        for remaining in range(minutes * 60, 0, -10):
            mins, secs = divmod(remaining, 60)
            print(f"\r⏱️ Time remaining: {mins:02d}:{secs:02d}", end='')
            time.sleep(10)
        print("\r⏱️ Time's up! Check for notification!            ")
    
if __name__ == "__main__":
    main()
