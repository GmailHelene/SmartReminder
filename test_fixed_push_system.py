#!/usr/bin/env python3
"""
Test the fixed push notification subscription with VAPID key
"""

import json
import requests
import time

def test_vapid_endpoint():
    """Test the VAPID key endpoint"""
    try:
        response = requests.get('http://localhost:5000/api/vapid-public-key')
        if response.status_code == 200:
            data = response.json()
            print(f"✅ VAPID endpoint working")
            print(f"📱 Public key: {data['public_key']}")
            return data['public_key']
        else:
            print(f"❌ VAPID endpoint failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_push_subscription_endpoint():
    """Test the push subscription endpoint"""
    try:
        # Mock subscription data (this would normally come from the browser)
        mock_subscription = {
            "endpoint": "https://fcm.googleapis.com/fcm/send/test",
            "keys": {
                "p256dh": "test_p256dh_key",
                "auth": "test_auth_key"
            }
        }
        
        response = requests.post('http://localhost:5000/api/push-subscription', 
                               json={'subscription': mock_subscription})
        
        if response.status_code == 200:
            print("✅ Push subscription endpoint working")
            return True
        else:
            print(f"❌ Push subscription failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error testing push subscription: {e}")
        return False

def main():
    print("🧪 Testing Fixed Push Notification System")
    print("=" * 50)
    
    # Test VAPID endpoint
    print("\n1. Testing VAPID key endpoint...")
    vapid_key = test_vapid_endpoint()
    
    # Test push subscription endpoint
    print("\n2. Testing push subscription endpoint...")
    subscription_ok = test_push_subscription_endpoint()
    
    print("\n" + "=" * 50)
    print("📋 TEST SUMMARY")
    print("=" * 50)
    
    if vapid_key and subscription_ok:
        print("✅ All endpoints working correctly!")
        print("\n🔧 NEXT STEPS:")
        print("1. Open the web app in a browser")
        print("2. Click on push notification enable button") 
        print("3. Accept notification permission")
        print("4. Run: python3 create_test_push_reminder.py")
        print("5. Wait 2 minutes for the test notification")
        print("\n💡 The notification should now include sound because:")
        print("   - VAPID key is properly configured")
        print("   - Service worker handles sound playback")
        print("   - Push subscription uses correct applicationServerKey")
    else:
        print("❌ Some tests failed - check the logs above")

if __name__ == "__main__":
    main()
