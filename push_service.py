"""
Push Notification Service for SmartReminder
Handles web push notifications for mobile devices
"""

import json
import requests
from pywebpush import webpush, WebPushException
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# VAPID keys for push notifications (placeholder - should be replaced with real keys)
VAPID_PRIVATE_KEY = "your-vapid-private-key-here"
VAPID_PUBLIC_KEY = "BPKg5QjGtlY8n9VJ9VdWUFfaG8FKzX2sQ3ZmFUPvYGJ0qRdKF3XGzjFXQR2vX8qT1FPZU1Ywwx2x3Y4Z5A6B7C8D"
VAPID_CLAIMS = {"sub": "mailto:admin@smartreminder.com"}

def send_push_notification(user_email, title, body, data=None, dm=None):
    """Send push notification to user"""
    if not dm:
        return False
        
    try:
        subscriptions_data = dm.load_data('push_subscriptions')
        user_subscriptions = subscriptions_data.get(user_email, [])
        
        if not user_subscriptions:
            logger.info(f"No push subscriptions found for user {user_email}")
            return False
        
        notification_payload = {
            "title": title,
            "body": body,
            "icon": "/static/icons/icon-192x192.png",
            "badge": "/static/icons/icon-72x72.png",
            "tag": "smartreminder",
            "renotify": True,
            "data": data or {},
            "actions": [
                {
                    "action": "view",
                    "title": "Se detaljer"
                },
                {
                    "action": "dismiss", 
                    "title": "Lukk"
                }
            ]
        }
        
        success_count = 0
        invalid_subscriptions = []
        
        for subscription in user_subscriptions:
            try:
                response = webpush(
                    subscription_info=subscription,
                    data=json.dumps(notification_payload),
                    vapid_private_key=VAPID_PRIVATE_KEY,
                    vapid_claims=VAPID_CLAIMS
                )
                success_count += 1
                logger.info(f"Push notification sent successfully to {user_email}")
                
            except WebPushException as e:
                logger.error(f"Failed to send push notification to {user_email}: {e}")
                # Mark subscription for removal if it's invalid
                if e.response and e.response.status_code in [410, 404]:
                    invalid_subscriptions.append(subscription)
            except Exception as e:
                logger.error(f"Unexpected error sending push notification: {e}")
        
        # Remove invalid subscriptions
        if invalid_subscriptions:
            for invalid_sub in invalid_subscriptions:
                if invalid_sub in user_subscriptions:
                    user_subscriptions.remove(invalid_sub)
            
            subscriptions_data[user_email] = user_subscriptions
            dm.save_data('push_subscriptions', subscriptions_data)
            logger.info(f"Removed {len(invalid_subscriptions)} invalid subscriptions for {user_email}")
        
        return success_count > 0
        
    except Exception as e:
        logger.error(f"Error sending push notification to {user_email}: {e}")
        return False

def send_board_notification(board_id, action, content, exclude_user=None, dm=None):
    """Send notification to all board members except the user who performed the action"""
    if not dm:
        return False
        
    try:
        boards_data = dm.load_data('shared_noteboards')
        
        # Find the board
        board = None
        for board_data in boards_data.values():
            if board_data.get('board_id') == board_id:
                board = board_data
                break
        
        if not board:
            logger.warning(f"Board {board_id} not found for notification")
            return False
        
        title = f"📋 {board['title']}"
        body = f"{action}: {content[:50]}..." if len(content) > 50 else f"{action}: {content}"
        
        notification_data = {
            "board_id": board_id,
            "action": action,
            "board_title": board['title'],
            "url": f"/board/{board_id}"
        }
        
        success_count = 0
        for member in board.get('members', []):
            if member != exclude_user:
                if send_push_notification(member, title, body, notification_data, dm):
                    success_count += 1
        
        logger.info(f"Sent board notifications to {success_count} members for board {board_id}")
        return success_count > 0
        
    except Exception as e:
        logger.error(f"Error sending board notification for {board_id}: {e}")
        return False

def send_reminder_notification(user_email, reminder_title, reminder_time, dm=None):
    """Send notification for upcoming reminder"""
    if not dm:
        return False
        
    title = "⏰ Påminnelse"
    body = f"{reminder_title} - {reminder_time}"
    
    notification_data = {
        "type": "reminder",
        "title": reminder_title,
        "time": reminder_time,
        "url": "/dashboard"
    }
    
    return send_push_notification(user_email, title, body, notification_data, dm)

def subscribe_user_to_push(user_email, subscription_data, dm=None):
    """Subscribe user to push notifications"""
    if not dm:
        return False
        
    try:
        subscriptions = dm.load_data('push_subscriptions')
        
        if user_email not in subscriptions:
            subscriptions[user_email] = []
        
        # Check if subscription already exists
        existing = False
        for sub in subscriptions[user_email]:
            if sub.get('endpoint') == subscription_data.get('endpoint'):
                existing = True
                break
        
        if not existing:
            # Add timestamp to subscription
            subscription_data['subscribed_at'] = datetime.now().isoformat()
            subscriptions[user_email].append(subscription_data)
            dm.save_data('push_subscriptions', subscriptions)
            logger.info(f"Added push subscription for {user_email}")
            return True
        else:
            logger.info(f"Push subscription already exists for {user_email}")
            return True
            
    except Exception as e:
        logger.error(f"Error subscribing user {user_email} to push notifications: {e}")
        return False

def get_user_subscriptions(user_email, dm=None):
    """Get all push subscriptions for a user"""
    if not dm:
        return []
        
    try:
        subscriptions = dm.load_data('push_subscriptions')
        return subscriptions.get(user_email, [])
    except Exception as e:
        logger.error(f"Error getting subscriptions for {user_email}: {e}")
        return []

def unsubscribe_user_from_push(user_email, endpoint, dm=None):
    """Unsubscribe user from push notifications"""
    if not dm:
        return False
        
    try:
        subscriptions = dm.load_data('push_subscriptions')
        user_subs = subscriptions.get(user_email, [])
        
        # Remove subscription with matching endpoint
        updated_subs = [sub for sub in user_subs if sub.get('endpoint') != endpoint]
        
        if len(updated_subs) != len(user_subs):
            subscriptions[user_email] = updated_subs
            dm.save_data('push_subscriptions', subscriptions)
            logger.info(f"Removed push subscription for {user_email}")
            return True
        else:
            logger.warning(f"No matching subscription found for {user_email}")
            return False
            
    except Exception as e:
        logger.error(f"Error unsubscribing user {user_email}: {e}")
        return False
