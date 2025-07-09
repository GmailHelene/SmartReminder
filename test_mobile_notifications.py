import requests
import json
import sys
import os

# Add the app directory to Python path
sys.path.insert(0, '/workspaces/smartreminder')

from app import app

def test_mobile_notification_features():
    """Test mobile-specific notification features"""
    
    print("🧪 Testing mobile notification features...")
    
    # Test 1: Check if sound files are accessible
    print("\n🔊 Testing sound file access...")
    sounds = ['pristine.mp3', 'ding.mp3', 'chime.mp3', 'alert.mp3']
    for sound in sounds:
        sound_path = f'/workspaces/smartreminder/static/sounds/{sound}'
        if os.path.exists(sound_path):
            print(f"   ✅ {sound} accessible")
        else:
            print(f"   ❌ {sound} missing")
    
    # Test 2: Check service worker registration
    print("\n🔄 Testing service worker...")
    sw_path = '/workspaces/smartreminder/static/sw.js'
    if os.path.exists(sw_path):
        print("   ✅ Service worker file exists")
        
        # Check for notification handling
        with open(sw_path, 'r') as f:
            sw_content = f.read()
            
        if "'push'" in sw_content:
            print("   ✅ Push event listener found")
        else:
            print("   ❌ Push event listener missing")
            
        if "showNotification" in sw_content:
            print("   ✅ Notification display found")
        else:
            print("   ❌ Notification display missing")
            
        if "vibrate" in sw_content:
            print("   ✅ Vibration support found")
        else:
            print("   ❌ Vibration support missing")
    
    # Test 3: Check app.js for mobile-specific features
    print("\n📱 Testing app.js mobile features...")
    app_js_path = '/workspaces/smartreminder/static/js/app.js'
    if os.path.exists(app_js_path):
        with open(app_js_path, 'r') as f:
            app_content = f.read()
            
        # Check for mobile-specific features
        mobile_features = [
            ("Audio autoplay handling", "userInteracted"),
            ("Vibration fallback", "navigator.vibrate"),
            ("Touch event handling", "ontouchstart"),
            ("Manual sound button", "play-sound-button"),
            ("Service worker messages", "postMessage"),
            ("Notification permission", "Notification.requestPermission")
        ]
        
        for feature, keyword in mobile_features:
            if keyword in app_content:
                print(f"   ✅ {feature} found")
            else:
                print(f"   ❌ {feature} missing")
    
    # Test 4: Check manifest.json for PWA features
    print("\n📋 Testing PWA manifest...")
    manifest_path = '/workspaces/smartreminder/static/manifest.json'
    if os.path.exists(manifest_path):
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
            
        required_fields = ['name', 'short_name', 'start_url', 'display', 'background_color', 'theme_color']
        for field in required_fields:
            if field in manifest:
                print(f"   ✅ {field}: {manifest[field]}")
            else:
                print(f"   ❌ {field} missing")
                
        # Check icons
        if 'icons' in manifest and len(manifest['icons']) > 0:
            print(f"   ✅ Icons: {len(manifest['icons'])} found")
        else:
            print("   ❌ Icons missing")
    
    # Test 5: Check for iOS-specific features
    print("\n🍎 Testing iOS compatibility...")
    with open('/workspaces/smartreminder/templates/base.html', 'r') as f:
        base_content = f.read()
        
    ios_features = [
        ("Apple touch icon", "apple-touch-icon"),
        ("Apple mobile web app", "apple-mobile-web-app"),
        ("Viewport meta tag", "viewport"),
        ("Status bar style", "status-bar-style")
    ]
    
    for feature, keyword in ios_features:
        if keyword in base_content:
            print(f"   ✅ {feature} found")
        else:
            print(f"   ❌ {feature} missing")
    
    print("\n🎉 Mobile notification test completed!")

if __name__ == "__main__":
    test_mobile_notification_features()
