#!/usr/bin/env python3
"""
Test script to debug the calendar events API endpoint
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, dm
import json

def test_data_manager():
    """Test if the data manager methods work correctly"""
    print("=== Testing Data Manager ===")
    
    try:
        # Test with a dummy email
        test_email = "test@example.com"
        
        print(f"Testing with email: {test_email}")
        
        # Test get_user_reminders
        print("\n1. Testing get_user_reminders...")
        my_reminders = dm.get_user_reminders(test_email)
        print(f"   Result type: {type(my_reminders)}")
        print(f"   Result length: {len(my_reminders) if isinstance(my_reminders, list) else 'N/A'}")
        if my_reminders:
            print(f"   First reminder: {my_reminders[0] if my_reminders else 'None'}")
        
        # Test get_shared_reminders
        print("\n2. Testing get_shared_reminders...")
        shared_reminders = dm.get_shared_reminders(test_email)
        print(f"   Result type: {type(shared_reminders)}")
        print(f"   Result length: {len(shared_reminders) if isinstance(shared_reminders, list) else 'N/A'}")
        if shared_reminders:
            print(f"   First shared reminder: {shared_reminders[0] if shared_reminders else 'None'}")
            
    except Exception as e:
        print(f"   ERROR: {e}")
        import traceback
        traceback.print_exc()

def test_calendar_endpoint():
    """Test the calendar endpoint directly"""
    print("\n=== Testing Calendar Endpoint ===")
    
    with app.test_client() as client:
        with app.test_request_context():
            try:
                # Disable login requirement for testing
                app.config['LOGIN_DISABLED'] = True
                
                print("Making request to /api/calendar-events...")
                response = client.get('/api/calendar-events')
                
                print(f"Status Code: {response.status_code}")
                print(f"Content-Type: {response.content_type}")
                
                if response.status_code == 200:
                    try:
                        data = response.get_json()
                        print(f"Response data type: {type(data)}")
                        print(f"Response data length: {len(data) if isinstance(data, list) else 'N/A'}")
                        if data:
                            print(f"First event: {data[0] if data else 'None'}")
                    except Exception as e:
                        print(f"JSON parsing error: {e}")
                        print(f"Raw response: {response.get_data(as_text=True)}")
                else:
                    print(f"Error response: {response.get_data(as_text=True)}")
                    
            except Exception as e:
                print(f"Endpoint test error: {e}")
                import traceback
                traceback.print_exc()

def test_with_mock_user():
    """Test the endpoint with a mock authenticated user"""
    print("\n=== Testing with Mock User ===")
    
    try:
        from unittest.mock import patch
        
        class MockUser:
            def __init__(self, email="test@example.com"):
                self.email = email
                self.is_authenticated = True
                self.is_active = True
                self.is_anonymous = False
            
            def get_id(self):
                return self.email
        
        with app.test_client() as client:
            with app.test_request_context():
                with patch('flask_login.current_user', MockUser()):
                    print("Making authenticated request...")
                    response = client.get('/api/calendar-events')
                    
                    print(f"Status Code: {response.status_code}")
                    
                    if response.status_code == 200:
                        try:
                            data = response.get_json()
                            print(f"Success! Got {len(data) if isinstance(data, list) else 0} events")
                            if data:
                                print(f"Sample event: {data[0]}")
                        except Exception as e:
                            print(f"JSON error: {e}")
                            print(f"Raw response: {response.get_data(as_text=True)}")
                    else:
                        print(f"Error: {response.get_data(as_text=True)}")
                        
    except Exception as e:
        print(f"Mock user test error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Calendar Debug Test")
    print("==================")
    
    test_data_manager()
    test_calendar_endpoint()
    test_with_mock_user()
    
    print("\n=== Test Complete ===")
