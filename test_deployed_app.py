#!/usr/bin/env python3
"""Final comprehensive test of SmartReminder fixes"""

import requests
import time

def test_deployed_app():
    """Test the deployed Railway app"""
    base_url = "https://smartremind-production.up.railway.app"
    
    print("🧪 Testing deployed SmartReminder app...")
    
    try:
        # Test main page
        print("🔍 Testing main page...")
        response = requests.get(base_url, timeout=10)
        if response.status_code == 200:
            print("✅ Main page loads successfully!")
            if 'SmartReminder' in response.text:
                print("✅ App name updated correctly!")
        else:
            print(f"❌ Main page failed: {response.status_code}")
        
        # Test email settings page (should redirect to login)
        print("\n🔍 Testing email settings page...")
        response = requests.get(f"{base_url}/email-settings", timeout=10, allow_redirects=False)
        if response.status_code in [302, 401]:
            print("✅ Email settings properly requires authentication!")
        elif response.status_code == 200:
            print("⚠️ Email settings accessible without login (unexpected)")
        else:
            print(f"❌ Email settings failed: {response.status_code}")
        
        # Test static files
        print("\n🔍 Testing static files...")
        manifest_response = requests.get(f"{base_url}/static/manifest.json", timeout=10)
        if manifest_response.status_code == 200:
            print("✅ Manifest file accessible!")
            manifest_data = manifest_response.json()
            if 'SmartReminder' in manifest_data.get('name', ''):
                print("✅ PWA name updated in manifest!")
        else:
            print(f"❌ Manifest file failed: {manifest_response.status_code}")
        
        print("\n🎉 Deployed app test completed!")
        
    except Exception as e:
        print(f"❌ Error testing deployed app: {e}")

if __name__ == "__main__":
    test_deployed_app()
