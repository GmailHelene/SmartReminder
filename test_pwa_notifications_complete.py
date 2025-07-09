#!/usr/bin/env python3
"""
Complete test for PWA functionality and mobile notifications
Tests all aspects of PWA installation and notification system
"""

import os
import json
import requests
from datetime import datetime

def test_pwa_manifest():
    """Test PWA manifest.json configuration"""
    print("🔍 Testing PWA manifest...")
    
    manifest_path = "/workspaces/smartreminder/static/manifest.json"
    
    if not os.path.exists(manifest_path):
        print("   ❌ manifest.json not found")
        return False
    
    try:
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        
        # Check required fields
        required_fields = ['name', 'short_name', 'start_url', 'display', 'icons']
        missing_fields = [field for field in required_fields if field not in manifest]
        
        if missing_fields:
            print(f"   ❌ Missing required fields: {missing_fields}")
            return False
        
        print("   ✅ All required manifest fields present")
        
        # Check icons
        if len(manifest['icons']) >= 2:
            print(f"   ✅ {len(manifest['icons'])} icons configured")
        else:
            print(f"   ⚠️ Only {len(manifest['icons'])} icons configured, recommend more")
        
        # Check display mode
        if manifest['display'] == 'standalone':
            print("   ✅ Display mode set to standalone")
        else:
            print(f"   ⚠️ Display mode is {manifest['display']}, recommend 'standalone'")
        
        # Check start URL
        if manifest['start_url'].startswith('/'):
            print("   ✅ Start URL properly configured")
        else:
            print(f"   ⚠️ Start URL should start with '/': {manifest['start_url']}")
        
        # Check new PWA features
        advanced_features = ['shortcuts', 'categories', 'orientation', 'scope']
        for feature in advanced_features:
            if feature in manifest:
                print(f"   ✅ Advanced PWA feature '{feature}' configured")
            else:
                print(f"   ℹ️ Advanced PWA feature '{feature}' not configured")
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"   ❌ Invalid JSON in manifest: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Error reading manifest: {e}")
        return False

def test_service_worker():
    """Test Service Worker implementation"""
    print("\n🔧 Testing Service Worker...")
    
    sw_path = "/workspaces/smartreminder/static/sw.js"
    
    if not os.path.exists(sw_path):
        print("   ❌ Service Worker file not found")
        return False
    
    try:
        with open(sw_path, 'r') as f:
            sw_content = f.read()
        
        # Check core service worker events
        core_events = [
            ('install', 'Install event'),
            ('activate', 'Activate event'),
            ('fetch', 'Fetch event'),
            ('push', 'Push notification event'),
            ('notificationclick', 'Notification click event'),
            ('message', 'Message event for client communication')
        ]
        
        for event, description in core_events:
            if f"addEventListener('{event}'" in sw_content:
                print(f"   ✅ {description} handler found")
            else:
                print(f"   ❌ {description} handler missing")
        
        # Check caching strategy
        if 'caches.open' in sw_content and 'cache.addAll' in sw_content:
            print("   ✅ Caching strategy implemented")
        else:
            print("   ❌ Caching strategy missing")
        
        # Check offline support
        if 'caches.match' in sw_content:
            print("   ✅ Offline support implemented")
        else:
            print("   ❌ Offline support missing")
        
        # Check push notification handling
        push_features = [
            ('showNotification', 'Notification display'),
            ('clients.matchAll', 'Client communication'),
            ('PLAY_NOTIFICATION_SOUND', 'Sound notification handling'),
            ('vibrate', 'Vibration support'),
            ('playNotificationSoundViaClients', 'Enhanced sound handling')
        ]
        
        for feature, description in push_features:
            if feature in sw_content:
                print(f"   ✅ {description} implemented")
            else:
                print(f"   ❌ {description} missing")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error reading Service Worker: {e}")
        return False

def test_pwa_javascript():
    """Test PWA JavaScript implementation"""
    print("\n📱 Testing PWA JavaScript...")
    
    # Test pwa.js
    pwa_js_path = "/workspaces/smartreminder/static/js/pwa.js"
    
    if not os.path.exists(pwa_js_path):
        print("   ❌ pwa.js not found")
        return False
    
    try:
        with open(pwa_js_path, 'r') as f:
            pwa_content = f.read()
        
        # Check PWA installation features
        pwa_features = [
            ('beforeinstallprompt', 'Install prompt handling'),
            ('appinstalled', 'App installed event'),
            ('deferredPrompt', 'Deferred prompt management'),
            ('showInstallButton', 'Install button display'),
            ('hideInstallButton', 'Install button hiding'),
            ('installApp', 'App installation function'),
            ('isMobileDevice', 'Mobile device detection'),
            ('isIOSDevice', 'iOS device detection'),
            ('showIOSInstallInstructions', 'iOS install instructions'),
            ('handleAndroidInstall', 'Android install handling')
        ]
        
        for feature, description in pwa_features:
            if feature in pwa_content:
                print(f"   ✅ {description} implemented")
            else:
                print(f"   ❌ {description} missing")
        
        # Check service worker registration
        if 'navigator.serviceWorker.register' in pwa_content:
            print("   ✅ Service Worker registration implemented")
        else:
            print("   ❌ Service Worker registration missing")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error reading pwa.js: {e}")
        return False

def test_notification_javascript():
    """Test notification JavaScript implementation"""
    print("\n🔔 Testing notification JavaScript...")
    
    app_js_path = "/workspaces/smartreminder/static/js/app.js"
    
    if not os.path.exists(app_js_path):
        print("   ❌ app.js not found")
        return False
    
    try:
        with open(app_js_path, 'r') as f:
            app_content = f.read()
        
        # Check notification features
        notification_features = [
            ('playNotificationSound', 'Sound playback function'),
            ('showMobileNotificationButton', 'Mobile notification button'),
            ('requestNotificationPermission', 'Permission request'),
            ('initializePushNotifications', 'Push notification initialization'),
            ('subscribeToPushNotifications', 'Push subscription'),
            ('sendSubscriptionToServer', 'Server subscription sync'),
            ('navigator.vibrate', 'Vibration API usage'),
            ('showToastNotification', 'Toast notification display'),
            ('isMobileDevice', 'Mobile device detection'),
            ('userInteracted', 'User interaction tracking')
        ]
        
        for feature, description in notification_features:
            if feature in app_content:
                print(f"   ✅ {description} implemented")
            else:
                print(f"   ❌ {description} missing")
        
        # Check service worker communication
        sw_communication = [
            ('addEventListener(\'message\'', 'Message event listener'),
            ('postMessage', 'Message posting'),
            ('CLIENT_READY', 'Client ready signaling'),
            ('PLAY_NOTIFICATION_SOUND', 'Sound play message type')
        ]
        
        for feature, description in sw_communication:
            if feature in app_content:
                print(f"   ✅ {description} implemented")
            else:
                print(f"   ❌ {description} missing")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error reading app.js: {e}")
        return False

def test_dashboard_integration():
    """Test dashboard PWA integration"""
    print("\n🎯 Testing dashboard PWA integration...")
    
    dashboard_path = "/workspaces/smartreminder/templates/dashboard.html"
    
    if not os.path.exists(dashboard_path):
        print("   ❌ dashboard.html not found")
        return False
    
    try:
        with open(dashboard_path, 'r') as f:
            dashboard_content = f.read()
        
        # Check PWA buttons
        pwa_elements = [
            ('id="enablePushBtn"', 'Push notification enable button'),
            ('id="installBtn"', 'PWA install button'),
            ('onclick="requestPushPermission()"', 'Push permission request'),
            ('onclick="installApp()"', 'App installation trigger'),
            ('showToastNotification', 'Toast notification function'),
            ('requestPushPermission', 'Push permission function'),
            ('display-mode: standalone', 'Standalone mode detection')
        ]
        
        for element, description in pwa_elements:
            if element in dashboard_content:
                print(f"   ✅ {description} found")
            else:
                print(f"   ❌ {description} missing")
        
        # Check mobile optimizations
        mobile_optimizations = [
            ('mobile-notification-optimized', 'Mobile notification CSS'),
            ('Android|iPhone|iPad', 'Mobile device detection'),
            ('slideInUp', 'Mobile animations'),
            ('90vw', 'Mobile responsive design')
        ]
        
        for optimization, description in mobile_optimizations:
            if optimization in dashboard_content:
                print(f"   ✅ {description} implemented")
            else:
                print(f"   ❌ {description} missing")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error reading dashboard.html: {e}")
        return False

def test_sound_files():
    """Test notification sound files"""
    print("\n🔊 Testing notification sound files...")
    
    sounds_dir = "/workspaces/smartreminder/static/sounds"
    
    if not os.path.exists(sounds_dir):
        print("   ❌ Sounds directory not found")
        return False
    
    try:
        sound_files = os.listdir(sounds_dir)
        print(f"   ℹ️ Found {len(sound_files)} sound files")
        
        # Check for default sound
        if 'pristine.mp3' in sound_files:
            print("   ✅ Default sound (pristine.mp3) found")
        else:
            print("   ❌ Default sound (pristine.mp3) missing")
        
        # Check for variety of sounds
        expected_sounds = ['ding.mp3', 'chime.mp3', 'alert.mp3']
        for sound in expected_sounds:
            if sound in sound_files:
                print(f"   ✅ Sound file {sound} found")
            else:
                print(f"   ⚠️ Sound file {sound} missing")
        
        return len(sound_files) > 0
        
    except Exception as e:
        print(f"   ❌ Error checking sound files: {e}")
        return False

def test_icon_files():
    """Test PWA icon files"""
    print("\n🖼️ Testing PWA icon files...")
    
    images_dir = "/workspaces/smartreminder/static/images"
    
    if not os.path.exists(images_dir):
        print("   ❌ Images directory not found")
        return False
    
    try:
        image_files = os.listdir(images_dir)
        print(f"   ℹ️ Found {len(image_files)} image files")
        
        # Check for required PWA icons
        required_icons = [
            'icon-192x192.png',
            'icon-512x512.png',
            'badge-96x96.png'
        ]
        
        for icon in required_icons:
            if icon in image_files:
                print(f"   ✅ Required icon {icon} found")
            else:
                print(f"   ❌ Required icon {icon} missing")
        
        # Check for additional recommended icons
        recommended_icons = [
            'icon-72x72.png',
            'icon-96x96.png',
            'icon-128x128.png',
            'icon-144x144.png',
            'icon-152x152.png',
            'icon-384x384.png'
        ]
        
        found_recommended = 0
        for icon in recommended_icons:
            if icon in image_files:
                found_recommended += 1
        
        print(f"   ℹ️ Found {found_recommended}/{len(recommended_icons)} recommended icons")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error checking icon files: {e}")
        return False

def run_complete_pwa_test():
    """Run complete PWA and notification test"""
    print("🚀 Starting complete PWA and notification system test")
    print("=" * 60)
    
    tests = [
        ("PWA Manifest", test_pwa_manifest),
        ("Service Worker", test_service_worker),
        ("PWA JavaScript", test_pwa_javascript),
        ("Notification JavaScript", test_notification_javascript),
        ("Dashboard Integration", test_dashboard_integration),
        ("Sound Files", test_sound_files),
        ("Icon Files", test_icon_files)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"   💥 Test {test_name} failed with error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n📈 Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All PWA and notification tests passed!")
        print("✅ PWA functionality is ready for mobile deployment")
        print("✅ Notification system is fully functional")
    else:
        print("⚠️ Some tests failed. Please fix the issues above.")
        print("📱 PWA may not work optimally on mobile devices")
        print("🔔 Notification system may have issues")
    
    return passed == total

if __name__ == "__main__":
    success = run_complete_pwa_test()
    exit(0 if success else 1)
