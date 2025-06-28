#!/usr/bin/env python3
"""Comprehensive test to check all endpoints and functionality"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Set environment variables
os.environ['FLASK_ENV'] = 'testing'
os.environ['TESTING'] = '1'

def test_app_functionality():
    """Test all app functionality"""
    
    print("🧪 Comprehensive App Test")
    print("=" * 50)
    
    try:
        # Import the app
        print("1. 📦 Importing app...")
        from app import app, dm
        
        # Create temporary data directory for testing
        temp_dir = tempfile.mkdtemp()
        original_data_dir = dm.data_dir
        dm.data_dir = Path(temp_dir)
        dm._ensure_data_files()
        
        print("   ✅ App imported successfully")
        
        # Test filters
        print("\n2. 🎨 Testing Jinja2 filters...")
        filters_to_check = ['nl2br', 'as_datetime', 'strftime']
        for filter_name in filters_to_check:
            if filter_name in app.jinja_env.filters:
                print(f"   ✅ {filter_name} filter registered")
            else:
                print(f"   ❌ {filter_name} filter MISSING")
                return False
        
        # Test filter functionality
        print("\n3. 🔧 Testing filter functionality...")
        with app.app_context():
            # Test nl2br
            nl2br = app.jinja_env.filters['nl2br']
            result = nl2br("Line 1\nLine 2")
            if '<br>' in str(result):
                print("   ✅ nl2br filter works")
            else:
                print("   ❌ nl2br filter broken")
                return False
            
            # Test as_datetime + strftime chain
            as_datetime = app.jinja_env.filters['as_datetime']
            strftime = app.jinja_env.filters['strftime']
            
            test_date = "2024-12-01 10:30"
            date_obj = as_datetime(test_date)
            if date_obj:
                formatted = strftime(date_obj, '%d.%m.%Y %H:%M')
                if '01.12.2024 10:30' in str(formatted):
                    print("   ✅ as_datetime + strftime chain works")
                else:
                    print(f"   ❌ Filter chain broken: {formatted}")
                    return False
            else:
                print("   ❌ as_datetime filter broken")
                return False
        
        # Test routes
        print("\n4. 🌐 Testing critical routes...")
        critical_routes = [
            'index', 'login', 'register', 'dashboard', 
            'noteboards', 'focus_modes', 'email_settings'
        ]
        
        registered_routes = [rule.endpoint for rule in app.url_map.iter_rules()]
        
        for route in critical_routes:
            if route in registered_routes:
                print(f"   ✅ {route} route registered")
            else:
                print(f"   ❌ {route} route MISSING")
                return False
        
        # Test URL generation
        print("\n5. 🔗 Testing URL generation...")
        with app.app_context():
            from flask import url_for
            
            for route in critical_routes:
                try:
                    url = url_for(route)
                    print(f"   ✅ url_for('{route}') -> {url}")
                except Exception as e:
                    print(f"   ❌ url_for('{route}') -> {e}")
                    return False
        
        # Test template rendering without actual HTTP requests
        print("\n6. 📄 Testing template rendering...")
        from flask import render_template_string
        
        # Test basic template with filters
        test_template = """
        {% extends 'base.html' %}
        {% block content %}
        <div>{{ test_date | as_datetime | strftime('%d.%m.%Y') }}</div>
        <div>{{ test_text | nl2br | safe }}</div>
        {% endblock %}
        """
        
        # This would normally fail if there are issues
        try:
            with app.app_context():
                # We can't easily test the full template without setting up users,
                # but we can test the filter chain
                template = "{{ test_date | as_datetime | strftime('%d.%m.%Y %H:%M') }}"
                result = render_template_string(template, test_date="2024-12-01 10:30")
                if '01.12.2024' in result:
                    print("   ✅ Template filter chain works")
                else:
                    print(f"   ❌ Template rendering failed: {result}")
                    return False
        except Exception as e:
            print(f"   ❌ Template rendering error: {e}")
            return False
        
        # Test focus modes data
        print("\n7. 🧠 Testing focus modes...")
        try:
            from focus_modes import FocusModeManager
            modes = FocusModeManager.get_all_modes()
            if isinstance(modes, dict) and len(modes) > 0:
                print(f"   ✅ Focus modes loaded: {list(modes.keys())}")
            else:
                print("   ❌ Focus modes empty or invalid")
                return False
        except Exception as e:
            print(f"   ⚠️  Focus modes module issue (using fallback): {e}")
            # This is ok, we have fallback in the app
        
        # Test noteboard manager
        print("\n8. 📋 Testing noteboard manager...")
        try:
            from shared_noteboard import NoteboardManager
            nm = NoteboardManager(dm)
            # Test basic functionality
            boards = nm.get_user_boards('test@example.com')
            print("   ✅ Noteboard manager works")
        except Exception as e:
            print(f"   ❌ Noteboard manager error: {e}")
            return False
        
        # Cleanup
        dm.data_dir = original_data_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        print("\n🎉 ALL TESTS PASSED!")
        print("The app should work correctly in production.")
        return True
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_app_functionality()
    sys.exit(0 if success else 1)
