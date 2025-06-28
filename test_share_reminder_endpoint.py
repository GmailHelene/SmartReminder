#!/usr/bin/env python3
"""Test script to verify the share_reminder endpoint is properly registered"""

import sys
import os
sys.path.append(os.path.abspath('.'))

try:
    from app import app
    
    print("Testing share_reminder endpoint registration...")
    
    # Get all registered routes
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            'endpoint': rule.endpoint,
            'methods': list(rule.methods),
            'rule': rule.rule
        })
    
    # Look for share_reminder endpoint  
    share_reminder_found = False
    for route in routes:
        if route['endpoint'] == 'share_reminder':
            share_reminder_found = True
            print(f"✅ Found share_reminder endpoint:")
            print(f"   Route: {route['rule']}")
            print(f"   Methods: {route['methods']}")
            break
    
    if not share_reminder_found:
        print("❌ share_reminder endpoint not found!")
        print("\nAll reminder-related endpoints:")
        for route in routes:
            if 'reminder' in route['endpoint']:
                print(f"   {route['endpoint']}: {route['rule']} {route['methods']}")
    else:
        print("✅ share_reminder endpoint successfully registered!")
    
    # Also check that the import and function definition exist
    if hasattr(app.view_functions, 'share_reminder'):
        print("✅ share_reminder function is available in view_functions")
    else:
        print("❌ share_reminder function not found in view_functions")
    
    print("\nTest completed!")
    
except Exception as e:
    print(f"❌ Error during test: {e}")
    import traceback
    traceback.print_exc()
