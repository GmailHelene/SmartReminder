#!/usr/bin/env python3
"""
Test the reminder count API endpoint
"""
import requests
import json

def test_reminder_count_api():
    """Test the /api/reminder-count endpoint"""
    
    try:
        # First, let's check if the server is running
        response = requests.get('http://localhost:5000/health', timeout=5)
        print(f"Health check: {response.status_code} - {response.text}")
        
        # Test the reminder count endpoint (this will require authentication)
        response = requests.get('http://localhost:5000/api/reminder-count', timeout=5)
        print(f"Reminder count API: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ API correctly requires authentication (401)")
        elif response.status_code == 200:
            data = response.json()
            print(f"✅ API response: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Flask app - is it running?")
    except requests.exceptions.Timeout:
        print("❌ Request timed out - app might be hanging")
    except Exception as e:
        print(f"❌ Error testing API: {e}")

if __name__ == "__main__":
    test_reminder_count_api()
