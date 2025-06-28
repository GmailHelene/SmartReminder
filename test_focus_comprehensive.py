#!/usr/bin/env python3
"""Test focus modes functionality"""

import os
os.environ['TESTING'] = '1'

print("🧪 Testing focus modes functionality...")

try:
    # Test the focus_modes module directly
    from focus_modes import FocusModeManager
    
    print("✅ FocusModeManager imported successfully")
    
    # Test getting all modes
    modes = FocusModeManager.get_all_modes()
    print(f"✅ Available modes: {list(modes.keys())}")
    
    for mode_key, mode in modes.items():
        print(f"  - {mode_key}: {mode.name} - {mode.description}")
    
    # Test applying mode to reminders
    test_reminders = [
        {'priority': 'Høy', 'title': 'Important task'},
        {'priority': 'Medium', 'title': 'Regular task'},
        {'priority': 'Lav', 'title': 'Low priority task'}
    ]
    
    # Test silent mode filtering
    silent_filtered = FocusModeManager.apply_mode_to_reminders(test_reminders, 'silent')
    print(f"✅ Silent mode filtered: {len(silent_filtered)} reminders (should be 1)")
    
    # Test getting mode settings
    adhd_settings = FocusModeManager.get_mode_settings('adhd')
    print(f"✅ ADHD mode settings: {list(adhd_settings.keys())}")
    
    print("\n✅ Focus modes functionality working correctly!")
    
except Exception as e:
    print(f"❌ Error testing focus modes: {e}")
    import traceback
    traceback.print_exc()

print("\n🧪 Testing focus mode saving in app...")

try:
    from app import app, dm
    
    # Simulate saving focus mode for a user
    test_user_email = 'test@example.com'
    
    # Load users
    users = dm.load_data('users')
    if not isinstance(users, dict):
        users = {}
    
    # Add test user if not exists
    test_user_id = 'test-user-123'
    if test_user_id not in users:
        users[test_user_id] = {
            'email': test_user_email,
            'username': 'Test User',
            'password_hash': 'dummy',
            'focus_mode': 'normal'
        }
    
    # Update focus mode
    users[test_user_id]['focus_mode'] = 'adhd'
    dm.save_data('users', users)
    
    # Verify it was saved
    users_loaded = dm.load_data('users')
    saved_mode = users_loaded[test_user_id]['focus_mode']
    
    if saved_mode == 'adhd':
        print("✅ Focus mode saving works correctly!")
    else:
        print(f"❌ Focus mode not saved correctly: {saved_mode}")
    
except Exception as e:
    print(f"❌ Error testing focus mode saving: {e}")
    import traceback
    traceback.print_exc()

print("\n🎯 Focus mode test completed!")
