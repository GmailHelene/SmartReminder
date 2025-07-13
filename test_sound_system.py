#!/usr/bin/env python3
"""
Comprehensive Sound System Test for SmartReminder
Tests all aspects of the sound system including file creation, playback, and notifications
"""

import os
import sys
import json
import time
from pathlib import Path

def test_sound_files():
    """Test if sound files exist and are valid"""
    print("🔊 Testing sound files...")
    
    sounds_dir = Path('static/sounds')
    required_sounds = ['alert.mp3', 'ding.mp3', 'chime.mp3', 'pristine.mp3']
    
    if not sounds_dir.exists():
        print(f"❌ Sounds directory not found: {sounds_dir}")
        return False
    
    found_sounds = []
    for sound_file in required_sounds:
        # Check for both MP3 and WAV versions
        mp3_path = sounds_dir / sound_file
        wav_path = sounds_dir / sound_file.replace('.mp3', '.wav')
        
        if mp3_path.exists():
            size = mp3_path.stat().st_size
            print(f"  ✅ {sound_file} (MP3, {size} bytes)")
            found_sounds.append(sound_file)
        elif wav_path.exists():
            size = wav_path.stat().st_size
            print(f"  ✅ {sound_file.replace('.mp3', '.wav')} (WAV, {size} bytes)")
            found_sounds.append(sound_file)
        else:
            print(f"  ❌ {sound_file} not found")
    
    print(f"\nFound {len(found_sounds)}/{len(required_sounds)} sound files")
    return len(found_sounds) >= 2  # At least 2 sounds needed

def test_service_worker_sound():
    """Test service worker sound handling"""
    print("\n🔧 Testing service worker sound handling...")
    
    sw_path = Path('sw.js')
    if not sw_path.exists():
        print("❌ Service worker file not found")
        return False
    
    with open(sw_path, 'r') as f:
        sw_content = f.read()
    
    required_features = [
        ("Push event listener", "addEventListener('push'"),
        ("Sound message handling", "PLAY_NOTIFICATION_SOUND"),
        ("Client communication", "postMessage"),
        ("Sound data extraction", "data.sound")
    ]
    
    all_present = True
    for name, feature in required_features:
        if feature in sw_content:
            print(f"  ✅ {name}: Found")
        else:
            print(f"  ❌ {name}: Missing")
            all_present = False
    
    return all_present

def test_app_js_sound():
    """Test app.js sound handling"""
    print("\n📱 Testing app.js sound handling...")
    
    app_js_path = Path('static/js/app.js')
    if not app_js_path.exists():
        print("❌ app.js file not found")
        return False
    
    with open(app_js_path, 'r') as f:
        app_js_content = f.read()
    
    required_features = [
        ("playNotificationSound function", "playNotificationSound"),
        ("testSound function", "testSound"),
        ("Audio creation", "new Audio"),
        ("Fallback handling", "tryFallbackNotification"),
        ("User interaction tracking", "userInteracted"),
        ("Service worker message listener", "addEventListener('message'")
    ]
    
    all_present = True
    for name, feature in required_features:
        if feature in app_js_content:
            print(f"  ✅ {name}: Found")
        else:
            print(f"  ❌ {name}: Missing")
            all_present = False
    
    return all_present

def create_test_html():
    """Create a test HTML file for manual sound testing"""
    print("\n🌐 Creating test HTML file...")
    
    test_html = """
<!DOCTYPE html>
<html>
<head>
    <title>SmartReminder Sound Test</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; background: #f5f5f5; }
        .container { max-width: 600px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }
        button { margin: 10px; padding: 15px 25px; font-size: 16px; border: none; border-radius: 5px; cursor: pointer; }
        .test-btn { background: #007bff; color: white; }
        .test-btn:hover { background: #0056b3; }
        .status { margin: 15px 0; padding: 15px; border-radius: 5px; font-weight: bold; }
        .success { background: #d4edda; color: #155724; }
        .error { background: #f8d7da; color: #721c24; }
        .info { background: #d1ecf1; color: #0c5460; }
        .warning { background: #fff3cd; color: #856404; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔊 SmartReminder Sound System Test</h1>
        <p>Test notification sounds by clicking the buttons below:</p>
        
        <div id="status" class="status info">Click any button to test sound playback</div>
        
        <h3>Individual Sound Tests:</h3>
        <button class="test-btn" onclick="testSound('alert.mp3')">🚨 Alert Sound</button>
        <button class="test-btn" onclick="testSound('ding.mp3')">🔔 Ding Sound</button>
        <button class="test-btn" onclick="testSound('chime.mp3')">🎵 Chime Sound</button>
        <button class="test-btn" onclick="testSound('pristine.mp3')">✨ Pristine Sound</button>
        
        <h3>System Tests:</h3>
        <button class="test-btn" onclick="testNotification()">📢 Test Browser Notification</button>
        <button class="test-btn" onclick="testVibration()">📳 Test Vibration</button>
        <button class="test-btn" onclick="testAllSounds()">🎼 Test All Sounds</button>
        
        <h3>Advanced Tests:</h3>
        <button class="test-btn" onclick="testServiceWorkerSound()">🔧 Test Service Worker Sound</button>
        <button class="test-btn" onclick="requestNotificationPermission()">🔔 Request Permissions</button>
        
        <h3>Debug Information:</h3>
        <div id="debug-info">
            <p><strong>User Agent:</strong> <span id="user-agent"></span></p>
            <p><strong>Notification Support:</strong> <span id="notification-support"></span></p>
            <p><strong>Service Worker Support:</strong> <span id="sw-support"></span></p>
            <p><strong>Vibration Support:</strong> <span id="vibration-support"></span></p>
            <p><strong>User Interaction:</strong> <span id="user-interaction">No</span></p>
        </div>
        
        <h3>Troubleshooting:</h3>
        <ul>
            <li>Make sure your browser allows audio playback</li>
            <li>Check that your device volume is turned up</li>
            <li>Try clicking a button to enable audio (user interaction required)</li>
            <li>On mobile, make sure the device is not in silent mode</li>
            <li>Check browser console for any error messages</li>
        </ul>
    </div>

    <script>
        // Global variables
        window.userInteracted = false;
        
        function updateStatus(message, type = 'info') {
            const status = document.getElementById('status');
            status.textContent = message;
            status.className = 'status ' + type;
        }

        function testSound(soundFile) {
            updateStatus('🎵 Testing ' + soundFile + '...', 'info');
            window.userInteracted = true;
            document.getElementById('user-interaction').textContent = 'Yes';
            
            const audioFormats = [
                '/static/sounds/' + soundFile,
                '/static/sounds/' + soundFile.replace('.mp3', '.wav'),
                'sounds/' + soundFile
            ];
            
            let audioLoaded = false;
            let attempts = 0;
            
            function tryNextFormat() {
                if (attempts >= audioFormats.length || audioLoaded) {
                    if (!audioLoaded) {
                        updateStatus('❌ All audio formats failed for ' + soundFile, 'error');
                        tryFallback();
                    }
                    return;
                }
                
                const audioPath = audioFormats[attempts];
                console.log('Trying: ' + audioPath);
                
                const audio = new Audio();
                audio.volume = 0.7;
                
                audio.addEventListener('canplaythrough', () => {
                    if (!audioLoaded) {
                        audioLoaded = true;
                        audio.play().then(() => {
                            updateStatus('✅ Sound played successfully: ' + soundFile, 'success');
                        }).catch(error => {
                            updateStatus('❌ Failed to play ' + soundFile + ': ' + error.message, 'error');
                        });
                    }
                }, { once: true });
                
                audio.addEventListener('error', (error) => {
                    console.warn('Audio error for ' + audioPath + ':', error);
                    attempts++;
                    setTimeout(tryNextFormat, 100);
                });
                
                audio.src = audioPath;
                audio.load();
                
                // Timeout fallback
                setTimeout(() => {
                    if (!audioLoaded) {
                        attempts++;
                        tryNextFormat();
                    }
                }, 2000);
            }
            
            tryNextFormat();
        }
        
        function tryFallback() {
            console.log('Trying fallback methods...');
            
            // Try vibration
            if ('vibrate' in navigator) {
                navigator.vibrate([200, 100, 200]);
                updateStatus('📳 Vibration triggered as fallback', 'warning');
            } else {
                updateStatus('❌ No fallback methods available', 'error');
            }
        }

        function testNotification() {
            if ('Notification' in window) {
                if (Notification.permission === 'granted') {
                    new Notification('🔔 Test Notification', {
                        body: 'This is a test notification from SmartReminder',
                        icon: '/static/images/icon-96x96.png'
                    });
                    updateStatus('✅ Notification sent', 'success');
                } else if (Notification.permission !== 'denied') {
                    Notification.requestPermission().then(permission => {
                        if (permission === 'granted') {
                            new Notification('🔔 Test Notification', {
                                body: 'This is a test notification from SmartReminder',
                                icon: '/static/images/icon-96x96.png'
                            });
                            updateStatus('✅ Notification permission granted and sent', 'success');
                        } else {
                            updateStatus('❌ Notification permission denied', 'error');
                        }
                    });
                } else {
                    updateStatus('❌ Notifications are blocked', 'error');
                }
            } else {
                updateStatus('❌ This browser does not support notifications', 'error');
            }
        }

        function testVibration() {
            if ('vibrate' in navigator) {
                navigator.vibrate([200, 100, 200]);
                updateStatus('✅ Vibration triggered', 'success');
            } else {
                updateStatus('❌ This device does not support vibration', 'error');
            }
        }
        
        function testAllSounds() {
            const sounds = ['alert.mp3', 'ding.mp3', 'chime.mp3', 'pristine.mp3'];
            let index = 0;
            
            function testNext() {
                if (index < sounds.length) {
                    testSound(sounds[index]);
                    index++;
                    setTimeout(testNext, 3000);
                }
            }
            
            testNext();
        }
        
        function testServiceWorkerSound() {
            if ('serviceWorker' in navigator) {
                navigator.serviceWorker.ready.then(registration => {
                    // Send test message to service worker
                    registration.active.postMessage({
                        type: 'PLAY_NOTIFICATION_SOUND',
                        sound: 'pristine.mp3'
                    });
                    updateStatus('📧 Message sent to service worker', 'info');
                }).catch(error => {
                    updateStatus('❌ Service worker not ready: ' + error.message, 'error');
                });
            } else {
                updateStatus('❌ Service workers not supported', 'error');
            }
        }
        
        function requestNotificationPermission() {
            if ('Notification' in window) {
                Notification.requestPermission().then(permission => {
                    updateStatus('🔔 Permission result: ' + permission, permission === 'granted' ? 'success' : 'warning');
                });
            } else {
                updateStatus('❌ Notifications not supported', 'error');
            }
        }

        // Initialize debug info
        document.addEventListener('DOMContentLoaded', function() {
            document.getElementById('user-agent').textContent = navigator.userAgent;
            document.getElementById('notification-support').textContent = 'Notification' in window ? 'Yes' : 'No';
            document.getElementById('sw-support').textContent = 'serviceWorker' in navigator ? 'Yes' : 'No';
            document.getElementById('vibration-support').textContent = 'vibrate' in navigator ? 'Yes' : 'No';
            
            updateStatus('Ready for testing! Click any button above.', 'info');
        });
        
        // Track user interaction
        ['click', 'touchstart'].forEach(event => {
            document.addEventListener(event, () => {
                window.userInteracted = true;
                document.getElementById('user-interaction').textContent = 'Yes';
            }, { once: true });
        });
    </script>
</body>
</html>
    """
    
    test_file = Path('sound_test.html')
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_html)
    
    print(f"✅ Created test file: {test_file}")
    return True

def run_comprehensive_sound_test():
    """Run all sound system tests"""
    print("=" * 80)
    print(" COMPREHENSIVE SOUND SYSTEM TEST ".center(80, "="))
    print("=" * 80)
    
    # Test 1: Sound files
    sounds_ok = test_sound_files()
    
    # Test 2: Service worker
    sw_ok = test_service_worker_sound()
    
    # Test 3: App.js
    app_js_ok = test_app_js_sound()
    
    # Test 4: Create test HTML
    test_html_ok = create_test_html()
    
    # Summary
    print("\n" + "=" * 80)
    print(" TEST SUMMARY ".center(80, "="))
    print("=" * 80)
    print(f"Sound files: {'✅ OK' if sounds_ok else '❌ Issues found'}")
    print(f"Service worker: {'✅ OK' if sw_ok else '❌ Issues found'}")
    print(f"App.js: {'✅ OK' if app_js_ok else '❌ Issues found'}")
    print(f"Test HTML: {'✅ Created' if test_html_ok else '❌ Failed'}")
    
    if sounds_ok and sw_ok and app_js_ok:
        print("\n🎉 ALL TESTS PASSED!")
        print("💡 Next steps:")
        print("1. Open sound_test.html in your browser")
        print("2. Test each sound manually")
        print("3. Check browser console for any errors")
        print("4. Test on mobile devices")
    else:
        print("\n⚠️ Some tests failed. Issues to fix:")
        if not sounds_ok:
            print("  - Run: python3 create_sound_files.py")
        if not sw_ok:
            print("  - Check service worker sound handling code")
        if not app_js_ok:
            print("  - Check app.js sound functions")
    
    return sounds_ok and sw_ok and app_js_ok

if __name__ == "__main__":
    run_comprehensive_sound_test()
