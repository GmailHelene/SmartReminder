#!/usr/bin/env python3
"""
Comprehensive Sound Notification Test for SmartReminder
-------------------------------------------------------
This script tests sound functionality through multiple channels:
1. Direct API calls to the send-test-notification endpoint
2. Browser automation to test UI sound interactions
3. Verification of sound selection in reminders

Usage:
  python3 test_notification_sounds.py [email] [password] [url]

  email: The email address to use for testing (defaults to admin@example.com)
  password: The password for the test account (defaults to admin)
  url: The base URL of the app (defaults to http://localhost:5000)
"""

import sys
import time
import json
import logging
import requests
from datetime import datetime, timedelta
import argparse
import subprocess
import os

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('sound_test.log')
    ]
)
logger = logging.getLogger(__name__)

# Default values
DEFAULT_EMAIL = "admin@example.com"
DEFAULT_PASSWORD = "admin"
DEFAULT_URL = "http://localhost:5000"
SOUNDS = ['alert.mp3', 'ding.mp3', 'chime.mp3', 'pristine.mp3']

def send_test_notification_api(session, base_url, sound, email=None):
    """Test the notification API with a specific sound"""
    try:
        logger.info(f"📱 Testing API notification with sound: {sound}")
        
        # Prepare test data
        test_data = {
            "title": f"Test Notification: {sound}",
            "message": f"This is a test notification with sound: {sound}",
            "sound": sound
        }
        if email:
            test_data["email"] = email
        
        # Send request to test notification endpoint
        response = session.post(
            f"{base_url}/api/send-test-notification",
            json=test_data
        )
        
        if response.status_code == 200 and response.json().get('success'):
            logger.info(f"✅ API test notification sent successfully with sound: {sound}")
            return True
        else:
            logger.warning(f"❌ API test notification failed: {response.status_code}")
            logger.warning(f"   Response: {response.text}")
            return False
    
    except Exception as e:
        logger.error(f"❌ Error sending API test notification: {e}")
        return False

def test_sound_test_page(session, base_url):
    """Test the dedicated sound test page if available"""
    try:
        # Try to access the sound test page
        response = session.get(f"{base_url}/sound-test")
        
        if response.status_code == 200:
            logger.info("✅ Sound test page is available")
            
            # Check if the page contains the expected sound testing elements
            expected_elements = [
                'playSound(',
                'testNotificationSound(',
                'testLocalNotification('
            ]
            
            page_content = response.text
            all_found = True
            
            for element in expected_elements:
                if element not in page_content:
                    logger.warning(f"❌ Could not find {element} in sound test page")
                    all_found = False
            
            if all_found:
                logger.info("✅ Sound test page contains all expected sound testing functions")
                return True
            else:
                logger.warning("⚠️ Sound test page is missing some expected functions")
                return False
        else:
            logger.warning(f"❌ Sound test page is not available: {response.status_code}")
            return False
    
    except Exception as e:
        logger.error(f"❌ Error accessing sound test page: {e}")
        return False

def test_sw_test_page(session, base_url):
    """Test the service worker test page if available"""
    try:
        # Try to access the SW test page
        response = session.get(f"{base_url}/sw-test")
        
        if response.status_code == 200:
            logger.info("✅ Service worker test page is available")
            return True
        else:
            logger.warning(f"❌ Service worker test page is not available: {response.status_code}")
            return False
    
    except Exception as e:
        logger.error(f"❌ Error accessing service worker test page: {e}")
        return False

def login(session, base_url, email, password):
    """Log in to the application"""
    try:
        # Get login page to capture any CSRF token
        login_page = session.get(f"{base_url}/login")
        
        # Submit login credentials
        login_data = {
            "email": email,
            "password": password,
            "remember": "on"
        }
        
        response = session.post(
            f"{base_url}/login",
            data=login_data,
            allow_redirects=True
        )
        
        # Check if login was successful by looking for dashboard in URL
        if 'dashboard' in response.url:
            logger.info(f"✅ Successfully logged in as {email}")
            return True
        else:
            logger.error(f"❌ Failed to log in as {email}")
            return False
    
    except Exception as e:
        logger.error(f"❌ Error during login: {e}")
        return False

def check_reminder_sound_options(session, base_url):
    """Check if reminder creation form has sound options"""
    try:
        # Get dashboard or add reminder page
        response = session.get(f"{base_url}/dashboard")
        
        if response.status_code == 200:
            page_content = response.text
            
            # Check for sound selection in the form
            if 'name="sound"' in page_content or 'id="sound"' in page_content:
                logger.info("✅ Reminder form has sound selection options")
                
                # Check if all sounds are available
                all_sounds_available = True
                for sound in SOUNDS:
                    sound_name = sound.replace('.mp3', '')
                    if sound_name not in page_content:
                        logger.warning(f"❌ Sound option '{sound_name}' not found in reminder form")
                        all_sounds_available = False
                
                if all_sounds_available:
                    logger.info("✅ All sound options are available in the reminder form")
                else:
                    logger.warning("⚠️ Some sound options are missing from the reminder form")
                
                return True
            else:
                logger.warning("❌ Reminder form does not have sound selection options")
                return False
        else:
            logger.error(f"❌ Failed to access dashboard: {response.status_code}")
            return False
    
    except Exception as e:
        logger.error(f"❌ Error checking reminder sound options: {e}")
        return False

def test_create_reminder_with_sound(session, base_url, sound):
    """Test creating a reminder with a specific sound"""
    try:
        # Prepare reminder data
        reminder_data = {
            "title": f"Sound Test: {sound}",
            "description": f"Testing sound: {sound}",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": (datetime.now() + timedelta(minutes=5)).strftime("%H:%M"),
            "category": "Test",
            "sound": sound
        }
        
        # Create the reminder
        response = session.post(
            f"{base_url}/add_reminder",
            json=reminder_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200 and (
            response.json().get('success') or 
            response.json().get('status') == 'success'
        ):
            logger.info(f"✅ Created reminder with sound: {sound}")
            
            # Get the reminder ID if available
            reminder_id = response.json().get('reminder_id')
            if reminder_id:
                # Clean up - delete the test reminder
                delete_response = session.get(f"{base_url}/delete_reminder/{reminder_id}")
                if delete_response.status_code == 200:
                    logger.info(f"✅ Deleted test reminder {reminder_id}")
                else:
                    logger.warning(f"⚠️ Could not delete test reminder {reminder_id}")
            
            return True
        else:
            logger.warning(f"❌ Failed to create reminder with sound: {response.status_code}")
            logger.warning(f"   Response: {response.text}")
            return False
    
    except Exception as e:
        logger.error(f"❌ Error creating reminder with sound: {e}")
        return False

def verify_sound_files_exist(session, base_url):
    """Verify that all sound files exist and are accessible"""
    all_exist = True
    
    for sound in SOUNDS:
        try:
            response = session.get(f"{base_url}/static/sounds/{sound}")
            
            if response.status_code == 200:
                logger.info(f"✅ Sound file exists: {sound}")
            else:
                logger.warning(f"❌ Sound file not found: {sound} ({response.status_code})")
                all_exist = False
        
        except Exception as e:
            logger.error(f"❌ Error checking sound file {sound}: {e}")
            all_exist = False
    
    return all_exist

def run_browser_test(base_url, email, password):
    """Run browser-based tests for sound if browser automation is available"""
    try:
        # Check if we have selenium
        subprocess.run(
            [sys.executable, "-c", "import selenium"],
            check=True,
            capture_output=True
        )
        
        # Create a simple test script for browser automation
        script_path = "browser_sound_test.py"
        with open(script_path, "w") as f:
            f.write(f"""
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Setup Chrome
options = Options()
options.add_argument("--autoplay-policy=no-user-gesture-required")
driver = webdriver.Chrome(options=options)
driver.maximize_window()

try:
    # Login
    print("Logging in...")
    driver.get("{base_url}/login")
    driver.find_element(By.NAME, "email").send_keys("{email}")
    driver.find_element(By.NAME, "password").send_keys("{password}")
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    
    # Wait for dashboard
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "dashboard"))
    )
    print("Logged in successfully")
    
    # Test sound page if available
    try:
        driver.get("{base_url}/sound-test")
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(@onclick, 'playSound')]"))
        )
        print("Testing sounds on sound-test page")
        
        # Set user interaction flag
        driver.execute_script("window.userInteracted = true;")
        
        # Test direct sound playback
        sounds = ['pristine.mp3', 'ding.mp3', 'chime.mp3', 'alert.mp3']
        for sound in sounds:
            button = driver.find_element(By.XPATH, f"//button[contains(@onclick, 'playSound(\\\"{sound}\\\"')")]
            print(f"Testing direct sound: {{sound}}")
            button.click()
            time.sleep(2)
        
        # Test notification sounds
        for sound in sounds:
            button = driver.find_element(By.XPATH, f"//button[contains(@onclick, 'testNotificationSound(\\\"{sound}\\\"')")]
            print(f"Testing notification sound: {{sound}}")
            button.click()
            time.sleep(2)
    except Exception as e:
        print(f"Error testing sound-test page: {{e}}")
    
    # Test dashboard sound preview if available
    try:
        driver.get("{base_url}/dashboard")
        print("Testing sounds on dashboard")
        
        # Set user interaction flag
        driver.execute_script("window.userInteracted = true;")
        
        # Test previewSound function if available
        sounds = ['pristine.mp3', 'ding.mp3', 'chime.mp3', 'alert.mp3']
        for sound in sounds:
            print(f"Testing preview sound: {{sound}}")
            driver.execute_script(f"previewSound('{{sound}}')")
            time.sleep(2)
    except Exception as e:
        print(f"Error testing dashboard sounds: {{e}}")
        
except Exception as e:
    print(f"Browser test error: {{e}}")
finally:
    print("Completed browser sound tests")
    driver.quit()
""")
        
        # Run the browser test
        logger.info("Running browser automation test...")
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True
        )
        
        # Display results
        logger.info("Browser test output:")
        for line in result.stdout.split("\n"):
            if line.strip():
                logger.info(f"  {line}")
        
        # Clean up
        os.remove(script_path)
        
        return "Error" not in result.stdout
    
    except subprocess.CalledProcessError:
        logger.warning("Selenium not available, skipping browser tests")
        return False
    except Exception as e:
        logger.error(f"Error running browser tests: {e}")
        return False

def main():
    """Main function to run all sound tests"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Test notification sounds in SmartReminder")
    parser.add_argument("--email", default=DEFAULT_EMAIL, help="Email for login")
    parser.add_argument("--password", default=DEFAULT_PASSWORD, help="Password for login")
    parser.add_argument("--url", default=DEFAULT_URL, help="Base URL of the application")
    parser.add_argument("--skip-browser", action="store_true", help="Skip browser automation tests")
    parser.add_argument("--sound", help="Test only a specific sound")
    args = parser.parse_args()
    
    # Use positional arguments if provided
    if len(sys.argv) > 1 and not sys.argv[1].startswith('--'):
        args.email = sys.argv[1]
    if len(sys.argv) > 2 and not sys.argv[2].startswith('--'):
        args.password = sys.argv[2]
    if len(sys.argv) > 3 and not sys.argv[3].startswith('--'):
        args.url = sys.argv[3]
    
    print("🔊 SmartReminder - Comprehensive Sound Test")
    print("==========================================")
    print(f"Testing URL: {args.url}")
    print(f"Login: {args.email}")
    
    # Create session for maintaining cookies
    session = requests.Session()
    
    # Track test results
    results = {
        "login": False,
        "sound_files": False,
        "sound_test_page": False,
        "sw_test_page": False,
        "api_notifications": [],
        "reminder_sound_options": False,
        "create_reminders": [],
        "browser_tests": False
    }
    
    # Step 1: Login
    results["login"] = login(session, args.url, args.email, args.password)
    if not results["login"]:
        logger.error("❌ Login failed, cannot continue with tests")
        return
    
    # Step 2: Verify sound files exist
    results["sound_files"] = verify_sound_files_exist(session, args.url)
    
    # Step 3: Check sound test pages
    results["sound_test_page"] = test_sound_test_page(session, args.url)
    results["sw_test_page"] = test_sw_test_page(session, args.url)
    
    # Step 4: Test API notifications with sounds
    sounds_to_test = [args.sound] if args.sound else SOUNDS
    
    for sound in sounds_to_test:
        success = send_test_notification_api(session, args.url, sound)
        results["api_notifications"].append({"sound": sound, "success": success})
        time.sleep(2)  # Wait between notifications
    
    # Step 5: Check reminder sound options
    results["reminder_sound_options"] = check_reminder_sound_options(session, args.url)
    
    # Step 6: Test creating reminders with sounds
    for sound in sounds_to_test:
        success = test_create_reminder_with_sound(session, args.url, sound)
        results["create_reminders"].append({"sound": sound, "success": success})
    
    # Step 7: Run browser tests if not skipped
    if not args.skip_browser:
        results["browser_tests"] = run_browser_test(args.url, args.email, args.password)
    
    # Print summary
    print("\n📝 Test Results Summary:")
    print(f"  Login: {'✅' if results['login'] else '❌'}")
    print(f"  Sound Files: {'✅' if results['sound_files'] else '❌'}")
    print(f"  Sound Test Page: {'✅' if results['sound_test_page'] else '❌'}")
    print(f"  Service Worker Test Page: {'✅' if results['sw_test_page'] else '❌'}")
    
    print("  API Notifications:")
    for result in results["api_notifications"]:
        print(f"    {result['sound']}: {'✅' if result['success'] else '❌'}")
    
    print(f"  Reminder Sound Options: {'✅' if results['reminder_sound_options'] else '❌'}")
    
    print("  Create Reminders with Sound:")
    for result in results["create_reminders"]:
        print(f"    {result['sound']}: {'✅' if result['success'] else '❌'}")
    
    if not args.skip_browser:
        print(f"  Browser Tests: {'✅' if results['browser_tests'] else '❌'}")
    
    # Overall assessment
    api_success = all(result["success"] for result in results["api_notifications"])
    reminder_success = all(result["success"] for result in results["create_reminders"])
    
    print("\n🔊 Sound Notification Test Assessment:")
    if results["sound_files"] and api_success and reminder_success:
        print("✅ Sound notifications are working properly!")
    else:
        print("⚠️ Some sound notification tests failed. Check the logs for details.")
    
    print("\n📝 Testing Tips:")
    print("  - Make sure the device is not on silent mode")
    print("  - Check that notifications are enabled for the app")
    print("  - Test with the app in foreground, background, and closed")
    print("  - On iOS, user interaction may be required to play sounds")
    print("  - For mobile devices, test using the actual device, not just emulators")

if __name__ == "__main__":
    main()
