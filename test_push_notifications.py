#!/usr/bin/env python3
"""
Test Push Notifications System
Diagnose why mobile push notifications with sound are not being received
"""

import json
import requests
import logging
from datetime import datetime, timedelta
import sys
import os

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_vapid_key_endpoint():
    """Test if VAPID public key endpoint is working"""
    try:
        response = requests.get('http://localhost:5000/api/vapid-public-key')
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✅ VAPID endpoint working: {data}")
            return data.get('public_key')
        else:
            logger.error(f"❌ VAPID endpoint failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logger.error(f"❌ Error testing VAPID endpoint: {e}")
        return None

def test_push_subscription_storage():
    """Check if push subscriptions are being stored"""
    try:
        with open('data/push_subscriptions.json', 'r') as f:
            subscriptions = json.load(f)
        
        logger.info(f"📄 Push subscriptions file content:")
        for email, subs in subscriptions.items():
            logger.info(f"  - {email}: {len(subs) if isinstance(subs, list) else 'invalid format'} subscriptions")
        
        return subscriptions
    except FileNotFoundError:
        logger.warning("⚠️ Push subscriptions file not found")
        return {}
    except Exception as e:
        logger.error(f"❌ Error reading push subscriptions: {e}")
        return {}

def test_push_service_import():
    """Test if push service can be imported and used"""
    try:
        from push_service import send_push_notification, get_vapid_public_key
        
        # Test VAPID key
        vapid_key = get_vapid_public_key()
        logger.info(f"✅ Push service imported successfully")
        logger.info(f"📱 VAPID public key: {vapid_key[:50]}...")
        
        return True
    except Exception as e:
        logger.error(f"❌ Error importing push service: {e}")
        return False

def test_notification_scheduling():
    """Check if reminders are scheduled to send notifications"""
    try:
        # Import data manager
        sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
        from models import data_manager as dm
        
        # Get recent reminders
        reminders = dm.load_data('reminders', [])
        now = datetime.now()
        
        # Find reminders that should have triggered notifications
        recent_reminders = []
        for reminder in reminders:
            try:
                reminder_time = datetime.fromisoformat(reminder['datetime'])
                if now - timedelta(hours=1) <= reminder_time <= now + timedelta(hours=1):
                    recent_reminders.append(reminder)
            except:
                continue
        
        logger.info(f"🕐 Found {len(recent_reminders)} reminders in the last/next hour")
        for reminder in recent_reminders:
            logger.info(f"  - {reminder.get('title', 'No title')} at {reminder.get('datetime', 'No time')}")
            logger.info(f"    Notification: {reminder.get('notification', False)}")
            logger.info(f"    Sound: {reminder.get('sound', 'No sound')}")
        
        return recent_reminders
    except Exception as e:
        logger.error(f"❌ Error checking reminder scheduling: {e}")
        return []

def test_service_worker():
    """Test if service worker is accessible"""
    try:
        response = requests.get('http://localhost:5000/sw.js')
        if response.status_code == 200:
            content = response.text
            
            # Check for push event handler
            if 'addEventListener(\'push\'' in content:
                logger.info("✅ Service worker has push event handler")
            else:
                logger.warning("⚠️ Service worker missing push event handler")
            
            # Check for sound handling
            if 'playNotificationSound' in content:
                logger.info("✅ Service worker has sound handling")
            else:
                logger.warning("⚠️ Service worker missing sound handling")
            
            return True
        else:
            logger.error(f"❌ Service worker not accessible: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ Error testing service worker: {e}")
        return False

def check_app_logs():
    """Check application logs for notification errors"""
    try:
        if os.path.exists('app.log'):
            with open('app.log', 'r') as f:
                lines = f.readlines()
            
            # Look for notification-related log entries
            notification_logs = []
            for line in lines[-100:]:  # Last 100 lines
                if any(keyword in line.lower() for keyword in ['notification', 'push', 'reminder', 'vapid']):
                    notification_logs.append(line.strip())
            
            logger.info(f"📋 Recent notification logs ({len(notification_logs)} entries):")
            for log in notification_logs[-10:]:  # Last 10 relevant logs
                logger.info(f"  {log}")
                
            return notification_logs
        else:
            logger.warning("⚠️ App log file not found")
            return []
    except Exception as e:
        logger.error(f"❌ Error reading app logs: {e}")
        return []

def main():
    logger.info("🔍 Starting Push Notification Diagnosis")
    logger.info("=" * 50)
    
    # Test 1: VAPID endpoint
    logger.info("\n1. Testing VAPID endpoint...")
    vapid_key = test_vapid_key_endpoint()
    
    # Test 2: Push service import
    logger.info("\n2. Testing push service...")
    push_service_ok = test_push_service_import()
    
    # Test 3: Push subscriptions
    logger.info("\n3. Checking push subscriptions...")
    subscriptions = test_push_subscription_storage()
    
    # Test 4: Service worker
    logger.info("\n4. Testing service worker...")
    sw_ok = test_service_worker()
    
    # Test 5: Reminder scheduling
    logger.info("\n5. Checking reminder scheduling...")
    recent_reminders = test_notification_scheduling()
    
    # Test 6: App logs
    logger.info("\n6. Checking app logs...")
    logs = check_app_logs()
    
    # Summary
    logger.info("\n" + "=" * 50)
    logger.info("🔍 DIAGNOSIS SUMMARY")
    logger.info("=" * 50)
    
    issues = []
    
    if not vapid_key:
        issues.append("❌ VAPID endpoint not working")
    
    if not push_service_ok:
        issues.append("❌ Push service not working")
    
    if not subscriptions:
        issues.append("⚠️ No push subscriptions found")
    
    if not sw_ok:
        issues.append("❌ Service worker issues")
    
    if not recent_reminders:
        issues.append("ℹ️ No recent reminders to test with")
    
    if issues:
        logger.info("🚨 POTENTIAL ISSUES FOUND:")
        for issue in issues:
            logger.info(f"  {issue}")
    else:
        logger.info("✅ All basic tests passed!")
    
    logger.info("\n🔧 RECOMMENDATIONS:")
    
    if not subscriptions:
        logger.info("  1. Users need to enable push notifications in the web app")
        logger.info("  2. Check that the dashboard loads the VAPID key correctly")
    
    if not vapid_key:
        logger.info("  1. Check if Flask app is running")
        logger.info("  2. Verify VAPID keys are configured correctly")
    
    logger.info("  3. Test with a real reminder set for the next few minutes")
    logger.info("  4. Check browser developer tools for JavaScript errors")

if __name__ == "__main__":
    main()
