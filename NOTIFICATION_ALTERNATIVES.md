# Alternative Notification Methods for SmartReminder

## Problem Summary
WebPush notifications with VAPID keys are causing "Invalid EC key" errors despite multiple attempts at generating compatible keys. This document outlines alternative notification approaches that don't require WebPush.

## Option 1: Browser-Based Notifications (Simplest)

### Implementation:
```javascript
// In app.js or a dedicated notifications.js file
function showLocalNotification(title, message, icon = '/static/images/icon-192x192.png', sound = 'pristine.mp3') {
  // Play sound first (requires user interaction first time)
  if (sound) {
    const audio = new Audio(`/static/sounds/${sound}`);
    audio.play().catch(err => console.log('Could not play notification sound:', err));
  }
  
  // Show notification if supported
  if ('Notification' in window) {
    if (Notification.permission === 'granted') {
      new Notification(title, {
        body: message,
        icon: icon,
        vibrate: [200, 100, 200]
      });
    } else if (Notification.permission !== 'denied') {
      Notification.requestPermission().then(permission => {
        if (permission === 'granted') {
          new Notification(title, {
            body: message,
            icon: icon,
            vibrate: [200, 100, 200]
          });
        }
      });
    }
  }
}

// Usage:
// showLocalNotification('Reminder', 'Meeting in 5 minutes', null, 'alert.mp3');
```

### Server-Side:
```python
# In app.py or a dedicated file
@app.route('/api/trigger-notification', methods=['POST'])
def trigger_notification():
    """Triggers a client-side notification via SSE or polling"""
    data = request.json
    user_email = data.get('user_email')
    
    # Store notification in database
    notification = {
        'user_email': user_email,
        'title': data.get('title', 'Notification'),
        'message': data.get('message', ''),
        'sound': data.get('sound', 'pristine.mp3'),
        'icon': data.get('icon', '/static/images/icon-192x192.png'),
        'timestamp': datetime.now().isoformat(),
        'read': False
    }
    
    # Add to notifications data store
    notifications = dm.load_data('notifications')
    if user_email not in notifications:
        notifications[user_email] = []
    notifications[user_email].append(notification)
    dm.save_data('notifications', notifications)
    
    return jsonify({'success': True})
```

## Option 2: Server-Sent Events (SSE)

### Server Implementation:
```python
# In app.py
@app.route('/api/notifications/stream')
def notification_stream():
    """Creates an SSE stream for real-time notifications"""
    def generate():
        user_email = request.args.get('user_email')
        if not user_email:
            return
            
        # Send initial heartbeat
        yield "data: {\"type\": \"connected\"}\n\n"
        
        last_check = datetime.now()
        
        while True:
            # Check for new notifications
            notifications = dm.load_data('notifications')
            user_notifications = notifications.get(user_email, [])
            
            # Filter for unread notifications since last check
            new_notifications = [
                n for n in user_notifications 
                if not n.get('read') and datetime.fromisoformat(n.get('timestamp')) > last_check
            ]
            
            # Send any new notifications
            for notification in new_notifications:
                yield f"data: {json.dumps(notification)}\n\n"
                
            last_check = datetime.now()
            time.sleep(3)  # Check every 3 seconds
            
            # Send heartbeat to keep connection alive
            yield "data: {\"type\": \"heartbeat\"}\n\n"
    
    response = app.response_class(
        stream_with_context(generate()),
        mimetype='text/event-stream'
    )
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['X-Accel-Buffering'] = 'no'
    return response
```

### Client Implementation:
```javascript
// In app.js
function connectToNotificationStream(userEmail) {
  if (!userEmail) return;
  
  const evtSource = new EventSource(`/api/notifications/stream?user_email=${userEmail}`);
  
  evtSource.onmessage = function(event) {
    const data = JSON.parse(event.data);
    
    // Ignore heartbeats
    if (data.type === 'heartbeat' || data.type === 'connected') {
      return;
    }
    
    // Show notification
    showLocalNotification(
      data.title, 
      data.message,
      data.icon,
      data.sound
    );
    
    // Mark as read
    fetch('/api/notifications/mark-read', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        user_email: userEmail,
        timestamp: data.timestamp
      })
    });
  };
  
  evtSource.onerror = function() {
    console.log('SSE connection error, reconnecting in 5s...');
    evtSource.close();
    setTimeout(() => connectToNotificationStream(userEmail), 5000);
  };
  
  // Store for cleanup
  window.notificationEventSource = evtSource;
}

// Call this when user logs in
// connectToNotificationStream('user@example.com');
```

## Option 3: Simple Polling

### Client Implementation:
```javascript
// In app.js
function startNotificationPolling(userEmail, interval = 10000) {
  if (!userEmail) return;
  
  // Initial check
  checkForNotifications(userEmail);
  
  // Set up interval
  const pollingInterval = setInterval(() => {
    checkForNotifications(userEmail);
  }, interval);
  
  // Store for cleanup
  window.notificationPolling = pollingInterval;
}

function checkForNotifications(userEmail) {
  fetch(`/api/notifications/check?user_email=${userEmail}`)
    .then(response => response.json())
    .then(data => {
      if (data.notifications && data.notifications.length > 0) {
        data.notifications.forEach(notification => {
          showLocalNotification(
            notification.title,
            notification.message,
            notification.icon,
            notification.sound
          );
        });
        
        // Mark as read
        fetch('/api/notifications/mark-read', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({
            user_email: userEmail,
            timestamps: data.notifications.map(n => n.timestamp)
          })
        });
      }
    })
    .catch(err => console.error('Error checking notifications:', err));
}

// Call this when user logs in
// startNotificationPolling('user@example.com');
```

### Server Implementation:
```python
@app.route('/api/notifications/check')
def check_notifications():
    """Checks for new notifications for a user"""
    user_email = request.args.get('user_email')
    if not user_email:
        return jsonify({'error': 'User email required'})
    
    notifications = dm.load_data('notifications')
    user_notifications = notifications.get(user_email, [])
    
    # Filter for unread notifications
    unread = [n for n in user_notifications if not n.get('read', False)]
    
    return jsonify({'notifications': unread})

@app.route('/api/notifications/mark-read', methods=['POST'])
def mark_notifications_read():
    """Marks notifications as read"""
    data = request.json
    user_email = data.get('user_email')
    timestamps = data.get('timestamps', [])
    
    if not user_email or not timestamps:
        return jsonify({'error': 'User email and timestamps required'})
    
    # If single timestamp provided
    if isinstance(timestamps, str):
        timestamps = [timestamps]
    
    notifications = dm.load_data('notifications')
    user_notifications = notifications.get(user_email, [])
    
    # Mark matching notifications as read
    for notification in user_notifications:
        if notification.get('timestamp') in timestamps:
            notification['read'] = True
    
    notifications[user_email] = user_notifications
    dm.save_data('notifications', notifications)
    
    return jsonify({'success': True})
```

## Implementation Plan

1. Add browser notification support first (Option 1)
2. Implement SSE or polling as needed for real-time updates
3. Verify sound playback works with user interaction
4. Add this as a fallback to WebPush in production

## Benefits

- No VAPID keys or complex encryption required
- Works in all modern browsers
- Simpler implementation and debugging
- Sound support still works
- Can be implemented alongside WebPush as a fallback
