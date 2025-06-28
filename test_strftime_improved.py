#!/usr/bin/env python3
"""Test the improved strftime filter"""

import os
os.environ['FLASK_ENV'] = 'development'
os.environ['TESTING'] = '1'

print("🧪 Testing improved strftime filter...")

try:
    from app import app
    from flask import render_template_string
    print("✅ App imported successfully")
    
    with app.app_context():
        # Test various scenarios
        test_cases = [
            {'datetime': '2024-12-01 10:30'},      # Valid datetime string
            {'datetime': '2024-12-01'},            # Date only
            {'datetime': None},                     # None value
            {'datetime': ''},                       # Empty string
            {'datetime': 'invalid'},                # Invalid string
        ]
        
        template = """{{ reminder.datetime | as_datetime | strftime('%d.%m.%Y %H:%M') }}"""
        
        for i, test_case in enumerate(test_cases):
            print(f"\nTest {i+1}: {test_case}")
            try:
                result = render_template_string(template, reminder=test_case)
                print(f"  Result: '{result.strip()}'")
            except Exception as e:
                print(f"  Error: {e}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
