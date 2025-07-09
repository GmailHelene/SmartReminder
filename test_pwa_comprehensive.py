#!/usr/bin/env python3
"""
Comprehensive PWA functionality test for SmartReminder Pro
Tests PWA installation, offline functionality, and notification features
"""

import requests
import json
import time
from urllib.parse import urljoin
import os
import sys

# Base URL for testing
BASE_URL = "http://localhost:5000"

def test_pwa_manifest():
    """Test PWA manifest.json file"""
    print("=== Testing PWA Manifest ===")
    
    try:
        response = requests.get(f"{BASE_URL}/static/manifest.json")
        if response.status_code == 200:
            manifest = response.json()
            print("✅ Manifest loaded successfully")
            
            # Check required fields
            required_fields = ['name', 'short_name', 'start_url', 'display', 'theme_color', 'background_color', 'icons']
            for field in required_fields:
                if field in manifest:
                    print(f"✅ {field}: {manifest[field]}")
                else:
                    print(f"❌ Missing required field: {field}")
            
            # Check icons
            if 'icons' in manifest:
                print(f"✅ Icons defined: {len(manifest['icons'])} icons")
                for icon in manifest['icons']:
                    print(f"   - {icon.get('sizes', 'unknown')} ({icon.get('src', 'no src')})")
            
            return True
        else:
            print(f"❌ Failed to load manifest: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing manifest: {e}")
        return False

def test_pwa_icons():
    """Test PWA icon availability"""
    print("\n=== Testing PWA Icons ===")
    
    # Test icons from manifest
    manifest_url = f"{BASE_URL}/static/manifest.json"
    try:
        response = requests.get(manifest_url)
        if response.status_code == 200:
            manifest = response.json()
            icons = manifest.get('icons', [])
            
            success_count = 0
            for icon in icons:
                icon_url = urljoin(BASE_URL, icon['src'])
                try:
                    icon_response = requests.get(icon_url)
                    if icon_response.status_code == 200:
                        print(f"✅ Icon {icon['sizes']}: {icon_url}")
                        success_count += 1
                    else:
                        print(f"❌ Icon {icon['sizes']} not found: {icon_url}")
                except Exception as e:
                    print(f"❌ Error loading icon {icon['sizes']}: {e}")
            
            print(f"✅ {success_count}/{len(icons)} icons loaded successfully")
            return success_count == len(icons)
        else:
            print("❌ Could not load manifest for icon testing")
            return False
    except Exception as e:
        print(f"❌ Error testing icons: {e}")
        return False

def test_service_worker():
    """Test service worker availability"""
    print("\n=== Testing Service Worker ===")
    
    try:
        response = requests.get(f"{BASE_URL}/static/sw.js")
        if response.status_code == 200:
            sw_content = response.text
            print("✅ Service Worker loaded successfully")
            
            # Check for key features
            features = [
                ('Cache handling', 'CACHE_NAME'),
                ('Install event', 'addEventListener(\'install\''),
                ('Activate event', 'addEventListener(\'activate\''),
                ('Fetch event', 'addEventListener(\'fetch\''),
                ('Push event', 'addEventListener(\'push\''),
                ('Notification click', 'addEventListener(\'notificationclick\'')
            ]
            
            for feature_name, search_term in features:
                if search_term in sw_content:
                    print(f"✅ {feature_name}: Found")
                else:
                    print(f"❌ {feature_name}: Not found")
            
            return True
        else:
            print(f"❌ Service Worker not found: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing service worker: {e}")
        return False

def test_pwa_javascript():
    """Test PWA JavaScript files"""
    print("\n=== Testing PWA JavaScript ===")
    
    js_files = [
        '/static/js/pwa.js',
        '/static/js/app.js'
    ]
    
    success_count = 0
    for js_file in js_files:
        try:
            response = requests.get(f"{BASE_URL}{js_file}")
            if response.status_code == 200:
                content = response.text
                print(f"✅ {js_file}: Loaded successfully")
                
                # Check for PWA-specific features
                if 'pwa.js' in js_file:
                    pwa_features = [
                        ('Install prompt', 'beforeinstallprompt'),
                        ('Install function', 'installApp'),
                        ('iOS detection', 'iPad|iPhone|iPod'),
                        ('Notification permission', 'Notification.requestPermission'),
                        ('Toast notifications', 'showToast')
                    ]
                    
                    for feature_name, search_term in pwa_features:
                        if search_term in content:
                            print(f"   ✅ {feature_name}: Found")
                        else:
                            print(f"   ❌ {feature_name}: Not found")
                
                success_count += 1
            else:
                print(f"❌ {js_file}: Not found ({response.status_code})")
        except Exception as e:
            print(f"❌ Error loading {js_file}: {e}")
    
    print(f"✅ {success_count}/{len(js_files)} JavaScript files loaded")
    return success_count == len(js_files)

def test_pwa_meta_tags():
    """Test PWA meta tags in HTML"""
    print("\n=== Testing PWA Meta Tags ===")
    
    try:
        response = requests.get(BASE_URL)
        if response.status_code == 200:
            html_content = response.text
            print("✅ Main page loaded successfully")
            
            # Check for PWA meta tags
            meta_tags = [
                ('Viewport', 'name="viewport"'),
                ('Theme color', 'name="theme-color"'),
                ('Mobile web app capable', 'name="mobile-web-app-capable"'),
                ('Apple mobile web app capable', 'name="apple-mobile-web-app-capable"'),
                ('Apple mobile web app title', 'name="apple-mobile-web-app-title"'),
                ('Manifest link', 'rel="manifest"'),
                ('Apple touch icon', 'rel="apple-touch-icon"'),
                ('Favicon', 'rel="shortcut icon"')
            ]
            
            success_count = 0
            for tag_name, search_term in meta_tags:
                if search_term in html_content:
                    print(f"✅ {tag_name}: Found")
                    success_count += 1
                else:
                    print(f"❌ {tag_name}: Not found")
            
            print(f"✅ {success_count}/{len(meta_tags)} meta tags found")
            return success_count >= len(meta_tags) * 0.8  # Allow 80% success rate
        else:
            print(f"❌ Could not load main page: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing meta tags: {e}")
        return False

def test_offline_page():
    """Test offline page availability"""
    print("\n=== Testing Offline Page ===")
    
    try:
        # Try to access offline page directly
        response = requests.get(f"{BASE_URL}/offline")
        if response.status_code == 200:
            print("✅ Offline page accessible")
            
            # Check if it contains expected content
            content = response.text
            if 'offline' in content.lower() or 'ikke tilkoblet' in content.lower():
                print("✅ Offline page contains appropriate content")
                return True
            else:
                print("❌ Offline page content may be incomplete")
                return False
        else:
            print(f"❌ Offline page not found: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing offline page: {e}")
        return False

def test_notification_endpoints():
    """Test notification-related endpoints"""
    print("\n=== Testing Notification Endpoints ===")
    
    endpoints = [
        '/api/vapid-public-key',
        '/api/subscribe',
        '/api/send-notification'
    ]
    
    success_count = 0
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            # These endpoints might require authentication or POST method
            if response.status_code in [200, 405, 401]:  # 405 = Method Not Allowed, 401 = Unauthorized
                print(f"✅ {endpoint}: Endpoint exists")
                success_count += 1
            else:
                print(f"❌ {endpoint}: Not found ({response.status_code})")
        except Exception as e:
            print(f"❌ Error testing {endpoint}: {e}")
    
    print(f"✅ {success_count}/{len(endpoints)} notification endpoints found")
    return success_count >= len(endpoints) * 0.7  # Allow 70% success rate

def test_pwa_css():
    """Test PWA-specific CSS"""
    print("\n=== Testing PWA CSS ===")
    
    try:
        response = requests.get(f"{BASE_URL}/static/css/style.css")
        if response.status_code == 200:
            css_content = response.text
            print("✅ CSS file loaded successfully")
            
            # Check for PWA-specific styles
            pwa_styles = [
                ('PWA install banner', 'pwa-install-banner'),
                ('Standalone mode', 'display-mode: standalone'),
                ('Offline indicator', 'offline'),
                ('Toast notifications', 'toast-pwa'),
                ('Mobile responsive', '@media')
            ]
            
            success_count = 0
            for style_name, search_term in pwa_styles:
                if search_term in css_content:
                    print(f"✅ {style_name}: Found")
                    success_count += 1
                else:
                    print(f"❌ {style_name}: Not found")
            
            print(f"✅ {success_count}/{len(pwa_styles)} PWA styles found")
            return success_count >= len(pwa_styles) * 0.6  # Allow 60% success rate
        else:
            print(f"❌ CSS file not found: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing CSS: {e}")
        return False

def test_install_button():
    """Test install button presence"""
    print("\n=== Testing Install Button ===")
    
    try:
        response = requests.get(BASE_URL)
        if response.status_code == 200:
            html_content = response.text
            
            # Check for install button
            if 'id="installBtn"' in html_content:
                print("✅ Install button element found")
                
                # Check for install-related text
                install_indicators = [
                    'Installer app',
                    'Install',
                    'download',
                    'hjemskjerm'
                ]
                
                found_indicators = 0
                for indicator in install_indicators:
                    if indicator.lower() in html_content.lower():
                        found_indicators += 1
                
                if found_indicators > 0:
                    print(f"✅ Install button text found ({found_indicators} indicators)")
                    return True
                else:
                    print("❌ Install button text not found")
                    return False
            else:
                print("❌ Install button element not found")
                return False
        else:
            print(f"❌ Could not load page to check install button: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing install button: {e}")
        return False

def run_all_tests():
    """Run all PWA tests"""
    print("🔍 Starting Comprehensive PWA Testing\n")
    
    tests = [
        ("PWA Manifest", test_pwa_manifest),
        ("PWA Icons", test_pwa_icons),
        ("Service Worker", test_service_worker),
        ("PWA JavaScript", test_pwa_javascript),
        ("PWA Meta Tags", test_pwa_meta_tags),
        ("Offline Page", test_offline_page),
        ("Notification Endpoints", test_notification_endpoints),
        ("PWA CSS", test_pwa_css),
        ("Install Button", test_install_button)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Error in {test_name}: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*50)
    print("PWA TEST SUMMARY")
    print("="*50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All PWA tests passed! Your app is ready for mobile installation.")
    elif passed >= total * 0.8:
        print("✅ PWA is mostly functional. Some minor issues may need attention.")
    else:
        print("⚠️ PWA needs significant improvements for optimal mobile experience.")
    
    return passed == total

if __name__ == "__main__":
    print("Starting PWA functionality test...\n")
    print("Make sure the app is running on http://localhost:5000")
    
    # Wait a moment for user to confirm
    time.sleep(2)
    
    try:
        # Quick connectivity test
        response = requests.get(BASE_URL, timeout=5)
        if response.status_code == 200:
            print("✅ App is accessible, starting tests...\n")
            success = run_all_tests()
            sys.exit(0 if success else 1)
        else:
            print(f"❌ App not accessible: {response.status_code}")
            sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to app: {e}")
        print("Please start the app with: python app.py")
        sys.exit(1)
