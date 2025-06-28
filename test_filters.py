#!/usr/bin/env python3
"""Test strftime filter"""

import os
os.environ['FLASK_ENV'] = 'development'
os.environ['TESTING'] = '1'

print("🧪 Testing strftime filter...")

try:
    from app import app
    print("✅ App imported successfully")
    
    # Check if filter is registered
    with app.app_context():
        filters = list(app.jinja_env.filters.keys())
        print(f"Available filters: {sorted(filters)}")
        
        if 'strftime' in app.jinja_env.filters:
            print("✅ strftime filter is registered")
        else:
            print("❌ strftime filter is NOT registered")
            
        if 'as_datetime' in app.jinja_env.filters:
            print("✅ as_datetime filter is registered")
        else:
            print("❌ as_datetime filter is NOT registered")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
