#!/usr/bin/env python3
"""
Mobile PWA functionality test for SmartReminder Pro
Focuses on mobile-specific PWA features and installation
"""

import requests
import json
import time
from urllib.parse import urljoin
import re

# Base URL for testing
BASE_URL = "http://localhost:5000"

def test_mobile_viewport():
    """Test mobile viewport configuration"""
    print("=== Testing Mobile Viewport ===")
    
    try:
        response = requests.get(BASE_URL)
        if response.status_code == 200:
            html_content = response.text
            
            # Check viewport meta tag
            viewport_pattern = r'<meta\s+name="viewport"\s+content="([^"]+)"'
            viewport_match = re.search(viewport_pattern, html_content, re.IGNORECASE)
            
            if viewport_match:
                viewport_content = viewport_match.group(1)
                print(f"✅ Viewport meta tag found: {viewport_content}")
                
                # Check for mobile-optimized settings
                mobile_settings = [
                    ('width=device-width', 'Device width scaling'),
                    ('initial-scale=1.0', 'Initial scale'),
                    ('user-scalable=no', 'User scaling disabled')
                ]
                
                for setting, description in mobile_settings:
                    if setting in viewport_content:
                        print(f"✅ {description}: {setting}")
                    else:
                        print(f"❌ {description}: Missing")
                
                return True
            else:
                print("❌ Viewport meta tag not found")
                return False
        else:
            print(f"❌ Could not load page: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing viewport: {e}")
        return False

def test_apple_mobile_support():
    """Test Apple mobile web app support"""
    print("\n=== Testing Apple Mobile Support ===")
    
    try:
        response = requests.get(BASE_URL)
        if response.status_code == 200:
            html_content = response.text
            
            # Check for Apple-specific meta tags
            apple_tags = [
                ('apple-mobile-web-app-capable', 'Web app capable'),
                ('apple-mobile-web-app-status-bar-style', 'Status bar style'),
                ('apple-mobile-web-app-title', 'App title'),
                ('apple-touch-icon', 'Touch icon')
            ]
            
            success_count = 0
            for tag_name, description in apple_tags:
                if f'name="{tag_name}"' in html_content or f'rel="{tag_name}"' in html_content:
                    print(f"✅ {description}: Found")
                    success_count += 1
                else:
                    print(f"❌ {description}: Not found")
            
            print(f"✅ {success_count}/{len(apple_tags)} Apple tags found")
            return success_count >= len(apple_tags) * 0.75  # Allow 75% success rate
        else:
            print(f"❌ Could not load page: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing Apple support: {e}")
        return False

def test_android_chrome_support():
    """Test Android Chrome PWA support"""
    print("\n=== Testing Android Chrome Support ===")
    
    try:
        response = requests.get(BASE_URL)
        if response.status_code == 200:
            html_content = response.text
            
            # Check for Android-specific tags
            android_tags = [
                ('theme-color', 'Theme color'),
                ('mobile-web-app-capable', 'Mobile web app capable'),
                ('msapplication-TileColor', 'Tile color'),
                ('msapplication-tap-highlight', 'Tap highlight')
            ]
            
            success_count = 0
            for tag_name, description in android_tags:
                if f'name="{tag_name}"' in html_content:
                    print(f"✅ {description}: Found")
                    success_count += 1
                else:
                    print(f"❌ {description}: Not found")
            
            print(f"✅ {success_count}/{len(android_tags)} Android tags found")
            return success_count >= len(android_tags) * 0.75  # Allow 75% success rate
        else:
            print(f"❌ Could not load page: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing Android support: {e}")
        return False

def test_manifest_display_mode():
    """Test manifest display mode for mobile"""
    print("\n=== Testing Manifest Display Mode ===")
    
    try:
        response = requests.get(f"{BASE_URL}/static/manifest.json")
        if response.status_code == 200:
            manifest = response.json()
            
            display_mode = manifest.get('display', 'browser')
            print(f"✅ Display mode: {display_mode}")
            
            # Check for mobile-optimized display modes
            mobile_modes = ['standalone', 'fullscreen', 'minimal-ui']
            if display_mode in mobile_modes:
                print(f"✅ Mobile-optimized display mode: {display_mode}")
                return True
            else:
                print(f"❌ Display mode not optimized for mobile: {display_mode}")
                return False
        else:
            print(f"❌ Could not load manifest: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing manifest display mode: {e}")
        return False

def test_touch_icons():
    """Test touch icon configurations"""
    print("\n=== Testing Touch Icons ===")
    
    try:
        response = requests.get(f"{BASE_URL}/static/manifest.json")
        if response.status_code == 200:
            manifest = response.json()
            icons = manifest.get('icons', [])
            
            if not icons:
                print("❌ No icons found in manifest")
                return False
            
            # Check for common mobile icon sizes
            mobile_sizes = ['192x192', '512x512', '144x144', '152x152', '180x180']
            found_sizes = []
            
            for icon in icons:
                sizes = icon.get('sizes', '')
                if sizes in mobile_sizes:
                    found_sizes.append(sizes)
                    
                    # Test if icon is accessible
                    icon_url = urljoin(BASE_URL, icon['src'])
                    try:
                        icon_response = requests.get(icon_url)
                        if icon_response.status_code == 200:
                            print(f"✅ Icon {sizes}: Accessible")
                        else:
                            print(f"❌ Icon {sizes}: Not accessible")
                    except Exception as e:
                        print(f"❌ Icon {sizes}: Error loading - {e}")
            
            print(f"✅ Found {len(found_sizes)} mobile-optimized icons")
            return len(found_sizes) >= 2  # At least 2 mobile sizes
        else:
            print(f"❌ Could not load manifest: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing touch icons: {e}")
        return False

def test_ios_install_instructions():
    """Test iOS install instructions"""
    print("\n=== Testing iOS Install Instructions ===")
    
    try:
        # Check PWA JavaScript for iOS detection and instructions
        response = requests.get(f"{BASE_URL}/static/js/pwa.js")
        if response.status_code == 200:
            pwa_content = response.text
            
            # Check for iOS detection
            ios_indicators = [
                'iPad|iPhone|iPod',
                'iOS',
                'showIOSInstallInstructions',
                'hjemskjerm',
                'share'
            ]
            
            found_indicators = 0
            for indicator in ios_indicators:
                if indicator in pwa_content:
                    found_indicators += 1
                    print(f"✅ iOS feature found: {indicator}")
                else:
                    print(f"❌ iOS feature not found: {indicator}")
            
            print(f"✅ {found_indicators}/{len(ios_indicators)} iOS features found")
            return found_indicators >= len(ios_indicators) * 0.6  # Allow 60% success rate
        else:
            print(f"❌ Could not load PWA JavaScript: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing iOS instructions: {e}")
        return False

def test_push_notification_setup():
    """Test push notification setup for mobile"""
    print("\n=== Testing Push Notification Setup ===")
    
    try:
        # Check service worker for push handling
        response = requests.get(f"{BASE_URL}/static/sw.js")
        if response.status_code == 200:
            sw_content = response.text
            
            # Check for push notification features
            push_features = [
                ('Push event listener', 'addEventListener(\'push\''),
                ('Notification display', 'showNotification'),
                ('Notification click', 'addEventListener(\'notificationclick\''),
                ('Vibration support', 'vibrate'),
                ('Badge support', 'badge')
            ]
            
            found_features = 0
            for feature_name, search_term in push_features:
                if search_term in sw_content:
                    found_features += 1
                    print(f"✅ {feature_name}: Found")
                else:
                    print(f"❌ {feature_name}: Not found")
            
            print(f"✅ {found_features}/{len(push_features)} push features found")
            return found_features >= len(push_features) * 0.8  # Allow 80% success rate
        else:
            print(f"❌ Could not load service worker: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing push notifications: {e}")
        return False

def test_offline_functionality():
    """Test offline functionality for mobile"""
    print("\n=== Testing Offline Functionality ===")
    
    try:
        # Check service worker for offline handling
        response = requests.get(f"{BASE_URL}/static/sw.js")
        if response.status_code == 200:
            sw_content = response.text
            
            # Check for offline features
            offline_features = [
                ('Cache storage', 'caches.open'),
                ('Cache matching', 'caches.match'),
                ('Fetch event', 'addEventListener(\'fetch\''),
                ('Offline page', '/offline'),
                ('Cache strategy', 'networkFirst\\|cacheFirst')
            ]
            
            found_features = 0
            for feature_name, search_term in offline_features:
                if search_term in sw_content:
                    found_features += 1
                    print(f"✅ {feature_name}: Found")
                else:
                    print(f"❌ {feature_name}: Not found")
            
            # Test offline page availability
            try:
                offline_response = requests.get(f"{BASE_URL}/offline")
                if offline_response.status_code == 200:
                    print("✅ Offline page: Accessible")
                    found_features += 1
                else:
                    print("❌ Offline page: Not accessible")
            except Exception as e:
                print(f"❌ Offline page: Error - {e}")
            
            print(f"✅ {found_features}/{len(offline_features)+1} offline features found")
            return found_features >= len(offline_features) * 0.7  # Allow 70% success rate
        else:
            print(f"❌ Could not load service worker: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing offline functionality: {e}")
        return False

def test_mobile_responsive_design():
    """Test mobile responsive design"""
    print("\n=== Testing Mobile Responsive Design ===")
    
    try:
        response = requests.get(f"{BASE_URL}/static/css/style.css")
        if response.status_code == 200:
            css_content = response.text
            
            # Check for responsive design features
            responsive_features = [
                ('Media queries', '@media'),
                ('Mobile breakpoints', 'max-width:\\s*768px'),
                ('Flexible layouts', 'flex\\|grid'),
                ('Touch-friendly buttons', 'btn\\|button'),
                ('Mobile navigation', 'navbar-toggler')
            ]
            
            found_features = 0
            for feature_name, search_term in responsive_features:
                if re.search(search_term, css_content, re.IGNORECASE):
                    found_features += 1
                    print(f"✅ {feature_name}: Found")
                else:
                    print(f"❌ {feature_name}: Not found")
            
            print(f"✅ {found_features}/{len(responsive_features)} responsive features found")
            return found_features >= len(responsive_features) * 0.6  # Allow 60% success rate
        else:
            print(f"❌ Could not load CSS: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing responsive design: {e}")
        return False

def test_mobile_performance():
    """Test mobile performance optimizations"""
    print("\n=== Testing Mobile Performance ===")
    
    try:
        # Check for performance optimizations
        response = requests.get(BASE_URL)
        if response.status_code == 200:
            html_content = response.text
            
            # Check for performance features
            performance_features = [
                ('Preload resources', 'rel="preload"'),
                ('Async scripts', 'async'),
                ('Defer scripts', 'defer'),
                ('Minified resources', '\\.min\\.(js|css)'),
                ('CDN usage', 'cdn\\.|jsdelivr\\.|unpkg\\.')
            ]
            
            found_features = 0
            for feature_name, search_term in performance_features:
                if re.search(search_term, html_content, re.IGNORECASE):
                    found_features += 1
                    print(f"✅ {feature_name}: Found")
                else:
                    print(f"❌ {feature_name}: Not found")
            
            print(f"✅ {found_features}/{len(performance_features)} performance features found")
            return found_features >= len(performance_features) * 0.4  # Allow 40% success rate
        else:
            print(f"❌ Could not load page: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing performance: {e}")
        return False

def run_mobile_pwa_tests():
    """Run all mobile PWA tests"""
    print("📱 Starting Mobile PWA Testing\n")
    
    tests = [
        ("Mobile Viewport", test_mobile_viewport),
        ("Apple Mobile Support", test_apple_mobile_support),
        ("Android Chrome Support", test_android_chrome_support),
        ("Manifest Display Mode", test_manifest_display_mode),
        ("Touch Icons", test_touch_icons),
        ("iOS Install Instructions", test_ios_install_instructions),
        ("Push Notification Setup", test_push_notification_setup),
        ("Offline Functionality", test_offline_functionality),
        ("Mobile Responsive Design", test_mobile_responsive_design),
        ("Mobile Performance", test_mobile_performance)
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
    print("MOBILE PWA TEST SUMMARY")
    print("="*50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n📱 Mobile PWA Result: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 Perfect mobile PWA! Your app is fully optimized for mobile installation.")
    elif passed >= total * 0.8:
        print("✅ Good mobile PWA. Most features work well on mobile devices.")
    elif passed >= total * 0.6:
        print("⚠️ Average mobile PWA. Some mobile features need improvement.")
    else:
        print("❌ Poor mobile PWA. Significant mobile optimizations needed.")
    
    return passed >= total * 0.8

if __name__ == "__main__":
    print("Starting Mobile PWA functionality test...\n")
    print("Make sure the app is running on http://localhost:5000")
    
    # Wait a moment for user to confirm
    time.sleep(2)
    
    try:
        # Quick connectivity test
        response = requests.get(BASE_URL, timeout=5)
        if response.status_code == 200:
            print("✅ App is accessible, starting mobile tests...\n")
            success = run_mobile_pwa_tests()
            
            if success:
                print("\n🎯 MOBILE PWA RECOMMENDATIONS:")
                print("• Test installation on actual mobile devices")
                print("• Verify offline functionality works as expected")
                print("• Test push notifications on mobile browsers")
                print("• Check touch interactions and gestures")
                print("• Verify app launch from home screen")
            else:
                print("\n🔧 MOBILE PWA IMPROVEMENT SUGGESTIONS:")
                print("• Add missing Apple mobile web app meta tags")
                print("• Ensure proper touch icon sizes are available")
                print("• Improve offline functionality and caching")
                print("• Add iOS-specific install instructions")
                print("• Test responsive design on various screen sizes")
            
            exit(0 if success else 1)
        else:
            print(f"❌ App not accessible: {response.status_code}")
            exit(1)
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to app: {e}")
        print("Please start the app with: python app.py")
        exit(1)
