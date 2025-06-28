#!/usr/bin/env python3
"""Test the template fix for dashboard.html"""

import os
os.environ['FLASK_ENV'] = 'development'
os.environ['TESTING'] = '1'

print("🧪 Testing dashboard template fix...")

try:
    from app import app
    from flask import render_template_string
    print("✅ App imported successfully")
    
    with app.app_context():
        # Test the new format_datetime filter
        if 'format_datetime' in app.jinja_env.filters:
            print("✅ format_datetime filter is registered")
        else:
            print("❌ format_datetime filter is NOT registered")
        
        # Test various datetime scenarios
        test_cases = [
            {'datetime': '2024-12-01 10:30'},      # Valid datetime string
            {'datetime': '2024-12-01T10:30:00'},   # ISO format
            {'datetime': None},                     # None value
            {'datetime': ''},                       # Empty string
            {'datetime': 'invalid'},                # Invalid string
        ]
        
        template = """{{ reminder.datetime | format_datetime }}"""
        
        for i, test_case in enumerate(test_cases):
            print(f"\nTest {i+1}: {test_case}")
            try:
                result = render_template_string(template, reminder=test_case)
                print(f"  Result: '{result.strip()}'")
                
                # Verify no template errors
                if "Error" in result or "error" in result:
                    print(f"  ⚠️  Possible error in result")
                else:
                    print(f"  ✅ No template errors")
                    
            except Exception as e:
                print(f"  ❌ Template error: {e}")
        
        # Test the actual dashboard template line that was causing issues
        print(f"\n🎯 Testing actual dashboard template syntax...")
        dashboard_template = """<span class="badge bg-primary">{{ reminder.datetime | format_datetime }}</span>"""
        
        test_reminder = {'datetime': '2024-12-01 14:30'}
        try:
            result = render_template_string(dashboard_template, reminder=test_reminder)
            print(f"Dashboard template result: '{result.strip()}'")
            
            if '01.12.2024 14:30' in result:
                print("✅ Dashboard template renders correctly!")
            else:
                print(f"⚠️  Dashboard template result: {result}")
        except Exception as e:
            print(f"❌ Dashboard template error: {e}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
