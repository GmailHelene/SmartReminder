#!/usr/bin/env python3
"""Test noteboard with actual data"""

import os
import sys
import json

# Set up the environment
os.environ['FLASK_ENV'] = 'development'
os.environ['TESTING'] = '1'

try:
    from app import app, dm, noteboard_manager
    from flask_login import login_user
    
    print("✅ App imported successfully")
    
    # Create test data
    with app.app_context():
        # Create a test user
        users = dm.load_data('users')
        if not isinstance(users, dict):
            users = {}
        
        test_user_id = 'test-user-123'
        users[test_user_id] = {
            'username': 'test@example.com',
            'email': 'test@example.com',
            'password_hash': 'dummy-hash',
            'created': '2024-01-01T00:00:00'
        }
        dm.save_data('users', users)
        
        # Create a test noteboard
        boards = dm.load_data('shared_noteboards')
        if not isinstance(boards, dict):
            boards = {}
        
        test_board_id = 'test-board-123'
        boards[test_board_id] = {
            'board_id': test_board_id,
            'title': 'Test Board',
            'description': 'Test board for debugging',
            'created_by': 'test@example.com',
            'access_code': 'TEST123',
            'members': ['test@example.com'],
            'notes': [
                {
                    'id': 'note-1',
                    'content': 'This is a test note\nWith multiple lines\nTo test nl2br filter',
                    'color': 'warning',
                    'author': 'test@example.com',
                    'created': '2024-01-01T00:00:00',
                    'position': {'x': 100, 'y': 100}
                }
            ],
            'created': '2024-01-01T00:00:00'
        }
        dm.save_data('shared_noteboards', boards)
        
        print("✅ Test data created")
        
        # Test the noteboard route with real data
        with app.test_client() as client:
            # Mock login
            with client.session_transaction() as sess:
                sess['user_id'] = test_user_id
                sess['_fresh'] = True
            
            print(f"\n🧪 Testing noteboard route with real data...")
            response = client.get(f'/noteboard/{test_board_id}')
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 500:
                print("❌ 500 Error occurred!")
                error_text = response.get_data(as_text=True)
                print("Error details:")
                print(error_text[:1000])
                
                # Look for the specific nl2br error
                if 'nl2br' in error_text:
                    print("\n🎯 Found nl2br error in response!")
                else:
                    print("\n❓ No nl2br error found, different issue")
            else:
                print("✅ Response looks OK")
                # Check if nl2br actually worked
                response_text = response.get_data(as_text=True)
                if '<br>' in response_text:
                    print("✅ Found <br> tags, nl2br filter worked")
                else:
                    print("❓ No <br> tags found, but no error either")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
