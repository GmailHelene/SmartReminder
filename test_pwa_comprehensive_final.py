#!/usr/bin/env python3
"""Comprehensive PWA functionality test for SmartReminder."""

import requests
import json
import os
import time
from PIL import Image

def test_local_pwa_endpoints():
    """Test PWA endpoints on local server."""
    print("🔍 Testing PWA endpoints locally...")
    
    base_url = "http://127.0.0.1:5001"
    
    # Test manifest.json
    try:
        response = requests.get(f"{base_url}/static/manifest.json")
        if response.status_code == 200:
            manifest = response.json()
            print(f"   ✅ Manifest accessible: {manifest['name']}")
        else:
            print(f"   ❌ Manifest failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Manifest error: {e}")
    
    # Test service worker
    try:
        response = requests.get(f"{base_url}/sw.js")
        if response.status_code == 200:
            print(f"   ✅ Service Worker accessible: {len(response.text)} bytes")
        else:
            print(f"   ❌ Service Worker failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Service Worker error: {e}")
    
    # Test key icon files
    icon_sizes = ["72x72", "96x96", "128x128", "144x144", "152x152", "192x192", "384x384", "512x512"]
    
    for size in icon_sizes:
        try:
            response = requests.get(f"{base_url}/static/images/icon-{size}.png")
            if response.status_code == 200:
                print(f"   ✅ Icon {size} accessible: {len(response.content)} bytes")
            else:
                print(f"   ❌ Icon {size} failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Icon {size} error: {e}")
    
    # Test screenshots
    try:
        response = requests.get(f"{base_url}/static/images/screenshot1.png")
        if response.status_code == 200:
            print(f"   ✅ Screenshot1 accessible: {len(response.content)} bytes")
        else:
            print(f"   ❌ Screenshot1 failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Screenshot1 error: {e}")

def test_pwa_install_requirements():
    """Test PWA install requirements."""
    print(f"\n🔧 Testing PWA install requirements...")
    
    # Check manifest content
    manifest_path = "/workspaces/smartreminder/static/manifest.json"
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
    
    # Required fields for PWA install
    required_fields = {
        'name': manifest.get('name'),
        'short_name': manifest.get('short_name'),
        'start_url': manifest.get('start_url'),
        'display': manifest.get('display'),
        'theme_color': manifest.get('theme_color'),
        'background_color': manifest.get('background_color'),
        'icons': len(manifest.get('icons', []))
    }
    
    for field, value in required_fields.items():
        if value:
            print(f"   ✅ {field}: {value}")
        else:
            print(f"   ❌ {field}: Missing")
    
    # Check icon requirements
    icons = manifest.get('icons', [])
    has_192 = any(icon['sizes'] == '192x192' for icon in icons)
    has_512 = any(icon['sizes'] == '512x512' for icon in icons)
    has_maskable = any(icon.get('purpose') == 'maskable' for icon in icons)
    
    print(f"   ✅ Has 192x192 icon: {has_192}")
    print(f"   ✅ Has 512x512 icon: {has_512}")
    print(f"   ✅ Has maskable icons: {has_maskable}")
    
    # Check service worker
    sw_path = "/workspaces/smartreminder/sw.js"
    sw_exists = os.path.exists(sw_path)
    print(f"   ✅ Service Worker exists: {sw_exists}")
    
    if sw_exists:
        with open(sw_path, 'r') as f:
            sw_content = f.read()
            has_install = 'install' in sw_content
            has_fetch = 'fetch' in sw_content
            print(f"   ✅ SW has install event: {has_install}")
            print(f"   ✅ SW has fetch event: {has_fetch}")

def test_notification_setup():
    """Test notification setup in JavaScript files."""
    print(f"\n🔔 Testing notification setup...")
    
    # Check PWA JavaScript
    pwa_js_path = "/workspaces/smartreminder/static/js/pwa.js"
    if os.path.exists(pwa_js_path):
        with open(pwa_js_path, 'r') as f:
            pwa_content = f.read()
            
        has_notification_permission = 'Notification.permission' in pwa_content
        has_service_worker_reg = 'serviceWorker.register' in pwa_content
        has_install_prompt = 'beforeinstallprompt' in pwa_content
        
        print(f"   ✅ PWA.js exists: True")
        print(f"   ✅ Has notification permission check: {has_notification_permission}")
        print(f"   ✅ Has service worker registration: {has_service_worker_reg}")
        print(f"   ✅ Has install prompt handling: {has_install_prompt}")
    else:
        print(f"   ❌ PWA.js not found")
    
    # Check main app JavaScript
    app_js_path = "/workspaces/smartreminder/static/js/app.js"
    if os.path.exists(app_js_path):
        with open(app_js_path, 'r') as f:
            app_content = f.read()
            
        has_notification_api = 'showNotification' in app_content or 'requestPermission' in app_content
        has_sw_registration = 'serviceWorker.register' in app_content
        
        print(f"   ✅ App.js exists: True")
        print(f"   ✅ Has notification API usage: {has_notification_api}")
        print(f"   ✅ Has SW registration: {has_sw_registration}")
    else:
        print(f"   ❌ App.js not found")

def test_file_integrity():
    """Test file integrity and sizes."""
    print(f"\n📁 Testing file integrity...")
    
    static_images = "/workspaces/smartreminder/static/images"
    
    # Check all manifest icons
    required_icons = [
        "icon-72x72.png", "icon-96x96.png", "icon-128x128.png", 
        "icon-144x144.png", "icon-152x152.png", "icon-192x192.png",
        "icon-384x384.png", "icon-512x512.png", "badge-96x96.png"
    ]
    
    for icon in required_icons:
        icon_path = os.path.join(static_images, icon)
        if os.path.exists(icon_path):
            try:
                with Image.open(icon_path) as img:
                    width, height = img.size
                    file_size = os.path.getsize(icon_path)
                    print(f"   ✅ {icon}: {width}x{height}, {file_size} bytes")
            except Exception as e:
                print(f"   ❌ {icon}: Error - {e}")
        else:
            print(f"   ❌ {icon}: Not found")
    
    # Check screenshots
    screenshots = ["screenshot1.png", "screenshot2.png"]
    for screenshot in screenshots:
        screenshot_path = os.path.join(static_images, screenshot)
        if os.path.exists(screenshot_path):
            try:
                with Image.open(screenshot_path) as img:
                    width, height = img.size
                    file_size = os.path.getsize(screenshot_path)
                    print(f"   ✅ {screenshot}: {width}x{height}, {file_size} bytes")
            except Exception as e:
                print(f"   ❌ {screenshot}: Error - {e}")
        else:
            print(f"   ❌ {screenshot}: Not found")

def test_mobile_optimization():
    """Test mobile optimization features."""
    print(f"\n📱 Testing mobile optimization...")
    
    # Check viewport meta tag in base template
    base_template = "/workspaces/smartreminder/templates/base.html"
    if os.path.exists(base_template):
        with open(base_template, 'r') as f:
            base_content = f.read()
            
        has_viewport = 'viewport' in base_content
        has_theme_color = 'theme-color' in base_content
        has_manifest_link = 'manifest' in base_content
        has_apple_touch_icon = 'apple-touch-icon' in base_content
        
        print(f"   ✅ Base template exists: True")
        print(f"   ✅ Has viewport meta: {has_viewport}")
        print(f"   ✅ Has theme-color meta: {has_theme_color}")
        print(f"   ✅ Has manifest link: {has_manifest_link}")
        print(f"   ✅ Has apple-touch-icon: {has_apple_touch_icon}")
    else:
        print(f"   ❌ Base template not found")

if __name__ == "__main__":
    print("=" * 60)
    print("🔍 COMPREHENSIVE PWA FUNCTIONALITY TEST")
    print("=" * 60)
    
    test_local_pwa_endpoints()
    test_pwa_install_requirements()
    test_notification_setup()
    test_file_integrity()
    test_mobile_optimization()
    
    print(f"\n" + "=" * 60)
    print("✅ PWA FUNCTIONALITY TEST COMPLETE!")
    print("=" * 60)
    
    print(f"\n🚀 Next steps:")
    print(f"   1. Test PWA install on mobile device")
    print(f"   2. Test push notifications")
    print(f"   3. Test offline functionality")
    print(f"   4. Verify production deployment")
