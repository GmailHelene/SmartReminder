# Smart Reminder Pro Notification System Documentation

This document provides an overview of the notification system in Smart Reminder Pro, focusing on mobile notifications, sound playback, and related features.

## Overview

The notification system in Smart Reminder Pro has been enhanced to provide a reliable and user-friendly experience across different devices, particularly mobile. The system includes:

1. **Push Notifications** - Web push notifications for reminders and shared board activities
2. **Sound Playback** - Customizable notification sounds with reliable playback
3. **Email Notifications** - Enhanced templates for shared board activities
4. **Fallback Mechanisms** - For devices or browsers with limited capabilities

## Key Components

### 1. Service Worker (`static/sw.js`)

The service worker handles:
- Receiving push events
- Displaying notifications
- Triggering sound playback
- Fallback mechanisms when no client is active
- Handling notification clicks

Key improvements:
- Sound information is now included in all notification payloads
- Service worker attempts to play sounds via active clients
- If no clients are available, the sound is cached for playback when the app opens
- Response handling for all requests

### 2. Frontend JavaScript (`static/js/app.js`)

The frontend handles:
- Service worker registration
- Sound playback when triggered by service worker
- Manual sound playback buttons
- Fallback UI for browsers with limited capabilities
- Checking for pending sounds on app load

Key improvements:
- Message listener for receiving sound playback commands
- Multiple fallback mechanisms (vibration, toast, manual play button)
- Automatic sound playback from cached requests

### 3. Backend (`app.py` and `push_service.py`)

The backend ensures:
- Sound selection is stored with reminders
- Sound is included in push notification payloads
- Test endpoints for notification testing
- Admin-only access to email settings

Key improvements:
- Sound parameter handling in all reminder APIs
- Test notification endpoint with sound selection
- Enhanced security for email settings

### 4. Email Templates

The email templates for shared boards have been improved:
- Better contrast for readability
- Clear distinction from regular reminders
- Prominent badges and warnings
- Consistent styling between different templates

## Testing the Notification System

### Testing Tools

1. **Test Notification Flow Script**
   ```
   python3 /workspaces/smartreminder/test_notification_flow.py
   ```
   This script checks all components of the notification system including sound files, service worker, push notifications, and email templates.

2. **Email Template Test**
   ```
   python3 /workspaces/smartreminder/test_email_improvements.py
   ```
   This script verifies improvements in email templates for shared boards.

3. **Sound Test Page**
   Access `/sound-test` in the app (admin only) to test different notification sounds directly.

### Testing on Real Devices

To thoroughly test the notification system on real mobile devices:

1. **Install as PWA**:
   - Open the app in Chrome on Android or Safari on iOS
   - Use "Add to Home Screen" option
   - Launch the app from the home screen icon

2. **Test Push Notifications**:
   - Create a reminder set to trigger in 1-2 minutes
   - Close the app completely
   - Verify notification appears with sound
   - Test with screen on and off

3. **Test Sound Playback**:
   - Try different notification sounds
   - Test with device on silent/vibrate mode
   - Check if fallback mechanisms work (vibration, manual play)

4. **Test Shared Board Notifications**:
   - Share a board with another user
   - Make updates to the board
   - Verify the other user receives email and push notifications
   - Check clarity of notification content

5. **Test Cross-Browser**:
   - Test in Chrome, Safari, Firefox, and other browsers
   - Note any differences in behavior

## Troubleshooting

### Common Issues

1. **No Sound on iOS**:
   - iOS requires user interaction to play sounds
   - Tap the "Play Sound" button or notification
   - Check if device is on silent mode

2. **Notification Permission Denied**:
   - Clear site data and permissions
   - Try again with "Allow" for notifications

3. **Service Worker Not Updating**:
   - Clear cache and site data
   - Refresh the page multiple times
   - Check console for registration errors

4. **Email Notifications Not Received**:
   - Check spam folder
   - Verify email address is correct
   - Check email logs in the admin panel

## Future Improvements

Potential enhancements to consider:

1. **Offline Notification Queue** - Store and trigger notifications when device comes online
2. **Badge API Integration** - Show notification counts on the app icon
3. **Notification Grouping** - Group multiple notifications from the same board
4. **Customizable Notification Schedule** - Allow users to set quiet hours
5. **Analytics** - Track notification delivery and interaction rates

---

## Technical Reference

### Sound Files Location
```
/static/sounds/
  ├── alert.mp3
  ├── chime.mp3
  ├── ding.mp3
  └── pristine.mp3
```

### Key Files
- Service Worker: `/static/sw.js`
- App JavaScript: `/static/js/app.js`
- Push Service: `/push_service.py`
- App Routes: `/app.py`
- Email Templates: `/templates/emails/`

### Testing Scripts
- Flow Test: `/test_notification_flow.py`
- Email Test: `/test_email_improvements.py`
- Alarm Test: `/test_alarm_notification.py`
