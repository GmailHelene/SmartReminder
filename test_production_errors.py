#!/usr/bin/env python3
"""
Final production error validation script
Tests for the specific production errors mentioned:
1. "Identifier 'deferredPrompt' has already been declared" JS error
2. Service Worker registration scope error
3. Manifest icon download errors
"""

import os
import json
import requests
from pathlib import Path
import subprocess
import time
import re

def test_duplicate_deferredPrompt():
    """Test for duplicate deferredPrompt declarations"""
    print("🔍 Testing for duplicate deferredPrompt declarations...")
    
    # Test files for duplicate declarations
    test_files = [
        '/workspaces/smartreminder/static/js/app.js',
        '/workspaces/smartreminder/static/js/pwa.js',
        '/workspaces/smartreminder/index.html'
    ]
    
    duplicate_found = False
    declaration_count = 0
    
    for file_path in test_files:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                content = f.read()
                lines = content.split('\n')
                
                # Check for actual variable declarations (not assignments)
                let_declarations = len(re.findall(r'\blet\s+deferredPrompt', content))
                var_declarations = len(re.findall(r'\bvar\s+deferredPrompt', content))
                
                # Only count the initial window.deferredPrompt = null as a declaration
                # (typically at the top of the file)
                window_declarations = 0
                for i, line in enumerate(lines):
                    if 'window.deferredPrompt = null' in line and not line.strip().startswith('//'):
                        # Check if this is likely an initial declaration (top 10 lines)
                        if i < 10:
                            window_declarations += 1
                            break
                
                file_declarations = let_declarations + var_declarations + window_declarations
                declaration_count += file_declarations
                
                if file_declarations > 0:
                    print(f"  📄 {file_path}: {file_declarations} declarations")
                    
                    # Look for beforeinstallprompt handlers
                    beforeinstall_handlers = len(re.findall(r'addEventListener\s*\(\s*[\'"]beforeinstallprompt[\'"]', content))
                    if beforeinstall_handlers > 0:
                        print(f"    📋 beforeinstallprompt handlers: {beforeinstall_handlers}")
    
    if declaration_count > 1:
        print(f"  ❌ ERROR: Found {declaration_count} deferredPrompt declarations (should be 1)")
        duplicate_found = True
    else:
        print(f"  ✅ OK: Found {declaration_count} deferredPrompt declaration (correct)")
    
    return not duplicate_found

def test_service_worker_registration():
    """Test Service Worker registration patterns"""
    print("\n🔍 Testing Service Worker registration patterns...")
    
    # Test files that should register service workers
    test_files = [
        '/workspaces/smartreminder/static/js/app.js',
        '/workspaces/smartreminder/static/js/pwa.js',
        '/workspaces/smartreminder/templates/base.html'
    ]
    
    correct_registrations = 0
    incorrect_registrations = 0
    
    for file_path in test_files:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                content = f.read()
                
                # Check for correct SW registration (/sw.js with scope /)
                correct_pattern = r"register\(['\"]\/sw\.js['\"].*scope:\s*['\"]\/['\"]"
                if re.search(correct_pattern, content):
                    print(f"  ✅ {file_path}: Correct SW registration")
                    correct_registrations += 1
                
                # Check for incorrect SW registration patterns
                incorrect_patterns = [
                    r"register\(['\"]\/static\/sw\.js['\"]",  # wrong path
                    r"register\(['\"]sw\.js['\"]",  # relative path
                    r"register\(['\"]\/sw\.js['\"].*scope:\s*['\"]\/static\/['\"]"  # wrong scope
                ]
                
                for pattern in incorrect_patterns:
                    if re.search(pattern, content):
                        print(f"  ❌ {file_path}: Incorrect SW registration pattern")
                        incorrect_registrations += 1
    
    if incorrect_registrations > 0:
        print(f"  ❌ ERROR: Found {incorrect_registrations} incorrect SW registrations")
        return False
    else:
        print(f"  ✅ OK: Found {correct_registrations} correct SW registrations")
        return True

def test_service_worker_route():
    """Test that /sw.js route exists in Flask app"""
    print("\n🔍 Testing Service Worker Flask route...")
    
    app_file = '/workspaces/smartreminder/app.py'
    if os.path.exists(app_file):
        with open(app_file, 'r') as f:
            content = f.read()
            
            if "@app.route('/sw.js')" in content:
                print("  ✅ /sw.js route found in app.py")
                return True
            else:
                print("  ❌ /sw.js route NOT found in app.py")
                return False
    else:
        print("  ❌ app.py file not found")
        return False

def test_manifest_icons():
    """Test that all manifest icons exist and are valid"""
    print("\n🔍 Testing manifest icons...")
    
    # Read manifest file
    manifest_path = '/workspaces/smartreminder/static/manifest.json'
    if not os.path.exists(manifest_path):
        print("  ❌ Manifest file not found")
        return False
    
    try:
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
    except:
        print("  ❌ Invalid manifest JSON")
        return False
    
    icons = manifest.get('icons', [])
    if not icons:
        print("  ❌ No icons found in manifest")
        return False
    
    print(f"  📄 Found {len(icons)} icons in manifest")
    
    valid_icons = 0
    invalid_icons = 0
    
    for icon in icons:
        icon_path = icon.get('src', '').replace('/static/', '/workspaces/smartreminder/static/')
        
        if os.path.exists(icon_path):
            # Test if it's a valid PNG
            try:
                result = subprocess.run(['identify', icon_path], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"  ✅ {icon.get('sizes', 'unknown')}: Valid PNG")
                    valid_icons += 1
                else:
                    print(f"  ❌ {icon.get('sizes', 'unknown')}: Invalid image")
                    invalid_icons += 1
            except:
                print(f"  ❌ {icon.get('sizes', 'unknown')}: Cannot validate")
                invalid_icons += 1
        else:
            print(f"  ❌ {icon.get('sizes', 'unknown')}: File not found")
            invalid_icons += 1
    
    if invalid_icons > 0:
        print(f"  ❌ ERROR: {invalid_icons} invalid icons found")
        return False
    else:
        print(f"  ✅ OK: All {valid_icons} icons are valid")
        return True

def test_badge_and_screenshots():
    """Test badge and screenshot images"""
    print("\n🔍 Testing badge and screenshot images...")
    
    test_files = [
        '/workspaces/smartreminder/static/images/badge-96x96.png',
        '/workspaces/smartreminder/static/images/screenshot1.png',
        '/workspaces/smartreminder/static/images/screenshot2.png'
    ]
    
    valid_count = 0
    
    for file_path in test_files:
        if os.path.exists(file_path):
            try:
                result = subprocess.run(['identify', file_path], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"  ✅ {os.path.basename(file_path)}: Valid")
                    valid_count += 1
                else:
                    print(f"  ❌ {os.path.basename(file_path)}: Invalid")
            except:
                print(f"  ❌ {os.path.basename(file_path)}: Cannot validate")
        else:
            print(f"  ❌ {os.path.basename(file_path)}: Not found")
    
    if valid_count == len(test_files):
        print(f"  ✅ OK: All {valid_count} support images are valid")
        return True
    else:
        print(f"  ❌ ERROR: Only {valid_count}/{len(test_files)} support images are valid")
        return False

def test_no_duplicate_beforeinstallprompt():
    """Test for duplicate beforeinstallprompt handlers"""
    print("\n🔍 Testing for duplicate beforeinstallprompt handlers...")
    
    test_files = [
        '/workspaces/smartreminder/static/js/app.js',
        '/workspaces/smartreminder/static/js/pwa.js',
        '/workspaces/smartreminder/index.html'
    ]
    
    handler_count = 0
    
    for file_path in test_files:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                content = f.read()
                
                # Count beforeinstallprompt handlers
                handlers = len(re.findall(r'addEventListener\s*\(\s*[\'"]beforeinstallprompt[\'"]', content))
                if handlers > 0:
                    print(f"  📄 {file_path}: {handlers} beforeinstallprompt handlers")
                    handler_count += handlers
    
    if handler_count > 1:
        print(f"  ❌ ERROR: Found {handler_count} beforeinstallprompt handlers (should be 1)")
        return False
    else:
        print(f"  ✅ OK: Found {handler_count} beforeinstallprompt handler (correct)")
        return True

def main():
    """Run all production error tests"""
    print("🚀 Production Error Validation Tests")
    print("=" * 50)
    
    tests = [
        ("Duplicate deferredPrompt declarations", test_duplicate_deferredPrompt),
        ("Service Worker registration patterns", test_service_worker_registration),
        ("Service Worker Flask route", test_service_worker_route),
        ("Manifest icons", test_manifest_icons),
        ("Badge and screenshots", test_badge_and_screenshots),
        ("Duplicate beforeinstallprompt handlers", test_no_duplicate_beforeinstallprompt)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"\n❌ FAILED: {test_name}")
        except Exception as e:
            print(f"\n❌ ERROR in {test_name}: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ ALL PRODUCTION ERROR TESTS PASSED!")
        print("🎉 The app should now work without production errors.")
    else:
        print(f"❌ {total - passed} tests failed. Please fix the issues above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
