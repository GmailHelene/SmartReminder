#!/usr/bin/env python3
"""Comprehensive test of all endpoints and functionality"""

import os
import requests
import json
from urllib.parse import urljoin

os.environ['FLASK_ENV'] = 'development'
os.environ['TESTING'] = '1'

def test_comprehensive_functionality():
    """Test all major functionality"""
    print("🧪 Starting comprehensive functionality test...")
    
    # Start with importing the app to test basic functionality
    try:
        from app import app, dm, noteboard_manager
        print("✅ App import successful")
        
        # Test data manager
        test_data = {'test': 'data'}
        dm.save_data('test_file', test_data)
        loaded_data = dm.load_data('test_file')
        assert loaded_data == test_data
        print("✅ Data Manager works")
        
        # Test noteboard manager
        user_boards = noteboard_manager.get_user_boards('test@example.com')
        print(f"✅ Noteboard Manager works (found {len(user_boards)} boards)")
        
        # Test filters
        with app.app_context():
            filters = ['nl2br', 'as_datetime', 'strftime']
            for filter_name in filters:
                if filter_name in app.jinja_env.filters:
                    print(f"✅ {filter_name} filter registered")
                else:
                    print(f"❌ {filter_name} filter missing")
            
            # Test safe_url_for
            if 'safe_url_for' in app.jinja_env.globals:
                print("✅ safe_url_for function available")
            else:
                print("❌ safe_url_for function missing")
        
        # Test focus modes
        try:
            from focus_modes import FocusModeManager
            modes = FocusModeManager.get_all_modes()
            print(f"✅ Focus Modes loaded ({len(modes)} modes available)")
            
            # Test each mode
            for mode_key, mode in modes.items():
                print(f"  - {mode_key}: {mode.name}")
        except Exception as e:
            print(f"❌ Focus Modes error: {e}")
        
        print("\n🧪 Testing routes registration...")
        
        # Check critical routes
        critical_routes = [
            'noteboards', 'create_board', 'join_board', 'view_board',
            'dashboard', 'login', 'register', 'focus_modes',
            'email_settings', 'add_reminder'
        ]
        
        missing_routes = []
        existing_routes = [rule.endpoint for rule in app.url_map.iter_rules()]
        
        for route in critical_routes:
            if route in existing_routes:
                print(f"✅ {route} route exists")
            else:
                print(f"❌ {route} route missing")
                missing_routes.append(route)
        
        if missing_routes:
            print(f"\n⚠️ Missing routes: {missing_routes}")
        else:
            print("\n✅ All critical routes registered")
        
        # Test focus mode functionality in app
        print("\n🧪 Testing focus mode functionality...")
        
        with app.test_client() as client:
            # Test focus modes page access (should redirect to login)
            response = client.get('/focus-modes')
            if response.status_code in [200, 302]:  # 302 = redirect to login
                print("✅ Focus modes endpoint accessible")
            else:
                print(f"❌ Focus modes endpoint error: {response.status_code}")
        
        print("\n🧪 Testing template rendering...")
        
        # Test template with problematic line
        from flask import render_template_string
        test_template = """
        <span class="badge bg-primary">{{ reminder.datetime | as_datetime | strftime('%d.%m.%Y %H:%M') }}</span>
        """
        
        test_cases = [
            {'datetime': '2024-12-01 10:30'},
            {'datetime': None},
            {'datetime': ''},
        ]
        
        for i, test_case in enumerate(test_cases):
            try:
                result = render_template_string(test_template, reminder=test_case)
                print(f"✅ Template test {i+1}: {result.strip()}")
            except Exception as e:
                print(f"❌ Template test {i+1} failed: {e}")
        
        print("\n🎯 Comprehensive test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    test_comprehensive_functionality()
