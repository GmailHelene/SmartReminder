# SmartReminder Notification System Test Guide

This guide provides instructions on how to test the notification system of SmartReminder, including push notifications, alarm notifications, and focus mode notification behavior.

## Prerequisites

Before testing, make sure:

1. The SmartReminder app is running
2. You have a valid user account in the system
3. Your browser supports push notifications
4. Notification permissions are enabled for the app in your browser

## Quick Start

To run a comprehensive test of the notification system:

```bash
python3 test_comprehensive_notifications.py [user_email]
```

If no user email is provided, the script will use the first user in the database or the default test user.

## Individual Tests

### 1. Test Push Subscriptions

To create a test push subscription for a user:

```bash
python3 create_test_subscription.py [user_email]
```

This is useful if you need to manually create a push subscription for testing.

### 2. Test Alarm Notifications

To test alarm notifications with different sounds:

```bash
python3 test_alarm_notification.py [user_email]
```

This script will send test notifications with each available sound.

## Troubleshooting Common Issues

### No Push Subscriptions Found

If the test shows "No push subscriptions found" for a user, you can:

1. Run `create_test_subscription.py` to create a test subscription
2. Verify the user exists in the database
3. Check if VAPID keys are properly configured in `push_service.py`

### Sound Not Playing on Mobile

Mobile devices have restrictions on audio playback:

1. Make sure the user has interacted with the page at least once
2. Try clicking the manual play button that appears
3. Verify the device is not in silent mode
4. Check that the Service Worker is registered correctly

### Service Worker Issues

If Service Worker-related tests fail:

1. Check that the Service Worker is registered with the correct scope
2. Verify that `sw.js` has the proper `clients.matchAll()` and `postMessage()` implementations
3. Check the browser console for Service Worker registration errors

## Focus Mode Testing

Different focus modes may affect notification behavior:

1. Test notifications in each focus mode
2. Verify sound and vibration settings are respected
3. Ensure fallback mechanisms work properly in silent modes

## Important Notes

- On iOS, Web Push Notifications have limited support
- For full testing on mobile, install the app as a PWA
- Some browsers require user interaction before playing sounds
- Vibration is only supported on mobile devices with vibration hardware

## Mock Testing Mode

For testing the notification system without sending real push notifications or encountering VAPID key issues, you can use the mock testing mode:

```bash
python3 test_comprehensive_notifications.py --mock [user_email]
```

or for the quick test:

```bash
python3 test_notification_fix.py --mock
```

### How Mock Mode Works

The mock mode:

1. Generates a mock version of the push service that logs notification details instead of sending real notifications
2. Bypasses WebPush API validation, which avoids "Invalid EC key" errors
3. Still performs all the notification flow logic so you can verify your code is working
4. Creates console output showing what notifications would have been sent

### When to Use Mock Mode

Use mock mode when:

- You're testing notification code logic without needing to see actual notifications
- You encounter VAPID key issues in your test environment
- You want to test notification handling without browser permission prompts
- You're running automated tests in CI/CD pipelines

### Mock Mode vs Real Mode

| Feature | Mock Mode | Real Mode |
|---------|-----------|-----------|
| Speed | Faster (no API calls) | Normal |
| VAPID Key Requirements | None | Valid keys required |
| Actual Notifications | No | Yes |
| Browser Permissions | Not needed | Required |
| Test Coverage | Logic only | Full end-to-end |
| Suitable for | Development & CI | Final validation |

## Fixing VAPID Key Issues

If you encounter "Invalid EC key" errors with the real notification service, the issue is likely with the VAPID keys. Here's how to fix it:

### Generate New VAPID Keys

1. Run the included script to generate new VAPID keys:

```bash
python3 generate_vapid_keys.py
```

2. Update the keys in `push_service.py`:

```python
# VAPID keys for push notifications
VAPID_PRIVATE_KEY = "your_new_private_key_here"
VAPID_PUBLIC_KEY = "your_new_public_key_here"
VAPID_CLAIMS = {"sub": "mailto:your_email@example.com"}
```

3. Make sure the keys are properly formatted:
   - Private key should be an unpadded URL-safe base64 string
   - Public key should be an unpadded URL-safe base64 string
   - Both keys should not contain any line breaks or extra spaces

### Using Environment Variables for VAPID Keys

For production, it's better to use environment variables instead of hardcoding the keys:

```python
import os

# Get VAPID keys from environment variables
VAPID_PRIVATE_KEY = os.environ.get('VAPID_PRIVATE_KEY')
VAPID_PUBLIC_KEY = os.environ.get('VAPID_PUBLIC_KEY')
VAPID_CLAIMS = {"sub": f"mailto:{os.environ.get('VAPID_CLAIM_EMAIL', 'admin@smartreminder.com')}"}
```

### Validating VAPID Keys

To verify your VAPID keys are valid:

```python
from pywebpush import WebPushException
import base64

def validate_vapid_key(key):
    """Validate that a VAPID key is properly formatted"""
    try:
        # Try to decode as base64
        decoded = base64.urlsafe_b64decode(key + "==")
        # EC P-256 keys should be 65 bytes for public, 32 bytes for private
        if len(decoded) not in (32, 65):
            return False
        return True
    except Exception:
        return False

# Test your keys
print(f"Private key valid: {validate_vapid_key(VAPID_PRIVATE_KEY)}")
print(f"Public key valid: {validate_vapid_key(VAPID_PUBLIC_KEY)}")
```
