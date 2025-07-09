#!/usr/bin/env python3
"""
Test PWA functionality - check manifest, service worker, and install requirements
"""

import json
import os
import requests
from urllib.parse import urljoin
import time

def test_pwa_functionality():
    """Test PWA functionality"""
    
    print("🔍 Testing PWA functionality...")
    
    # Test 1: Check if manifest.json exists and is valid
    print("\n1. Testing manifest.json...")
    manifest_path = "/workspaces/smartreminder/static/manifest.json"
    
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
            
            print(f"✅ Manifest file exists and is valid JSON")
            print(f"   - Name: {manifest.get('name', 'N/A')}")
            print(f"   - Short name: {manifest.get('short_name', 'N/A')}")
            print(f"   - Start URL: {manifest.get('start_url', 'N/A')}")
            print(f"   - Display mode: {manifest.get('display', 'N/A')}")
            print(f"   - Icons: {len(manifest.get('icons', []))} icons")
            
            # Check required fields
            required_fields = ['name', 'short_name', 'start_url', 'display', 'icons']
            missing_fields = [field for field in required_fields if field not in manifest]
            
            if missing_fields:
                print(f"❌ Missing required fields: {missing_fields}")
            else:
                print("✅ All required manifest fields present")
                
        except json.JSONDecodeError as e:
            print(f"❌ Manifest JSON parse error: {e}")
    else:
        print(f"❌ Manifest file not found at {manifest_path}")
    
    # Test 2: Check if service worker exists
    print("\n2. Testing service worker...")
    sw_path = "/workspaces/smartreminder/static/js/sw.js"
    
    if os.path.exists(sw_path):
        print("✅ Service worker file exists")
        
        # Check service worker content
        with open(sw_path, 'r') as f:
            sw_content = f.read()
            
        if 'addEventListener' in sw_content and 'install' in sw_content:
            print("✅ Service worker has install event listener")
        else:
            print("❌ Service worker missing install event listener")
            
        if 'fetch' in sw_content:
            print("✅ Service worker has fetch event handler")
        else:
            print("❌ Service worker missing fetch event handler")
            
    else:
        print(f"❌ Service worker not found at {sw_path}")
    
    # Test 3: Check if PWA icons exist
    print("\n3. Testing PWA icons...")
    icon_sizes = ['192x192', '512x512']
    missing_icons = []
    
    for size in icon_sizes:
        icon_path = f"/workspaces/smartreminder/static/images/icon-{size}.png"
        if os.path.exists(icon_path):
            print(f"✅ Icon {size} exists")
        else:
            print(f"❌ Icon {size} missing")
            missing_icons.append(size)
    
    # Test 4: Check if PWA meta tags are in templates
    print("\n4. Testing PWA meta tags...")
    base_template_path = "/workspaces/smartreminder/templates/base.html"
    
    if os.path.exists(base_template_path):
        with open(base_template_path, 'r') as f:
            base_content = f.read()
        
        meta_tags = [
            'name="viewport"',
            'name="theme-color"',
            'rel="manifest"',
            'name="apple-mobile-web-app-capable"'
        ]
        
        for tag in meta_tags:
            if tag in base_content:
                print(f"✅ {tag} found in base template")
            else:
                print(f"❌ {tag} missing from base template")
    else:
        print("❌ Base template not found")
    
    # Test 5: Check if PWA JavaScript is included
    print("\n5. Testing PWA JavaScript...")
    pwa_js_path = "/workspaces/smartreminder/static/js/pwa.js"
    
    if os.path.exists(pwa_js_path):
        print("✅ PWA JavaScript file exists")
        
        with open(pwa_js_path, 'r') as f:
            pwa_content = f.read()
        
        if 'beforeinstallprompt' in pwa_content:
            print("✅ PWA install prompt handling found")
        else:
            print("❌ PWA install prompt handling missing")
            
        if 'serviceWorker' in pwa_content:
            print("✅ Service worker registration found")
        else:
            print("❌ Service worker registration missing")
    else:
        print("❌ PWA JavaScript file not found")
    
    # Test 6: Check if offline page exists
    print("\n6. Testing offline functionality...")
    offline_template_path = "/workspaces/smartreminder/templates/offline.html"
    
    if os.path.exists(offline_template_path):
        print("✅ Offline page template exists")
    else:
        print("❌ Offline page template missing")
    
    print("\n" + "="*50)
    print("PWA FUNCTIONALITY TEST COMPLETE")
    print("="*50)
    
    return True

if __name__ == "__main__":
    test_pwa_functionality()
