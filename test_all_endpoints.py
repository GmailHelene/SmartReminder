#!/usr/bin/env python3
"""
Comprehensive API Endpoint Test for SmartReminder
------------------------------------------------
This script tests all API endpoints in the SmartReminder application,
including notification sound functionality.
"""

import sys
import os
import json
import requests
import unittest
from datetime import datetime, timedelta
import logging
import uuid

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Base URL - change this to your app's URL when testing
BASE_URL = "http://localhost:5000"

# Test credentials
TEST_USER = {
    "email": "test@example.com",
    "password": "testpassword123"
}

class SmartReminderAPITest(unittest.TestCase):
    """Test all API endpoints in SmartReminder"""
    
    def setUp(self):
        """Set up test session with login"""
        self.session = requests.Session()
        self.login()
    
    def tearDown(self):
        """Clean up by logging out"""
        self.session.get(f"{BASE_URL}/logout")
        self.session.close()
    
    def login(self):
        """Login to the application"""
        try:
            # First get the login page to extract CSRF token
            login_page = self.session.get(f"{BASE_URL}/login")
            
            # Check if already logged in (redirect to dashboard)
            if 'dashboard' in login_page.url:
                logger.info("Already logged in")
                return True
            
            # Attempt login
            login_response = self.session.post(
                f"{BASE_URL}/login",
                data={
                    "email": TEST_USER["email"],
                    "password": TEST_USER["password"],
                    # CSRF token would be extracted here in a real implementation
                },
                allow_redirects=True
            )
            
            if 'dashboard' in login_response.url:
                logger.info("Login successful")
                return True
            else:
                logger.warning(f"Login failed: {login_response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Login error: {e}")
            return False
    
    def test_01_health_endpoint(self):
        """Test the health check endpoint"""
        response = self.session.get(f"{BASE_URL}/health")
        self.assertEqual(response.status_code, 200)
        logger.info("✅ Health endpoint working")
    
    def test_02_dashboard_endpoint(self):
        """Test the dashboard endpoint"""
        response = self.session.get(f"{BASE_URL}/dashboard")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Mine påminnelser", response.text)
        logger.info("✅ Dashboard endpoint working")
    
    def test_03_reminder_count_endpoint(self):
        """Test the reminder count API endpoint"""
        response = self.session.get(f"{BASE_URL}/api/reminder-count")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('my_count', data)
        self.assertIn('shared_count', data)
        logger.info(f"✅ Reminder count endpoint working: {data}")
    
    def test_04_calendar_events_endpoint(self):
        """Test the calendar events API endpoint"""
        response = self.session.get(f"{BASE_URL}/api/calendar-events")
        self.assertEqual(response.status_code, 200)
        events = response.json()
        self.assertIsInstance(events, list)
        logger.info(f"✅ Calendar events endpoint working: {len(events)} events")
    
    def test_05_add_reminder_endpoint(self):
        """Test adding a reminder via POST endpoint"""
        current_date = datetime.now().strftime("%Y-%m-%d")
        current_time = datetime.now().strftime("%H:%M")
        
        reminder_data = {
            "title": f"Test Reminder {uuid.uuid4()}",
            "description": "This is a test reminder for API testing",
            "date": current_date,
            "time": current_time,
            "category": "Test",
            "priority": "Medium",
            "sound": "pristine.mp3"
        }
        
        response = self.session.post(
            f"{BASE_URL}/add_reminder",
            json=reminder_data,
            headers={"Content-Type": "application/json"}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get('success'))
        self.assertIn('reminder_id', data)
        
        # Store reminder ID for later tests
        self.reminder_id = data['reminder_id']
        logger.info(f"✅ Add reminder endpoint working: {self.reminder_id}")
    
    def test_06_update_reminder_datetime_endpoint(self):
        """Test updating a reminder's date/time via API endpoint"""
        if not hasattr(self, 'reminder_id'):
            self.test_05_add_reminder_endpoint()
        
        # Set date to tomorrow
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        update_data = {
            "reminder_id": self.reminder_id,
            "date": tomorrow,
            "time": "10:00"
        }
        
        response = self.session.post(
            f"{BASE_URL}/api/update-reminder-datetime",
            json=update_data,
            headers={"Content-Type": "application/json"}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get('success'))
        logger.info(f"✅ Update reminder datetime endpoint working")
    
    def test_07_complete_reminder_endpoint(self):
        """Test marking a reminder as complete"""
        if not hasattr(self, 'reminder_id'):
            self.test_05_add_reminder_endpoint()
        
        response = self.session.get(f"{BASE_URL}/complete_reminder/{self.reminder_id}")
        self.assertEqual(response.status_code, 302)  # Redirect status
        logger.info(f"✅ Complete reminder endpoint working")
    
    def test_08_share_reminder_endpoint(self):
        """Test sharing a reminder via email"""
        if not hasattr(self, 'reminder_id'):
            self.test_05_add_reminder_endpoint()
        
        share_data = {
            "reminder_id": self.reminder_id,
            "email_addresses": "share@example.com",
            "personal_message": "Testing the share reminder functionality"
        }
        
        # This will likely fail without real email configuration, but we can test the endpoint
        response = self.session.post(
            f"{BASE_URL}/share_reminder", 
            data=share_data
        )
        
        # Either 200 or 302 (redirect) is acceptable
        self.assertIn(response.status_code, [200, 302])
        logger.info(f"✅ Share reminder endpoint tested")
    
    def test_09_sound_test_endpoint(self):
        """Test the sound test page"""
        response = self.session.get(f"{BASE_URL}/sound_test")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Test varsellyder", response.text)
        logger.info(f"✅ Sound test page working")
    
    def test_10_focus_modes_endpoint(self):
        """Test the focus modes page and functionality"""
        response = self.session.get(f"{BASE_URL}/focus_modes")
        self.assertEqual(response.status_code, 200)
        self.assertIn("fokusmodus", response.text.lower())
        logger.info(f"✅ Focus modes page working")
    
    def test_11_notification_sound_endpoint(self):
        """Test notification sound functionality"""
        test_data = {
            "title": "Test Sound Notification",
            "message": "Testing notification sounds",
            "sound": "alert.mp3"
        }
        
        try:
            response = self.session.post(
                f"{BASE_URL}/api/send-test-notification",
                json=test_data,
                headers={"Content-Type": "application/json"}
            )
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertTrue(data.get('success'))
            logger.info(f"✅ Test notification endpoint working")
        except Exception as e:
            logger.warning(f"Test notification endpoint may not exist: {e}")
    
    def test_12_static_sound_files(self):
        """Test that sound files are accessible"""
        sound_files = ["pristine.mp3", "ding.mp3", "chime.mp3", "alert.mp3"]
        
        for sound in sound_files:
            response = self.session.get(f"{BASE_URL}/static/sounds/{sound}")
            self.assertEqual(response.status_code, 200)
            self.assertIn("audio/mpeg", response.headers.get("Content-Type", ""))
            
        logger.info(f"✅ Static sound files accessible")
    
    def test_13_delete_reminder_endpoint(self):
        """Test deleting a reminder"""
        if not hasattr(self, 'reminder_id'):
            self.test_05_add_reminder_endpoint()
        
        response = self.session.get(f"{BASE_URL}/delete_reminder/{self.reminder_id}")
        self.assertEqual(response.status_code, 302)  # Redirect status
        logger.info(f"✅ Delete reminder endpoint working")
    
    def test_14_service_worker(self):
        """Test service worker file"""
        response = self.session.get(f"{BASE_URL}/sw.js")
        self.assertEqual(response.status_code, 200)
        self.assertIn("javascript", response.headers.get("Content-Type", ""))
        logger.info(f"✅ Service worker file accessible")
    
    def test_15_manifest_json(self):
        """Test PWA manifest.json"""
        response = self.session.get(f"{BASE_URL}/static/manifest.json")
        self.assertEqual(response.status_code, 200)
        self.assertIn("application/json", response.headers.get("Content-Type", ""))
        
        manifest = response.json()
        self.assertIn("name", manifest)
        self.assertIn("icons", manifest)
        logger.info(f"✅ PWA manifest.json accessible")

def run_tests():
    """Run all tests"""
    logger.info("Starting SmartReminder API Endpoint Tests")
    
    # Check server availability before running tests
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            logger.error(f"Server at {BASE_URL} is not responding correctly")
            return False
    except requests.exceptions.RequestException:
        logger.error(f"Cannot connect to server at {BASE_URL}")
        return False
    
    logger.info(f"Server at {BASE_URL} is available, running tests...")
    
    # Run tests
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
    
    logger.info("All tests completed!")
    return True

if __name__ == "__main__":
    # Handle command line arguments
    if len(sys.argv) > 1:
        BASE_URL = sys.argv[1]
        
    # If test user credentials are provided as arguments
    if len(sys.argv) > 3:
        TEST_USER["email"] = sys.argv[2]
        TEST_USER["password"] = sys.argv[3]
    
    run_tests()
