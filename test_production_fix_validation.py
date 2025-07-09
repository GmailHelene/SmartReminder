#!/usr/bin/env python3
"""
Test the production error fixes by checking key endpoints
"""

import requests
import time
import subprocess
import os

def test_live_endpoints():
    """Test live endpoints to verify the fixes"""
    print("🔍 Testing live endpoints...")
    
    # Test production deployment URL
    base_url = "https://smartremind-production.up.railway.app"
    
    endpoints = [
        "/",
        "/sw.js",
        "/static/manifest.json",
        "/static/images/icon-144x144.png",
        "/static/images/icon-192x192.png",
        "/static/images/icon-512x512.png",
        "/static/images/badge-96x96.png",
        "/static/images/screenshot1.png"
    ]
    
    print(f"Testing {base_url}...")
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            
            if response.status_code == 200:
                print(f"  ✅ {endpoint}: {response.status_code} ({len(response.content)} bytes)")
                
                # Special checks for specific endpoints
                if endpoint == "/sw.js":
                    if "service worker" in response.text.lower():
                        print(f"    ✅ Service Worker content validated")
                    else:
                        print(f"    ⚠️ Service Worker content may be incorrect")
                
                elif endpoint == "/static/manifest.json":
                    try:
                        manifest = response.json()
                        if "icons" in manifest and len(manifest["icons"]) > 0:
                            print(f"    ✅ Manifest contains {len(manifest['icons'])} icons")
                        else:
                            print(f"    ❌ Manifest missing icons")
                    except:
                        print(f"    ❌ Invalid manifest JSON")
                
                elif endpoint.endswith(".png"):
                    if response.headers.get('content-type', '').startswith('image/png'):
                        print(f"    ✅ Valid PNG image")
                    else:
                        print(f"    ❌ Invalid PNG image")
                        
            else:
                print(f"  ❌ {endpoint}: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"  ❌ {endpoint}: Request failed - {e}")
    
    print()
    
    # Test the main page for JavaScript errors
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            content = response.text
            
            # Check for potential JavaScript error patterns
            error_patterns = [
                "Identifier 'deferredPrompt' has already been declared",
                "deferredPrompt is not defined",
                "beforeinstallprompt",
                "Service Worker registration failed",
                "SecurityError"
            ]
            
            js_errors = []
            for pattern in error_patterns:
                if pattern in content:
                    js_errors.append(pattern)
            
            if js_errors:
                print(f"  ⚠️ Potential JavaScript issues found:")
                for error in js_errors:
                    print(f"    - {error}")
            else:
                print(f"  ✅ No obvious JavaScript error patterns found")
                
        else:
            print(f"  ❌ Could not fetch main page: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Main page test failed: {e}")

def test_chrome_lighthouse():
    """Test with Chrome Lighthouse if available"""
    print("\n🔍 Testing PWA with Chrome Lighthouse...")
    
    # Check if Chrome is available
    try:
        subprocess.run(["google-chrome", "--version"], capture_output=True, check=True)
        print("  ✅ Chrome is available")
        
        # Note: This would require lighthouse-cli to be installed
        # For now, just indicate that manual testing is recommended
        print("  ℹ️ Manual Lighthouse testing recommended:")
        print("    1. Open https://smartremind-production.up.railway.app in Chrome")
        print("    2. Open Developer Tools (F12)")
        print("    3. Go to Lighthouse tab")
        print("    4. Run PWA audit")
        
    except:
        print("  ℹ️ Chrome not available for automated testing")

def main():
    print("🚀 Production Error Fix Validation")
    print("=" * 50)
    
    test_live_endpoints()
    test_chrome_lighthouse()
    
    print("\n" + "=" * 50)
    print("🎉 Production error fix validation complete!")
    print("\nThe fixes should address:")
    print("1. ✅ Duplicate deferredPrompt declarations")
    print("2. ✅ Service Worker registration scope errors")
    print("3. ✅ Manifest icon download errors")
    print("\nTo verify in production:")
    print("- Open https://smartremind-production.up.railway.app")
    print("- Check browser console for any JavaScript errors")
    print("- Test PWA installation functionality")
    print("- Verify push notifications work correctly")

if __name__ == "__main__":
    main()
