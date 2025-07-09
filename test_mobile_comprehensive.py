#!/usr/bin/env python3
"""
Comprehensive Mobile Notification Test
Tests all aspects of mobile notifications including PWA, push, sound, and fallbacks
"""

import os
import sys
import json
import time
import requests
from datetime import datetime, timedelta

# Add the app directory to Python path
sys.path.insert(0, '/workspaces/smartreminder')

from app import app, dm
from push_service import send_push_notification

def test_mobile_pwa_features():
    """Test PWA features for mobile"""
    print("📱 Testing PWA features for mobile...")
    
    # Test manifest.json
    manifest_path = '/workspaces/smartreminder/static/manifest.json'
    if os.path.exists(manifest_path):
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        
        required_fields = {
            'name': 'SmartReminder Pro',
            'short_name': 'SmartReminder',
            'start_url': '/',
            'display': 'standalone',
            'background_color': '#007bff',
            'theme_color': '#007bff'
        }
        
        for field, expected in required_fields.items():
            if field in manifest and manifest[field] == expected:
                print(f"   ✅ {field}: {manifest[field]}")
            else:
                print(f"   ❌ {field}: expected '{expected}', got '{manifest.get(field)}'")
        
        # Check icons
        if 'icons' in manifest and len(manifest['icons']) >= 2:
            print(f"   ✅ Icons: {len(manifest['icons'])} found")
        else:
            print(f"   ❌ Icons: insufficient icons")
    else:
        print("   ❌ manifest.json not found")

def test_mobile_service_worker():
    """Test service worker for mobile features"""
    print("\n🔄 Testing service worker for mobile...")
    
    sw_path = '/workspaces/smartreminder/static/sw.js'
    if os.path.exists(sw_path):
        with open(sw_path, 'r') as f:
            sw_content = f.read()
        
        mobile_features = [
            ("Push event listener", "addEventListener('push'"),
            ("Notification display", "showNotification"),
            ("Vibration support", "vibrate"),
            ("Notification actions", "actions"),
            ("Mobile-optimized options", "requireInteraction"),
            ("Enhanced fallback", "pending-sounds"),
            ("Client messaging", "postMessage"),
            ("Notification click handling", "notificationclick")
        ]
        
        for feature, keyword in mobile_features:
            if keyword in sw_content:
                print(f"   ✅ {feature} found")
            else:
                print(f"   ❌ {feature} missing")
    else:
        print("   ❌ Service worker not found")

def test_mobile_app_js():
    """Test app.js for mobile features"""
    print("\n📲 Testing app.js for mobile...")
    
    app_js_path = '/workspaces/smartreminder/static/js/app.js'
    if os.path.exists(app_js_path):
        with open(app_js_path, 'r') as f:
            app_content = f.read()
        
        mobile_features = [
            ("Mobile device detection", "isMobileDevice"),
            ("Enhanced sound playback", "playNotificationSound"),
            ("Mobile notification button", "showMobileNotificationButton"),
            ("Vibration fallback", "navigator.vibrate"),
            ("Touch event handling", "ontouchstart"),
            ("Service worker messaging", "addEventListener('message'"),
            ("Permission handling", "requestNotificationPermissionWithFallback"),
            ("Push subscription", "initializePushNotifications")
        ]
        
        for feature, keyword in mobile_features:
            if keyword in app_content:
                print(f"   ✅ {feature} found")
            else:
                print(f"   ❌ {feature} missing")
    else:
        print("   ❌ app.js not found")

def test_mobile_pwa_js():
    """Test PWA.js for mobile features"""
    print("\n🔧 Testing PWA.js for mobile...")
    
    pwa_js_path = '/workspaces/smartreminder/static/js/pwa.js'
    if os.path.exists(pwa_js_path):
        with open(pwa_js_path, 'r') as f:
            pwa_content = f.read()
        
        pwa_features = [
            ("Mobile installability check", "checkMobileInstallability"),
            ("iOS install instructions", "showIOSInstallInstructions"),
            ("Android install handling", "handleAndroidInstall"),
            ("Enhanced notifications", "requestNotificationPermissionForPWA"),
            ("Install prompt handling", "beforeinstallprompt"),
            ("App installed event", "appinstalled"),
            ("Service worker registration", "serviceWorker.register")
        ]
        
        for feature, keyword in pwa_features:
            if keyword in pwa_content:
                print(f"   ✅ {feature} found")
            else:
                print(f"   ❌ {feature} missing")
    else:
        print("   ❌ pwa.js not found")

def test_sound_files():
    """Test sound files for mobile"""
    print("\n🔊 Testing sound files for mobile...")
    
    sounds_dir = '/workspaces/smartreminder/static/sounds'
    if os.path.exists(sounds_dir):
        sound_files = ['pristine.mp3', 'ding.mp3', 'chime.mp3', 'alert.mp3']
        
        for sound_file in sound_files:
            sound_path = os.path.join(sounds_dir, sound_file)
            if os.path.exists(sound_path):
                file_size = os.path.getsize(sound_path)
                print(f"   ✅ {sound_file}: {file_size} bytes")
            else:
                print(f"   ❌ {sound_file}: missing")
    else:
        print("   ❌ Sounds directory not found")

def test_base_template():
    """Test base template for mobile PWA features"""
    print("\n📄 Testing base template for mobile...")
    
    base_path = '/workspaces/smartreminder/templates/base.html'
    if os.path.exists(base_path):
        with open(base_path, 'r') as f:
            base_content = f.read()
        
        mobile_features = [
            ("Viewport meta tag", "user-scalable=no"),
            ("PWA manifest", "manifest.json"),
            ("Apple touch icon", "apple-touch-icon"),
            ("Apple mobile web app", "apple-mobile-web-app-capable"),
            ("Theme color", "theme-color"),
            ("Install button", "installBtn"),
            ("Mobile web app title", "apple-mobile-web-app-title")
        ]
        
        for feature, keyword in mobile_features:
            if keyword in base_content:
                print(f"   ✅ {feature} found")
            else:
                print(f"   ❌ {feature} missing")
    else:
        print("   ❌ base.html not found")

def test_push_service():
    """Test push service for mobile optimizations"""
    print("\n🔔 Testing push service for mobile...")
    
    push_path = '/workspaces/smartreminder/push_service.py'
    if os.path.exists(push_path):
        with open(push_path, 'r') as f:
            push_content = f.read()
        
        mobile_features = [
            ("Enhanced vibration", "vibrate"),
            ("Require interaction", "requireInteraction"),
            ("Mobile actions", "actions"),
            ("Sound handling", "sound"),
            ("Badge support", "badge"),
            ("Priority handling", "priority"),
            ("Notification tag", "tag"),
            ("Renotify support", "renotify")
        ]
        
        for feature, keyword in mobile_features:
            if keyword in push_content:
                print(f"   ✅ {feature} found")
            else:
                print(f"   ❌ {feature} missing")
    else:
        print("   ❌ push_service.py not found")

def test_mobile_notification_flow():
    """Test the complete mobile notification flow"""
    print("\n🔄 Testing complete mobile notification flow...")
    
    # Check if all components are in place
    components = [
        ('/workspaces/smartreminder/static/sw.js', 'Service Worker'),
        ('/workspaces/smartreminder/static/js/app.js', 'App JavaScript'),
        ('/workspaces/smartreminder/static/js/pwa.js', 'PWA JavaScript'),
        ('/workspaces/smartreminder/push_service.py', 'Push Service'),
        ('/workspaces/smartreminder/static/manifest.json', 'PWA Manifest'),
        ('/workspaces/smartreminder/templates/base.html', 'Base Template')
    ]
    
    all_present = True
    for path, name in components:
        if os.path.exists(path):
            print(f"   ✅ {name}: Present")
        else:
            print(f"   ❌ {name}: Missing")
            all_present = False
    
    if all_present:
        print("   ✅ All components present for mobile notification flow")
    else:
        print("   ❌ Some components missing")

def main():
    """Run all mobile tests"""
    print("🚀 Starting Comprehensive Mobile Notification Test")
    print("=" * 60)
    
    test_mobile_pwa_features()
    test_mobile_service_worker()
    test_mobile_app_js()
    test_mobile_pwa_js()
    test_sound_files()
    test_base_template()
    test_push_service()
    test_mobile_notification_flow()
    
    print("\n" + "=" * 60)
    print("✅ Mobile notification comprehensive test completed!")
    print("\n📋 Next steps for mobile testing:")
    print("1. Test PWA installation on real mobile devices")
    print("2. Test push notifications with screen off")
    print("3. Test sound playback on iOS/Android")
    print("4. Test notification permissions and fallbacks")
    print("5. Test offline functionality")

if __name__ == "__main__":
    main()
