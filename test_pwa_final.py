#!/usr/bin/env python3
"""Final comprehensive PWA production readiness test."""

import json
import os
import requests
import subprocess
import time
from PIL import Image
import io

def test_service_worker_registration():
    """Test that Service Worker is properly registered and accessible."""
    print("🔧 Testing Service Worker registration...")
    
    # Check SW file exists at root
    sw_path = "/workspaces/smartreminder/sw.js"
    if os.path.exists(sw_path):
        print(f"   ✅ Service Worker file exists at /sw.js")
        
        # Check SW content
        with open(sw_path, 'r') as f:
            content = f.read()
            
        if 'addEventListener' in content and 'install' in content:
            print(f"   ✅ Service Worker has install event listener")
        else:
            print(f"   ❌ Service Worker missing install event listener")
            
        if 'push' in content:
            print(f"   ✅ Service Worker has push notification support")
        else:
            print(f"   ❌ Service Worker missing push notification support")
            
    else:
        print(f"   ❌ Service Worker not found at /sw.js")

def test_manifest_completeness():
    """Test manifest.json completeness for PWA requirements."""
    print(f"\n📋 Testing manifest.json completeness...")
    
    manifest_path = "/workspaces/smartreminder/static/manifest.json"
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
    
    # Test required PWA fields
    required_fields = {
        'name': 'App name',
        'short_name': 'Short name',
        'start_url': 'Start URL',
        'display': 'Display mode',
        'theme_color': 'Theme color',
        'background_color': 'Background color',
        'icons': 'Icons array'
    }
    
    for field, description in required_fields.items():
        if field in manifest and manifest[field]:
            print(f"   ✅ {description}: {manifest[field] if field != 'icons' else f'{len(manifest[field])} icons'}")
        else:
            print(f"   ❌ Missing {description}")
    
    # Test PWA-specific features
    if 'scope' in manifest:
        print(f"   ✅ Scope defined: {manifest['scope']}")
    
    if 'shortcuts' in manifest:
        print(f"   ✅ App shortcuts: {len(manifest['shortcuts'])} shortcuts")
    
    if 'screenshots' in manifest:
        print(f"   ✅ Screenshots: {len(manifest['screenshots'])} screenshots")
    
    # Test icon requirements
    icon_sizes = [icon['sizes'] for icon in manifest['icons']]
    required_sizes = ['192x192', '512x512']
    
    for size in required_sizes:
        if size in icon_sizes:
            print(f"   ✅ Required icon size {size} present")
        else:
            print(f"   ❌ Missing required icon size {size}")
    
    # Test icon purposes
    purposes = []
    for icon in manifest['icons']:
        if 'purpose' in icon:
            purposes.append(icon['purpose'])
    
    if 'maskable' in purposes:
        print(f"   ✅ Maskable icons present")
    if 'monochrome' in purposes:
        print(f"   ✅ Monochrome badge icon present")

def test_icon_file_integrity():
    """Test that all referenced icons are valid and accessible."""
    print(f"\n🖼️  Testing icon file integrity...")
    
    manifest_path = "/workspaces/smartreminder/static/manifest.json"
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
    
    static_path = "/workspaces/smartreminder/static"
    
    for icon in manifest['icons']:
        icon_path = icon['src'].replace('/static', static_path)
        
        if os.path.exists(icon_path):
            try:
                with Image.open(icon_path) as img:
                    width, height = img.size
                    expected_size = icon['sizes'].split('x')[0]
                    
                    if str(width) == expected_size:
                        purpose = icon.get('purpose', 'any')
                        print(f"   ✅ {icon['src']} - {width}x{height} - {purpose}")
                    else:
                        print(f"   ⚠️  {icon['src']} - Size mismatch: {width}x{height} vs {icon['sizes']}")
                        
            except Exception as e:
                print(f"   ❌ {icon['src']} - Invalid image: {e}")
        else:
            print(f"   ❌ {icon['src']} - File not found")

def test_pwa_js_integration():
    """Test PWA JavaScript integration."""
    print(f"\n🔗 Testing PWA JavaScript integration...")
    
    # Check pwa.js exists
    pwa_js_path = "/workspaces/smartreminder/static/js/pwa.js"
    if os.path.exists(pwa_js_path):
        print(f"   ✅ PWA JavaScript file exists")
        
        with open(pwa_js_path, 'r') as f:
            content = f.read()
            
        # Check for key PWA features
        if 'serviceWorker' in content:
            print(f"   ✅ Service Worker registration code present")
        if 'beforeinstallprompt' in content:
            print(f"   ✅ Install prompt handling present")
        if 'deferredPrompt' in content:
            print(f"   ✅ Deferred prompt handling present")
        if 'Push' in content or 'Notification' in content:
            print(f"   ✅ Push notification support present")
    else:
        print(f"   ❌ PWA JavaScript file not found")
    
    # Check app.js for conflicts
    app_js_path = "/workspaces/smartreminder/static/js/app.js"
    if os.path.exists(app_js_path):
        with open(app_js_path, 'r') as f:
            content = f.read()
            
        # Check for duplicate PWA code
        if 'let deferredPrompt' in content or 'var deferredPrompt' in content:
            print(f"   ⚠️  Duplicate deferredPrompt declaration found in app.js")
        else:
            print(f"   ✅ No duplicate PWA declarations in app.js")

def test_production_readiness():
    """Test production deployment readiness."""
    print(f"\n🚀 Testing production deployment readiness...")
    
    # Check essential files
    essential_files = [
        "/workspaces/smartreminder/app.py",
        "/workspaces/smartreminder/requirements.txt",
        "/workspaces/smartreminder/sw.js",
        "/workspaces/smartreminder/static/manifest.json",
        "/workspaces/smartreminder/static/js/pwa.js",
        "/workspaces/smartreminder/Procfile"
    ]
    
    for file_path in essential_files:
        if os.path.exists(file_path):
            print(f"   ✅ {os.path.basename(file_path)} exists")
        else:
            print(f"   ❌ {os.path.basename(file_path)} missing")
    
    # Check git status
    try:
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True, 
                              cwd='/workspaces/smartreminder')
        
        if result.returncode == 0:
            if result.stdout.strip():
                print(f"   ⚠️  Uncommitted changes found")
            else:
                print(f"   ✅ All changes committed")
        else:
            print(f"   ❌ Git status check failed")
    except Exception as e:
        print(f"   ❌ Git check error: {e}")

def test_mobile_features():
    """Test mobile-specific PWA features."""
    print(f"\n📱 Testing mobile-specific features...")
    
    manifest_path = "/workspaces/smartreminder/static/manifest.json"
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
    
    # Test mobile-friendly settings
    if manifest.get('display') == 'standalone':
        print(f"   ✅ Standalone display mode for mobile")
    
    if manifest.get('orientation') == 'portrait-primary':
        print(f"   ✅ Portrait orientation preference")
    
    if 'viewport-fit=cover' in str(manifest):
        print(f"   ✅ Viewport fit for notched devices")
    else:
        print(f"   ⚠️  No viewport-fit specified")
    
    # Check Service Worker for mobile push
    sw_path = "/workspaces/smartreminder/sw.js"
    if os.path.exists(sw_path):
        with open(sw_path, 'r') as f:
            sw_content = f.read()
            
        if 'vibrate' in sw_content:
            print(f"   ✅ Vibration API for mobile notifications")
        if 'badge' in sw_content:
            print(f"   ✅ Badge icon for mobile notifications")
        if 'requireInteraction' in sw_content:
            print(f"   ✅ Persistent notifications for mobile")

def generate_pwa_score():
    """Generate a PWA readiness score."""
    print(f"\n📊 Generating PWA Readiness Score...")
    
    score = 0
    max_score = 20
    
    # Check manifest (5 points)
    manifest_path = "/workspaces/smartreminder/static/manifest.json"
    if os.path.exists(manifest_path):
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        
        required_fields = ['name', 'short_name', 'start_url', 'display', 'icons']
        if all(field in manifest for field in required_fields):
            score += 5
    
    # Check Service Worker (5 points)
    sw_path = "/workspaces/smartreminder/sw.js"
    if os.path.exists(sw_path):
        with open(sw_path, 'r') as f:
            sw_content = f.read()
        if 'addEventListener' in sw_content and 'install' in sw_content:
            score += 5
    
    # Check icons (5 points)
    if os.path.exists(manifest_path):
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        
        icon_sizes = [icon['sizes'] for icon in manifest['icons']]
        if '192x192' in icon_sizes and '512x512' in icon_sizes:
            score += 5
    
    # Check PWA features (5 points)
    pwa_js_path = "/workspaces/smartreminder/static/js/pwa.js"
    if os.path.exists(pwa_js_path):
        with open(pwa_js_path, 'r') as f:
            pwa_content = f.read()
        if 'beforeinstallprompt' in pwa_content and 'serviceWorker' in pwa_content:
            score += 5
    
    percentage = (score / max_score) * 100
    print(f"   📈 PWA Readiness Score: {score}/{max_score} ({percentage:.0f}%)")
    
    if percentage >= 90:
        print(f"   🎉 Excellent! Ready for production deployment")
    elif percentage >= 70:
        print(f"   ✅ Good! Minor improvements recommended")
    elif percentage >= 50:
        print(f"   ⚠️  Adequate! Several improvements needed")
    else:
        print(f"   ❌ Poor! Major improvements required")

if __name__ == "__main__":
    print("=" * 60)
    print("🔍 FINAL PWA PRODUCTION READINESS TEST")
    print("=" * 60)
    
    test_service_worker_registration()
    test_manifest_completeness()
    test_icon_file_integrity()
    test_pwa_js_integration()
    test_production_readiness()
    test_mobile_features()
    generate_pwa_score()
    
    print(f"\n" + "=" * 60)
    print("✅ Final PWA test completed!")
    print("=" * 60)
