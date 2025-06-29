#!/usr/bin/env python3
"""Test calendar API endpoint to debug loading issues"""

import requests
import json
from app import app
from werkzeug.test import Client
import os

def test_calendar_api():
    """Test the calendar API endpoint directly"""
    print("Testing calendar API endpoint...")
    
    # Test without authentication (should fail)
    with app.test_client() as client:
        response = client.get('/api/calendar-events')
        print(f"Without auth - Status: {response.status_code}")
        print(f"Response: {response.get_data(as_text=True)}")
        
        # Mock session to test with authentication
        with client.session_transaction() as sess:
            sess['_user_id'] = 'test@example.com'
            sess['_fresh'] = True
        
        response = client.get('/api/calendar-events')
        print(f"\nWith auth - Status: {response.status_code}")
        print(f"Response: {response.get_data(as_text=True)}")
        
        if response.status_code == 200:
            try:
                data = response.get_json()
                print(f"JSON data: {json.dumps(data, indent=2)}")
                print(f"Number of events: {len(data) if data else 0}")
            except Exception as e:
                print(f"Error parsing JSON: {e}")

def test_calendar_with_real_user():
    """Test with a user that might exist in the system"""
    print("\nTesting with potential real users...")
    
    # Check if any user data exists
    if os.path.exists('/workspaces/smartreminder/data/users.json'):
        with open('/workspaces/smartreminder/data/users.json', 'r') as f:
            users = json.load(f)
            print(f"Found {len(users)} users in system")
            for email in users.keys():
                print(f"User: {email}")
                
                # Test API with this user
                with app.test_client() as client:
                    with client.session_transaction() as sess:
                        sess['_user_id'] = email
                        sess['_fresh'] = True
                    
                    response = client.get('/api/calendar-events')
                    print(f"User {email} - Status: {response.status_code}")
                    
                    if response.status_code == 200:
                        try:
                            data = response.get_json()
                            print(f"Events for {email}: {len(data) if data else 0}")
                            if data:
                                print(f"First event: {data[0]}")
                        except Exception as e:
                            print(f"Error parsing JSON for {email}: {e}")
                    else:
                        print(f"Error response: {response.get_data(as_text=True)}")
                    print()

if __name__ == '__main__':
    test_calendar_api()
    test_calendar_with_real_user()
