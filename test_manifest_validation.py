#!/usr/bin/env python3
"""Test manifest.json validation and icon file availability."""

import json
import os
import requests
from PIL import Image
import io

def test_manifest_validation():
    """Test that manifest.json is valid and all referenced files exist."""
    print("🔍 Testing manifest.json validation...")
    
    # Read manifest.json
    manifest_path = "/workspaces/smartreminder/static/manifest.json"
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
    
    print(f"✅ Manifest loaded successfully")
    print(f"   Name: {manifest['name']}")
    print(f"   Short name: {manifest['short_name']}")
    print(f"   Start URL: {manifest['start_url']}")
    print(f"   Icons: {len(manifest['icons'])}")
    
    # Check all icon files exist and are valid
    static_path = "/workspaces/smartreminder/static"
    print(f"\n🖼️  Checking {len(manifest['icons'])} icons...")
    
    for i, icon in enumerate(manifest['icons']):
        # Remove /static prefix from src to get file path
        icon_path = icon['src'].replace('/static', static_path)
        
        if os.path.exists(icon_path):
            try:
                # Try to open and validate as PNG
                with Image.open(icon_path) as img:
                    width, height = img.size
                    expected_size = icon['sizes'].split('x')[0]
                    
                    if str(width) == expected_size:
                        print(f"   ✅ {icon['src']} - {icon['sizes']} - Valid PNG")
                    else:
                        print(f"   ⚠️  {icon['src']} - Size mismatch: {width}x{height} vs {icon['sizes']}")
                        
            except Exception as e:
                print(f"   ❌ {icon['src']} - Invalid image: {e}")
        else:
            print(f"   ❌ {icon['src']} - File not found")
    
    # Check screenshots
    print(f"\n📸 Checking {len(manifest['screenshots'])} screenshots...")
    for screenshot in manifest['screenshots']:
        screenshot_path = screenshot['src'].replace('/static', static_path)
        if os.path.exists(screenshot_path):
            try:
                with Image.open(screenshot_path) as img:
                    width, height = img.size
                    expected_width, expected_height = screenshot['sizes'].split('x')
                    
                    if str(width) == expected_width and str(height) == expected_height:
                        print(f"   ✅ {screenshot['src']} - {screenshot['sizes']} - Valid PNG")
                    else:
                        print(f"   ⚠️  {screenshot['src']} - Size mismatch: {width}x{height} vs {screenshot['sizes']}")
                        
            except Exception as e:
                print(f"   ❌ {screenshot['src']} - Invalid image: {e}")
        else:
            print(f"   ❌ {screenshot['src']} - File not found")
    
    print(f"\n✅ Manifest validation complete!")

def test_pwa_requirements():
    """Test PWA requirements."""
    print(f"\n🔧 Testing PWA requirements...")
    
    # Check service worker exists
    sw_path = "/workspaces/smartreminder/sw.js"
    if os.path.exists(sw_path):
        print(f"   ✅ Service Worker found: /sw.js")
    else:
        print(f"   ❌ Service Worker not found: /sw.js")
    
    # Check required manifest fields
    manifest_path = "/workspaces/smartreminder/static/manifest.json"
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
    
    required_fields = ['name', 'short_name', 'start_url', 'display', 'icons']
    for field in required_fields:
        if field in manifest:
            print(f"   ✅ Required field '{field}' present")
        else:
            print(f"   ❌ Required field '{field}' missing")
    
    # Check minimum icon sizes
    icon_sizes = [icon['sizes'] for icon in manifest['icons']]
    required_sizes = ['192x192', '512x512']
    
    for size in required_sizes:
        if size in icon_sizes:
            print(f"   ✅ Required icon size {size} present")
        else:
            print(f"   ❌ Required icon size {size} missing")

def test_icon_file_integrity():
    """Test that all icon files are valid and not corrupted."""
    print(f"\n🔍 Testing icon file integrity...")
    
    static_images = "/workspaces/smartreminder/static/images"
    icon_files = [f for f in os.listdir(static_images) if f.startswith('icon-') and f.endswith('.png')]
    
    for icon_file in sorted(icon_files):
        icon_path = os.path.join(static_images, icon_file)
        try:
            with Image.open(icon_path) as img:
                width, height = img.size
                format = img.format
                mode = img.mode
                
                # Extract expected size from filename
                size_part = icon_file.replace('icon-', '').replace('.png', '')
                expected_size = size_part.split('x')[0]
                
                if str(width) == expected_size:
                    print(f"   ✅ {icon_file} - {width}x{height} {format} {mode}")
                else:
                    print(f"   ⚠️  {icon_file} - Size mismatch: {width}x{height} vs expected {expected_size}")
                    
        except Exception as e:
            print(f"   ❌ {icon_file} - Error: {e}")

if __name__ == "__main__":
    print("=" * 50)
    print("🔍 MANIFEST AND PWA VALIDATION TEST")
    print("=" * 50)
    
    test_manifest_validation()
    test_pwa_requirements()
    test_icon_file_integrity()
    
    print(f"\n" + "=" * 50)
    print("✅ All tests completed!")
    print("=" * 50)
