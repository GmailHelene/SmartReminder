#!/usr/bin/env python3
"""Test the strftime filter fix"""

import os
os.environ['FLASK_ENV'] = 'development'
os.environ['TESTING'] = '1'

print("🧪 Testing strftime filter fix...")

try:
    from app import app
    from datetime import datetime
    
    print("✅ App imported successfully")
    
    # Test the strftime filter
    with app.app_context():
        # Check if filter is registered
        if 'strftime' in app.jinja_env.filters:
            print("✅ strftime filter is registered")
        else:
            print("❌ strftime filter is NOT registered")
        
        # Test the filter directly
        test_date_string = "2024-12-01 10:30"
        
        # Test the as_datetime filter first
        as_datetime_filter = app.jinja_env.filters['as_datetime']
        date_obj = as_datetime_filter(test_date_string)
        print(f"as_datetime result: {date_obj} (type: {type(date_obj)})")
        
        # Test the strftime filter
        strftime_filter = app.jinja_env.filters['strftime']
        formatted_date = strftime_filter(date_obj, '%d.%m.%Y %H:%M')
        print(f"strftime result: {formatted_date}")
        
        # Test the complete chain like in template
        if date_obj:
            final_result = strftime_filter(date_obj, '%d.%m.%Y %H:%M')
            print(f"Final result: {final_result}")
            
            if final_result and '01.12.2024 10:30' in final_result:
                print("✅ Filter chain works correctly!")
            else:
                print(f"❌ Filter chain failed. Expected '01.12.2024 10:30', got: {final_result}")
        else:
            print("❌ as_datetime filter failed")
        
        # Test template rendering using Flask's render_template_string
        from flask import render_template_string
        test_template = """{{ reminder.datetime | as_datetime | strftime('%d.%m.%Y %H:%M') }}"""
        
        test_reminder = {'datetime': test_date_string}
        result = render_template_string(test_template, reminder=test_reminder)
        print(f"Template render result: {result}")
        
        if '01.12.2024 10:30' in result:
            print("✅ Template rendering works correctly!")
        else:
            print(f"❌ Template rendering failed: {result}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()