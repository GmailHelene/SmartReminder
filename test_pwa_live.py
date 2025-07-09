#!/usr/bin/env python3
"""
Test PWA live functionality - start app and test PWA features
"""

import subprocess
import time
import requests
import json
import os
import signal

def test_pwa_live():
    """Test PWA functionality on live app"""
    
    print("🚀 Testing PWA live functionality...")
    
    # Start the Flask app in the background
    print("\n1. Starting Flask app...")
    
    # Try to start the app
    app_process = None
    try:
        app_process = subprocess.Popen(
            ["python3", "app.py"], 
            cwd="/workspaces/smartreminder",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid
        )
        
        # Wait for app to start
        time.sleep(3)
        
        # Check if app is responding
        try:
            response = requests.get("http://localhost:5000", timeout=5)
            if response.status_code == 200:
                print("✅ Flask app started successfully")
            else:
                print(f"❌ Flask app returned status {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Could not connect to Flask app: {e}")
            return False
        
        # Test 2: Check manifest.json endpoint
        print("\n2. Testing manifest.json endpoint...")
        try:
            response = requests.get("http://localhost:5000/static/manifest.json", timeout=5)
            if response.status_code == 200:
                manifest = response.json()
                print("✅ Manifest accessible via HTTP")
                print(f"   - Content-Type: {response.headers.get('Content-Type', 'N/A')}")
                print(f"   - Name: {manifest.get('name', 'N/A')}")
            else:
                print(f"❌ Manifest not accessible: {response.status_code}")
        except Exception as e:
            print(f"❌ Manifest test failed: {e}")
        
        # Test 3: Check service worker endpoint
        print("\n3. Testing service worker endpoint...")
        try:
            response = requests.get("http://localhost:5000/static/js/sw.js", timeout=5)
            if response.status_code == 200:
                print("✅ Service worker accessible via HTTP")
                print(f"   - Content-Type: {response.headers.get('Content-Type', 'N/A')}")
                print(f"   - Size: {len(response.content)} bytes")
            else:
                print(f"❌ Service worker not accessible: {response.status_code}")
        except Exception as e:
            print(f"❌ Service worker test failed: {e}")
        
        # Test 4: Check PWA icons
        print("\n4. Testing PWA icons...")
        icons = ['192x192', '512x512']
        for size in icons:
            try:
                response = requests.get(f"http://localhost:5000/static/images/icon-{size}.png", timeout=5)
                if response.status_code == 200:
                    print(f"✅ Icon {size} accessible via HTTP")
                else:
                    print(f"❌ Icon {size} not accessible: {response.status_code}")
            except Exception as e:
                print(f"❌ Icon {size} test failed: {e}")
        
        # Test 5: Check offline page
        print("\n5. Testing offline page...")
        try:
            response = requests.get("http://localhost:5000/offline", timeout=5)
            if response.status_code == 200:
                print("✅ Offline page accessible")
            else:
                print(f"❌ Offline page not accessible: {response.status_code}")
        except Exception as e:
            print(f"❌ Offline page test failed: {e}")
        
        # Test 6: Check if PWA JavaScript is included in main page
        print("\n6. Testing PWA JavaScript inclusion...")
        try:
            response = requests.get("http://localhost:5000", timeout=5)
            if response.status_code == 200:
                content = response.text
                if 'pwa.js' in content:
                    print("✅ PWA JavaScript included in main page")
                else:
                    print("❌ PWA JavaScript not included in main page")
                    
                if 'sw.js' in content:
                    print("✅ Service worker registration found in main page")
                else:
                    print("❌ Service worker registration not found in main page")
            else:
                print(f"❌ Could not check main page: {response.status_code}")
        except Exception as e:
            print(f"❌ Main page test failed: {e}")
        
        print("\n" + "="*50)
        print("PWA LIVE FUNCTIONALITY TEST COMPLETE")
        print("="*50)
        
        return True
        
    except Exception as e:
        print(f"❌ Error starting app: {e}")
        return False
    
    finally:
        # Clean up - kill the app process
        if app_process:
            try:
                os.killpg(os.getpgid(app_process.pid), signal.SIGTERM)
                app_process.wait(timeout=5)
                print("\n✅ Flask app stopped")
            except:
                try:
                    os.killpg(os.getpgid(app_process.pid), signal.SIGKILL)
                    print("\n⚠️  Flask app force killed")
                except:
                    print("\n❌ Could not stop Flask app")

if __name__ == "__main__":
    test_pwa_live()
