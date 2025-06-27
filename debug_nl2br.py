#!/usr/bin/env python3
"""Simple test to reproduce the nl2br error"""

import os
import sys

# Set up the environment to avoid import issues
os.environ['FLASK_ENV'] = 'development'
os.environ['TESTING'] = '1'

# Import the app
try:
    from app import app, dm, noteboard_manager
    print("✅ App imported successfully")
    
    # Check if nl2br filter is registered
    if 'nl2br' in app.jinja_env.filters:
        print("✅ nl2br filter is registered")
    else:
        print("❌ nl2br filter is NOT registered")
        print("Available filters:", list(app.jinja_env.filters.keys())[:10])
    
    # Try to access a noteboard route to reproduce the error
    with app.test_client() as client:
        # First create a test user session
        with client.session_transaction() as sess:
            sess['user_id'] = 'test-user'
            sess['_fresh'] = True
        
        # Test the noteboard route
        print("\n🧪 Testing noteboard route...")
        response = client.get('/noteboard/test-board')
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 500:
            print("Response data (first 500 chars):")
            print(response.get_data(as_text=True)[:500])
        else:
            print("Response looks OK")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
