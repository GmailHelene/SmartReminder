#!/usr/bin/env python3
"""Minimal test to check what routes are actually registered"""

import os
os.environ['FLASK_ENV'] = 'development'
os.environ['TESTING'] = '1'

print("Testing route registration step by step...")

try:
    print("1. Importing Flask...")
    from flask import Flask
    
    print("2. Creating basic app...")
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'test'
    
    print(f"   Basic app has {len(list(app.url_map.iter_rules()))} routes")
    
    print("3. Importing app module...")
    # This should register all routes
    from app import app as real_app
    
    print(f"   Real app has {len(list(real_app.url_map.iter_rules()))} routes")
    
    # Check for specific routes
    endpoints = [rule.endpoint for rule in real_app.url_map.iter_rules()]
    
    critical_routes = ['dashboard', 'noteboards', 'focus_modes', 'email_settings']
    
    for route in critical_routes:
        if route in endpoints:
            print(f"   ✅ {route}")
        else:
            print(f"   ❌ {route} - MISSING!")
    
    print("4. Success! All imports worked.")
    
except Exception as e:
    print(f"❌ Error during import: {e}")
    import traceback
    traceback.print_exc()
