#!/usr/bin/env python3
"""
Test sound playback functionality
This script tests if sound files can be played and if the notification system works
"""

import os
import sys
import json
import time
from pathlib import Path
import webbrowser
import subprocess

def check_sound_files():
    """Check if sound files exist and are valid"""
    print("🔊 Checking sound files...")
    
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

def test_with_browser():
    """Test sound playback using browser"""
    print("\n🌐 Testing sound playback in browser...")
    
    # Create a simple HTML test page
    test_html = """
<!DOCTYPE html>
<html>
<head>
    <title>SmartReminder Sound Test</title>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; background: #f5f5f5; }
        .container { max-width: 600px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }
        button { margin: 10px; padding: 10px 20px; font-size: 16px; border: none; border-radius: 5px; cursor: pointer; }
        .test-btn { background: #007bff; color: white; }
        .test-btn:hover { background: #0056b3; }
        .status { margin: 10px 0; padding: 10px; border-radius: 5px; }
        .success { background: #d4edda; color: #155724; }
        .error { background: #f8d7da; color: #721c24; }
        .info { background: #d1ecf1; color: #0c5460; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔊 SmartReminder Sound Test</h1>
        <p>Test notification sounds by clicking the buttons below:</p>
        
        <div id="status" class="status info">Click any button to test sound playback</div>
        
        <button class="test-btn" onclick="testSound('alert.mp3')">🚨 Alert Sound</button>
        <button class="test-btn" onclick="testSound('ding.mp3')">🔔 Ding Sound</button>
        <button class="test-btn" onclick="testSound('chime.mp3')">🎵 Chime Sound</button>
        <button class="test-btn" onclick="testSound('pristine.mp3')">✨ Pristine Sound</button>
        
        <br><br>
        <button class="test-btn" onclick="testNotification()">📢 Test Browser Notification</button>
        <button class="test-btn" onclick="testVibration()">📳 Test Vibration</button>
        
        <h3>Troubleshooting:</h3>
        <ul>
            <li>Make sure your browser allows audio playback</li>
            <li>Check that your device volume is turned up</li>
            <li>Try clicking a button to enable audio (user interaction required)</li>
            <li>On mobile, make sure the device is not in silent mode</li>
        </ul>
    </div>

    <script>
        function updateStatus(message, type = 'info') {
            const status = document.getElementById('status');
            status.textContent = message;
            status.className = 'status ' + type;
        }

        function testSound(soundFile) {
            updateStatus('🎵 Testing ' + soundFile + '...', 'info');
            
            const audio = new Audio('/static/sounds/' + soundFile);
            audio.volume = 0.7;
            
            audio.addEventListener('canplaythrough', () => {
                audio.play().then(() => {
                    updateStatus('✅ Sound played successfully: ' + soundFile, 'success');
                }).catch(error => {
                    updateStatus('❌ Failed to play ' + soundFile + ': ' + error.message, 'error');
                    
                    // Try WAV version
                    const wavFile = soundFile.replace('.mp3', '.wav');
                    const audioWav = new Audio('/static/sounds/' + wavFile);
                    audioWav.volume = 0.7;
                    audioWav.play().then(() => {
                        updateStatus('✅ WAV version played: ' + wavFile, 'success');
                    }).catch(wavError => {
                        updateStatus('❌ Both MP3 and WAV failed for ' + soundFile, 'error');
                    });
                });
            });
            
            audio.addEventListener('error', (error) => {
                updateStatus('❌ Error loading ' + soundFile + ': ' + error.message, 'error');
            });
            
            audio.load();
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

        // Auto-test on load
        updateStatus('Ready for testing! Click any button above.', 'info');
    </script>
</body>
</html>
    """
    
    # Write test file
    test_file = Path('sound_test.html')
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_html)
    
    print(f"✅ Created test file: {test_file}")
    
    # Try to open in browser
    try:
        file_url = f"file://{os.path.abspath(test_file)}"
        print(f"🌐 Opening browser test: {file_url}")
        webbrowser.open(file_url)
        
        print("\n📋 Browser test opened!")
        print("Instructions:")
        print("1. Click the sound buttons to test each notification sound")
        print("2. Check browser console for any error messages")
        print("3. Try the notification and vibration tests")
        print("4. Close the browser when done testing")
        
        return True
    except Exception as e:
        print(f"❌ Could not open browser: {e}")
        print(f"💡 Manually open: {os.path.abspath(test_file)}")
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print(" SMARTREMINDER SOUND PLAYBACK TEST ")
    print("=" * 60)
    
    # Check if sound files exist
    sounds_exist = check_sound_files()
    
    if not sounds_exist:
        print("\n❌ Sound files missing or insufficient")
        print("💡 Run: python3 create_sound_files.py")
        return False
    
    # Test with browser
    browser_test = test_with_browser()
    
    print("\n" + "=" * 60)
    print(" TEST SUMMARY ")
    print("=" * 60)
    print(f"Sound files: {'✅ OK' if sounds_exist else '❌ Missing'}")
    print(f"Browser test: {'✅ Opened' if browser_test else '❌ Failed'}")
    
    if sounds_exist and browser_test:
        print("\n✅ Sound test setup complete!")
        print("Test the sounds in the browser window that opened.")
    else:
        print("\n⚠️ Some tests failed. Check the output above for details.")
    
    return sounds_exist and browser_test

if __name__ == "__main__":
    main()
